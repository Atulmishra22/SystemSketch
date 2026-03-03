"""
WebSocket Connection Manager for Real-time Collaboration
Handles WebSocket connections, user identification, and message broadcasting
"""
from fastapi import WebSocket
from typing import Dict, List
import random
import uuid


class ConnectionManager:
    """
    Manages WebSocket connections for collaborative rooms
    - Tracks active connections per room
    - Assigns unique colors to users
    - Broadcasts messages to room participants
    """
    
    # Distinct color palette — kept well away from brand brick #C0431F
    USER_COLORS = [
        "#2563EB",  # Blue
        "#16A34A",  # Green
        "#7C3AED",  # Violet
        "#0891B2",  # Cyan
        "#D97706",  # Amber
        "#DB2777",  # Pink
        "#059669",  # Emerald
        "#9333EA",  # Purple
        "#EA580C",  # Orange (distinct from brick)
        "#0284C7",  # Sky
        "#65A30D",  # Lime
        "#BE185D",  # Rose
    ]
    
    def __init__(self):
        # room_id -> list of (websocket, user_id, username, color)
        self.active_connections: Dict[str, List[tuple]] = {}
        # connection_id -> color (to maintain consistency)
        self.user_colors: Dict[str, str] = {}
        # room_id -> set of used colors
        self.room_colors: Dict[str, set] = {}
    
    def _assign_color(self, room_id: str) -> str:
        """Assign a unique color for a user in a room"""
        if room_id not in self.room_colors:
            self.room_colors[room_id] = set()
        
        used_colors = self.room_colors[room_id]
        available_colors = [c for c in self.USER_COLORS if c not in used_colors]
        
        if available_colors:
            color = random.choice(available_colors)
        else:
            # All colors used, recycle with randomization
            color = random.choice(self.USER_COLORS)
        
        self.room_colors[room_id].add(color)
        return color
    
    async def connect(
        self,
        room_id: str,
        websocket: WebSocket,
        username: str = None,
        can_edit: bool = False
    ) -> tuple[str, str]:
        """
        Accept a WebSocket connection and assign user ID and color
        Returns: (user_id, color)
        """
        await websocket.accept()
        
        # Generate unique user ID for this connection
        user_id = str(uuid.uuid4())[:8]  # Short ID for display
        
        # Assign color
        color = self._assign_color(room_id)
        self.user_colors[user_id] = color
        
        # Determine username
        if not username:
            username = f"User-{user_id}"
        
        # Add to active connections (5-tuple: ws, user_id, username, color, can_edit)
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append(
            (websocket, user_id, username, color, can_edit)
        )
        
        return user_id, color
    
    def disconnect(self, room_id: str, websocket: WebSocket) -> tuple:
        """
        Remove a WebSocket connection
        Returns: (user_id, color) if found, else (None, None)
        """
        if room_id in self.active_connections:
            for conn in self.active_connections[room_id]:
                ws, user_id, username, color, can_edit = conn
                if ws == websocket:
                    self.active_connections[room_id].remove(conn)
                    
                    # Clean up color assignment
                    if room_id in self.room_colors:
                        self.room_colors[room_id].discard(color)
                    
                    # Clean up user color mapping
                    if user_id in self.user_colors:
                        del self.user_colors[user_id]
                    
                    # Clean up empty room
                    if not self.active_connections[room_id]:
                        del self.active_connections[room_id]
                        if room_id in self.room_colors:
                            del self.room_colors[room_id]
                        # Release the orphaned asyncio lock in state_manager so it can be GC'd
                        from app.core.state_manager import room_state_manager
                        if room_id in room_state_manager.locks:
                            del room_state_manager.locks[room_id]
                    
                    return user_id, color
        
        return None, None
    
    async def broadcast(
        self,
        room_id: str,
        message: str,
        exclude_ws: WebSocket = None
    ) -> None:
        """
        Broadcast a message to all connections in a room
        Optionally exclude the sender websocket
        """
        if room_id not in self.active_connections:
            return
        
        # Create a copy to avoid modification during iteration
        connections = self.active_connections[room_id].copy()
        
        for websocket, user_id, username, color, can_edit in connections:
            if websocket != exclude_ws:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    # Connection might be closed, will be cleaned up on next message
                    print(f"Error broadcasting to {user_id}: {e}")
    
    async def send_personal(
        self,
        room_id: str,
        websocket: WebSocket,
        message: str
    ) -> None:
        """Send a message to a specific websocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    def get_room_users(self, room_id: str) -> List[Dict]:
        """Get list of users in a room"""
        if room_id not in self.active_connections:
            return []
        
        return [
            {
                "userId": user_id,
                "username": username,
                "color": color,
                "canEdit": can_edit,
            }
            for _, user_id, username, color, can_edit in self.active_connections[room_id]
        ]
    
    def get_connection_count(self, room_id: str) -> int:
        """Get number of active connections in a room"""
        if room_id not in self.active_connections:
            return 0
        return len(self.active_connections[room_id])


# Global singleton instance
connection_manager = ConnectionManager()
