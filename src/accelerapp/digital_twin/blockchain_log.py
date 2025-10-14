"""
Blockchain-verifiable hardware logs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json


class BlockchainBlock:
    """Represents a block in the blockchain log."""
    
    def __init__(self, index: int, timestamp: datetime, data: Dict[str, Any], previous_hash: str):
        """
        Initialize a blockchain block.
        
        Args:
            index: Block index
            timestamp: Block timestamp
            data: Block data
            previous_hash: Hash of previous block
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate block hash."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class BlockchainLogger:
    """
    Provides blockchain-verifiable logging for hardware operations.
    Creates immutable audit trail of device state changes.
    """
    
    def __init__(self, device_id: str):
        """
        Initialize blockchain logger.
        
        Args:
            device_id: Device identifier
        """
        self.device_id = device_id
        self.chain: List[BlockchainBlock] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self) -> None:
        """Create the genesis (first) block."""
        genesis_block = BlockchainBlock(
            index=0,
            timestamp=datetime.utcnow(),
            data={"type": "genesis", "device_id": self.device_id},
            previous_hash="0",
        )
        self.chain.append(genesis_block)
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Log an event to the blockchain.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            Hash of the created block
        """
        previous_block = self.chain[-1]
        
        new_block = BlockchainBlock(
            index=len(self.chain),
            timestamp=datetime.utcnow(),
            data={
                "device_id": self.device_id,
                "event_type": event_type,
                "event_data": event_data,
            },
            previous_hash=previous_block.hash,
        )
        
        self.chain.append(new_block)
        return new_block.hash
    
    def log_state_change(self, pin: int, value: Any, state_type: str) -> str:
        """
        Log a state change event.
        
        Args:
            pin: Pin number
            value: New value
            state_type: Type of state (digital/analog)
            
        Returns:
            Block hash
        """
        return self.log_event("state_change", {
            "pin": pin,
            "value": value,
            "state_type": state_type,
        })
    
    def log_connection_event(self, connected: bool) -> str:
        """
        Log a connection event.
        
        Args:
            connected: Connection status
            
        Returns:
            Block hash
        """
        return self.log_event("connection", {
            "connected": connected,
        })
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the blockchain.
        
        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block hash
            if current_block.hash != current_block._calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_chain(self) -> List[Dict[str, Any]]:
        """
        Get the entire blockchain.
        
        Returns:
            List of block dictionaries
        """
        return [block.to_dict() for block in self.chain]
    
    def get_block(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific block by index.
        
        Args:
            index: Block index
            
        Returns:
            Block dictionary or None
        """
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
    
    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent events from the blockchain.
        
        Args:
            count: Number of recent events to retrieve
            
        Returns:
            List of recent blocks
        """
        start_index = max(1, len(self.chain) - count)  # Skip genesis block
        return [block.to_dict() for block in self.chain[start_index:]]
    
    def export_chain(self) -> str:
        """
        Export blockchain as JSON.
        
        Returns:
            JSON string of blockchain
        """
        return json.dumps(self.get_chain(), indent=2)
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """
        Get blockchain statistics.
        
        Returns:
            Statistics dictionary
        """
        event_types = {}
        for block in self.chain[1:]:  # Skip genesis
            event_type = block.data.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "device_id": self.device_id,
            "total_blocks": len(self.chain),
            "genesis_timestamp": self.chain[0].timestamp.isoformat(),
            "latest_timestamp": self.chain[-1].timestamp.isoformat(),
            "is_valid": self.verify_chain(),
            "event_types": event_types,
        }
