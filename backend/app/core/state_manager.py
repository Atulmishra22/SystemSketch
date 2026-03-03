"""
Room State Manager for In-Memory Canvas State
Handles active room state, undo/redo operations, and thread-safe access
"""
from typing import Dict, List
import asyncio
from copy import deepcopy


class RoomStateManager:
    """
    Manages in-memory state for active rooms
    - Stores current canvas shapes
    - Implements undo/redo with history stacks
    - Thread-safe with async locks
    """
    
    # Maximum history depth to prevent memory bloat
    MAX_HISTORY_DEPTH = 50
    
    def __init__(self):
        # room_id -> {"shapes": [], "history": [], "redo_stack": []}
        self.rooms: Dict[str, Dict] = {}
        # room_id -> asyncio.Lock for thread-safe operations
        self.locks: Dict[str, asyncio.Lock] = {}
    
    def _get_lock(self, room_id: str) -> asyncio.Lock:
        """Get or create lock for a room"""
        if room_id not in self.locks:
            self.locks[room_id] = asyncio.Lock()
        return self.locks[room_id]
    
    def _initialize_room(self, room_id: str) -> None:
        """Initialize room state if it doesn't exist"""
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                "shapes": [],
                "history": [],
                "redo_stack": []
            }
    
    async def get_state(self, room_id: str) -> List[Dict]:
        """Get current shapes array for a room"""
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            return deepcopy(self.rooms[room_id]["shapes"])
    
    async def set_state(self, room_id: str, shapes: List[Dict]) -> None:
        """
        Replace entire state (used for initial load from database)
        Does NOT add to history (for loading persisted state)
        """
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            self.rooms[room_id]["shapes"] = deepcopy(shapes)
    
    async def update_state(self, room_id: str, shapes: List[Dict], add_to_history: bool = True) -> None:
        """
        Update the entire shapes array and optionally save to history
        """
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            
            if add_to_history:
                # Save current state to history before updating
                current_state = deepcopy(self.rooms[room_id]["shapes"])
                self.rooms[room_id]["history"].append(current_state)
                
                # Maintain history depth limit
                if len(self.rooms[room_id]["history"]) > self.MAX_HISTORY_DEPTH:
                    self.rooms[room_id]["history"].pop(0)
                
                # Clear redo stack when new action is performed
                self.rooms[room_id]["redo_stack"] = []
            
            self.rooms[room_id]["shapes"] = deepcopy(shapes)
    
    async def add_shape(self, room_id: str, shape: Dict) -> None:
        """Add a single shape to the canvas"""
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            
            # Save to history
            current_state = deepcopy(self.rooms[room_id]["shapes"])
            self.rooms[room_id]["history"].append(current_state)
            
            # Maintain history depth
            if len(self.rooms[room_id]["history"]) > self.MAX_HISTORY_DEPTH:
                self.rooms[room_id]["history"].pop(0)
            
            # Clear redo stack
            self.rooms[room_id]["redo_stack"] = []
            
            # Add shape
            self.rooms[room_id]["shapes"].append(shape)

    async def move_shape(self, room_id: str, shape_id: str, updates: Dict) -> bool:
        """
        Update position (and any other fields) of an existing shape by id.
        Saves to history so the move can be undone.
        Returns True if the shape was found and updated.
        """
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            shapes = self.rooms[room_id]["shapes"]
            for i, s in enumerate(shapes):
                if s.get("id") == shape_id:
                    # Snapshot before mutating
                    current_state = deepcopy(shapes)
                    self.rooms[room_id]["history"].append(current_state)
                    if len(self.rooms[room_id]["history"]) > self.MAX_HISTORY_DEPTH:
                        self.rooms[room_id]["history"].pop(0)
                    self.rooms[room_id]["redo_stack"] = []
                    # Merge updates into the existing shape dict
                    shapes[i] = {**s, **updates}
                    return True
            return False
    
    async def clear_state(self, room_id: str) -> None:
        """Clear all shapes (save to history)"""
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            
            # Save to history
            current_state = deepcopy(self.rooms[room_id]["shapes"])
            if current_state:  # Only save if there was something to clear
                self.rooms[room_id]["history"].append(current_state)
            
            # Clear redo stack
            self.rooms[room_id]["redo_stack"] = []
            
            # Clear shapes
            self.rooms[room_id]["shapes"] = []
    
    async def undo(self, room_id: str) -> List[Dict]:
        """
        Undo last action (restore previous state from history)
        Returns the new current state
        """
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            
            if not self.rooms[room_id]["history"]:
                # Nothing to undo
                return deepcopy(self.rooms[room_id]["shapes"])
            
            # Save current state to redo stack
            current_state = deepcopy(self.rooms[room_id]["shapes"])
            self.rooms[room_id]["redo_stack"].append(current_state)
            
            # Restore previous state from history
            previous_state = self.rooms[room_id]["history"].pop()
            self.rooms[room_id]["shapes"] = previous_state
            
            return deepcopy(self.rooms[room_id]["shapes"])
    
    async def redo(self, room_id: str) -> List[Dict]:
        """
        Redo last undone action
        Returns the new current state
        """
        async with self._get_lock(room_id):
            self._initialize_room(room_id)
            
            if not self.rooms[room_id]["redo_stack"]:
                # Nothing to redo
                return deepcopy(self.rooms[room_id]["shapes"])
            
            # Save current state to history
            current_state = deepcopy(self.rooms[room_id]["shapes"])
            self.rooms[room_id]["history"].append(current_state)
            
            # Restore from redo stack
            redo_state = self.rooms[room_id]["redo_stack"].pop()
            self.rooms[room_id]["shapes"] = redo_state
            
            return deepcopy(self.rooms[room_id]["shapes"])
    
    async def delete_room(self, room_id: str) -> None:
        """Delete room state (cleanup)"""
        async with self._get_lock(room_id):
            if room_id in self.rooms:
                del self.rooms[room_id]
            if room_id in self.locks:
                del self.locks[room_id]
    
    def get_room_count(self) -> int:
        """Get number of active rooms in memory"""
        return len(self.rooms)


# Global singleton instance
room_state_manager = RoomStateManager()
