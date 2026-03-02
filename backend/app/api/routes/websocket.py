"""
WebSocket API Endpoint for Real-time Collaboration
Handles bi-directional communication for canvas synchronization
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json

from app.core.websocket_manager import connection_manager
from app.core.state_manager import room_state_manager
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.permission import PermissionLevel
from app.services.auth_service import decode_access_token
from app.services.permission_service import PermissionService
from app.schemas.websocket import (
    UserJoined,
    UserLeft,
    SyncState,
    ErrorMessage
)


router = APIRouter()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: Optional[str] = Query(default=None),
    token: Optional[str] = Query(default=None)
):
    """
    WebSocket endpoint for real-time room collaboration
    
    Authentication & Authorization:
    - Optional JWT token via query parameter
    - Falls back to anonymous username if no token provided
    - Checks room permissions: VIEWER (read-only), EDITOR (can edit), OWNER (full control)
    - Anonymous users can access public rooms as viewers
    
    Flow:
    1. Validate optional JWT token and get user info
    2. Check room access permissions
    3. Accept connection and assign user ID/color
    4. Send current room state to new user
    5. Broadcast user joined to others
    6. Handle incoming messages with permission checks
    7. Broadcast updates to all room participants
    8. Handle disconnection gracefully
    """
    
    # Try to authenticate with JWT token
    authenticated_username = None
    user_id_from_token = None
    user_permission = None
    
    if token:
        token_data = decode_access_token(token)
        if token_data:
            user_id_from_token = token_data.user_id
            # Fetch user from database to get actual username and check permissions
            async with AsyncSessionLocal() as session:
                user = await session.get(User, token_data.user_id)
                if user:
                    authenticated_username = user.username
                    # Check user's permission for this room
                    user_permission = await PermissionService.get_user_permission(
                        db=session,
                        user_id=user.id,
                        room_id=room_id
                    )
    
    # If no authenticated permission, check if room is public (anonymous access)
    if not user_permission and not user_id_from_token:
        async with AsyncSessionLocal() as session:
            from app.models.room import Room
            room = await session.get(Room, room_id)
            if room and room.permission_level == "public":
                user_permission = PermissionLevel.VIEWER  # Anonymous users are viewers
    
    # Reject connection if no access
    if not user_permission:
        await websocket.accept()
        error_message = ErrorMessage(
            action="error",
            message="Access denied: You don't have permission to access this room",
            code="FORBIDDEN"
        )
        await websocket.send_text(error_message.model_dump_json())
        await websocket.close(code=1008, reason="Forbidden")
        return
    
    # Determine if user can edit (EDITOR or OWNER permissions)
    can_edit = user_permission in [PermissionLevel.EDITOR, PermissionLevel.OWNER]
    
    # Use authenticated username, or provided username, or generate anonymous
    final_username = authenticated_username or username or None
    
    # Accept connection and get user info
    user_id, color = await connection_manager.connect(room_id, websocket, final_username)
    
    try:
        # Send current room state to newly connected user
        current_shapes = await room_state_manager.get_state(room_id)
        sync_message = SyncState(
            action="sync_state",
            shapes=current_shapes
        )
        await connection_manager.send_personal(
            room_id,
            websocket,
            sync_message.model_dump_json()
        )
        
        # Broadcast user joined to others in the room
        join_message = UserJoined(
            action="user_joined",
            userId=user_id,
            username=username,
            color=color
        )
        await connection_manager.broadcast(
            room_id,
            join_message.model_dump_json(),
            exclude_ws=websocket  # Don't send to the new user
        )
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            
            if action == "draw":
                # Check if user has edit permission
                if not can_edit:
                    error_message = ErrorMessage(
                        action="error",
                        message="You don't have permission to edit this room (view-only access)",
                        code="PERMISSION_DENIED"
                    )
                    await connection_manager.send_personal(
                        room_id,
                        websocket,
                        error_message.model_dump_json()
                    )
                    continue
                
                # Add shape to room state
                shape = message.get("shape")
                if shape:
                    await room_state_manager.add_shape(room_id, shape)
                    # Broadcast to all users in room
                    await connection_manager.broadcast(
                        room_id,
                        data,
                        exclude_ws=websocket
                    )
            
            elif action == "cursor":
                # Broadcast cursor position (no permission check, everyone can show cursor)
                await connection_manager.broadcast(
                    room_id,
                    data,
                    exclude_ws=websocket
                )
            
            elif action == "clear":
                # Check if user has edit permission
                if not can_edit:
                    error_message = ErrorMessage(
                        action="error",
                        message="You don't have permission to clear this room (view-only access)",
                        code="PERMISSION_DENIED"
                    )
                    await connection_manager.send_personal(
                        room_id,
                        websocket,
                        error_message.model_dump_json()
                    )
                    continue
                
                # Clear canvas for everyone
                await room_state_manager.clear_state(room_id)
                await connection_manager.broadcast(
                    room_id,
                    data
                )
            
            elif action == "undo":
                # Check if user has edit permission
                if not can_edit:
                    error_message = ErrorMessage(
                        action="error",
                        message="You don't have permission to undo in this room (view-only access)",
                        code="PERMISSION_DENIED"
                    )
                    await connection_manager.send_personal(
                        room_id,
                        websocket,
                        error_message.model_dump_json()
                    )
                    continue
                
                # Undo last action
                new_state = await room_state_manager.undo(room_id)
                sync_message = SyncState(
                    action="sync_state",
                    shapes=new_state
                )
                # Broadcast full state to all users
                await connection_manager.broadcast(
                    room_id,
                    sync_message.model_dump_json()
                )
            
            elif action == "redo":
                # Check if user has edit permission
                if not can_edit:
                    error_message = ErrorMessage(
                        action="error",
                        message="You don't have permission to redo in this room (view-only access)",
                        code="PERMISSION_DENIED"
                    )
                    await connection_manager.send_personal(
                        room_id,
                        websocket,
                        error_message.model_dump_json()
                    )
                    continue
                
                # Redo last undone action
                new_state = await room_state_manager.redo(room_id)
                sync_message = SyncState(
                    action="sync_state",
                    shapes=new_state
                )
                # Broadcast full state to all users
                await connection_manager.broadcast(
                    room_id,
                    sync_message.model_dump_json()
                )
            
            else:
                # Unknown action - send error
                error_message = ErrorMessage(
                    action="error",
                    message=f"Unknown action: {action}",
                    code="INVALID_ACTION"
                )
                await connection_manager.send_personal(
                    room_id,
                    websocket,
                    error_message.model_dump_json()
                )
    
    except WebSocketDisconnect:
        # Client disconnected
        user_id, color = connection_manager.disconnect(room_id, websocket)
        
        if user_id:
            # Broadcast user left to remaining users
            leave_message = UserLeft(
                action="user_left",
                userId=user_id
            )
            await connection_manager.broadcast(
                room_id,
                leave_message.model_dump_json()
            )
    
    except Exception as e:
        # Unexpected error - log and disconnect
        print(f"WebSocket error in room {room_id}: {e}")
        connection_manager.disconnect(room_id, websocket)
        
        # Try to send error message to client
        try:
            error_message = ErrorMessage(
                action="error",
                message="Internal server error",
                code="SERVER_ERROR"
            )
            await websocket.send_text(error_message.model_dump_json())
        except:
            pass  # Connection already closed
