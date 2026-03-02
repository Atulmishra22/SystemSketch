"""
Permission Service Layer
Business logic for room access control and permission management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from fastapi import HTTPException, status

from app.models.permission import RoomPermission, PermissionLevel
from app.models.room import Room
from app.models.user import User


class PermissionService:
    """Service for managing room permissions"""
    
    @staticmethod
    async def check_permission(
        db: AsyncSession,
        user_id: str,
        room_id: str,
        required_permission: PermissionLevel = PermissionLevel.VIEWER
    ) -> bool:
        """
        Check if user has required permission level for a room
        
        Args:
            db: Database session
            user_id: User ID to check
            room_id: Room ID to check access for
            required_permission: Minimum permission level required
            
        Returns:
            True if user has access, False otherwise
        """
        # Check if user is the room owner
        room = await db.get(Room, room_id)
        if not room:
            return False
            
        if room.creator_id == user_id:
            return True  # Owner has all permissions
            
        # Check explicit permissions
        stmt = select(RoomPermission).where(
            and_(
                RoomPermission.user_id == user_id,
                RoomPermission.room_id == room_id
            )
        )
        result = await db.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if not permission:
            # Check if room is public
            return room.permission_level == "public"
            
        # Check permission hierarchy: OWNER > EDITOR > VIEWER
        permission_hierarchy = {
            PermissionLevel.OWNER: 3,
            PermissionLevel.EDITOR: 2,
            PermissionLevel.VIEWER: 1
        }
        
        return permission_hierarchy.get(permission.permission, 0) >= permission_hierarchy.get(required_permission, 0)
    
    @staticmethod
    async def get_user_permission(
        db: AsyncSession,
        user_id: str,
        room_id: str
    ) -> Optional[PermissionLevel]:
        """
        Get user's permission level for a room
        
        Returns:
            PermissionLevel if user has access, None otherwise
        """
        # Check if user is the room owner
        room = await db.get(Room, room_id)
        if not room:
            return None
            
        if room.creator_id == user_id:
            return PermissionLevel.OWNER
            
        # Check explicit permissions
        stmt = select(RoomPermission).where(
            and_(
                RoomPermission.user_id == user_id,
                RoomPermission.room_id == room_id
            )
        )
        result = await db.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if permission:
            return permission.permission
            
        # Check if room is public (viewer access)
        if room.permission_level == "public":
            return PermissionLevel.VIEWER
            
        return None
    
    @staticmethod
    async def grant_permission(
        db: AsyncSession,
        granter_id: str,
        user_id: str,
        room_id: str,
        permission: PermissionLevel
    ) -> RoomPermission:
        """
        Grant or update permission for a user to access a room
        
        Args:
            db: Database session
            granter_id: User ID granting the permission
            user_id: User ID to grant permission to
            room_id: Room ID
            permission: Permission level to grant
            
        Returns:
            RoomPermission object
            
        Raises:
            HTTPException if granter doesn't have permission or user doesn't exist
        """
        # Verify granter has OWNER permission
        room = await db.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
            
        if room.creator_id != granter_id:
            # Check if granter has OWNER permission
            granter_perm = await PermissionService.get_user_permission(db, granter_id, room_id)
            if granter_perm != PermissionLevel.OWNER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only room owners can grant permissions"
                )
        
        # Verify target user exists
        target_user = await db.get(User, user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if permission already exists
        stmt = select(RoomPermission).where(
            and_(
                RoomPermission.user_id == user_id,
                RoomPermission.room_id == room_id
            )
        )
        result = await db.execute(stmt)
        existing_perm = result.scalar_one_or_none()
        
        if existing_perm:
            # Update existing permission
            existing_perm.permission = permission
            existing_perm.granted_by = granter_id
            await db.commit()
            await db.refresh(existing_perm)
            return existing_perm
        else:
            # Create new permission
            new_perm = RoomPermission(
                user_id=user_id,
                room_id=room_id,
                permission=permission,
                granted_by=granter_id
            )
            db.add(new_perm)
            await db.commit()
            await db.refresh(new_perm)
            return new_perm
    
    @staticmethod
    async def revoke_permission(
        db: AsyncSession,
        revoker_id: str,
        user_id: str,
        room_id: str
    ) -> bool:
        """
        Revoke user's permission to access a room
        
        Returns:
            True if permission was revoked, False if no permission existed
        """
        # Verify revoker has OWNER permission
        room = await db.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
            
        if room.creator_id != revoker_id:
            # Check if revoker has OWNER permission
            revoker_perm = await PermissionService.get_user_permission(db, revoker_id, room_id)
            if revoker_perm != PermissionLevel.OWNER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only room owners can revoke permissions"
                )
        
        # Find and delete permission
        stmt = select(RoomPermission).where(
            and_(
                RoomPermission.user_id == user_id,
                RoomPermission.room_id == room_id
            )
        )
        result = await db.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if permission:
            await db.delete(permission)
            await db.commit()
            return True
            
        return False
    
    @staticmethod
    async def list_room_permissions(
        db: AsyncSession,
        room_id: str,
        requester_id: str
    ) -> List[RoomPermission]:
        """
        List all permissions for a room
        Only accessible by room owner
        """
        # Verify requester has OWNER permission
        room = await db.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
            
        if room.creator_id != requester_id:
            requester_perm = await PermissionService.get_user_permission(db, requester_id, room_id)
            if requester_perm != PermissionLevel.OWNER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only room owners can view all permissions"
                )
        
        stmt = select(RoomPermission).where(RoomPermission.room_id == room_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_accessible_rooms(
        db: AsyncSession,
        user_id: str
    ) -> List[Room]:
        """
        Get all rooms accessible by a user (owned + shared)
        """
        # Get rooms where user is creator
        stmt_owned = select(Room).where(Room.creator_id == user_id)
        result_owned = await db.execute(stmt_owned)
        owned_rooms = list(result_owned.scalars().all())
        
        # Get rooms where user has explicit permissions
        stmt_perms = select(Room).join(
            RoomPermission,
            Room.id == RoomPermission.room_id
        ).where(RoomPermission.user_id == user_id)
        result_perms = await db.execute(stmt_perms)
        shared_rooms = list(result_perms.scalars().all())
        
        # Combine and deduplicate
        all_rooms = {room.id: room for room in owned_rooms + shared_rooms}
        return list(all_rooms.values())
