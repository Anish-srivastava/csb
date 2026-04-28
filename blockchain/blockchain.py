"""Blockchain implementation for immutable ransomware attack logs."""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class Block:
    """Single block in the blockchain."""
    
    def __init__(self, index: int, data: Dict[str, Any], previous_hash: str):
        """
        Initialize a block.
        
        Args:
            index: Position of block in chain
            data: Event data to store (attack info, file hash, etc.)
            previous_hash: Hash of previous block for chain integrity
        """
        self.index = index
        self.timestamp = datetime.now().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this block."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> None:
        """
        Proof of Work: Find nonce that creates hash with leading zeros.
        
        Args:
            difficulty: Number of leading zeros required
        """
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class Blockchain:
    """Immutable blockchain for ransomware attack records."""
    
    def __init__(self, difficulty: int = 2):
        """
        Initialize blockchain.
        
        Args:
            difficulty: Number of leading zeros for proof of work
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block (genesis block)."""
        genesis_data = {
            "event": "GENESIS",
            "description": "Blockchain initialized for ransomware detection",
            "source": "HybridRansomware"
        }
        genesis_block = Block(0, genesis_data, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the last block in the chain."""
        return self.chain[-1]
    
    def add_attack_log(self, event_type: str, file_path: str, file_hash: str, 
                       severity: str, details: str, mined: bool = True) -> Block:
        """
        Log a ransomware attack event to blockchain.
        
        Args:
            event_type: Type of event (FILE_ENCRYPTED, SUSPICIOUS_ACTIVITY, etc.)
            file_path: Path of affected file
            file_hash: SHA-256 hash of file
            severity: HIGH, MEDIUM, LOW
            details: Additional details about the event
            mined: Whether to mine the block (proof of work)
        
        Returns:
            The newly added block
        """
        data = {
            "event_type": event_type,
            "file_path": file_path,
            "file_hash": file_hash,
            "severity": severity,
            "details": details,
            "status": "LOGGED"
        }
        
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), data, latest_block.hash)
        
        if mined:
            new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return new_block
    
    def add_recovery_log(self, file_path: str, file_hash: str, 
                        recovery_method: str, success: bool, 
                        details: str, mined: bool = True) -> Block:
        """
        Log file recovery attempt.
        
        Args:
            file_path: Path of recovered file
            file_hash: SHA-256 hash of recovered file
            recovery_method: Method used (backup, decrypt, etc.)
            success: Whether recovery succeeded
            details: Additional info
            mined: Whether to mine the block
        
        Returns:
            The newly added block
        """
        data = {
            "event_type": "FILE_RECOVERY",
            "file_path": file_path,
            "file_hash": file_hash,
            "recovery_method": recovery_method,
            "success": success,
            "details": details,
            "status": "RECOVERED" if success else "RECOVERY_FAILED"
        }
        
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), data, latest_block.hash)
        
        if mined:
            new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return new_block
    
    def verify_chain_integrity(self) -> bool:
        """
        Verify that blockchain hasn't been tampered with.
        
        Returns:
            True if chain is valid, False if tampered
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Block {i} hash is invalid!")
                return False
            
            # Verify chain link
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block {i} previous hash doesn't match!")
                return False
        
        print("✅ Blockchain integrity verified - NO tampering detected!")
        return True
    
    def get_chain_as_json(self) -> str:
        """Export entire blockchain as JSON."""
        chain_data = [block.to_dict() for block in self.chain]
        return json.dumps(chain_data, indent=2)
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Get block by its index."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def search_by_file_hash(self, file_hash: str) -> List[Block]:
        """Find all blocks related to a specific file."""
        results = []
        for block in self.chain:
            if block.data.get("file_hash") == file_hash:
                results.append(block)
        return results
    
    def search_by_event_type(self, event_type: str) -> List[Block]:
        """Find all blocks of a specific event type."""
        results = []
        for block in self.chain:
            if block.data.get("event_type") == event_type:
                results.append(block)
        return results
    
    def get_chain_length(self) -> int:
        """Get total number of blocks."""
        return len(self.chain)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get blockchain statistics."""
        total_blocks = len(self.chain)
        total_events = sum(1 for b in self.chain if b.data.get("event_type"))
        
        event_counts = {}
        for block in self.chain:
            event_type = block.data.get("event_type", "UNKNOWN")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for block in self.chain:
            severity = block.data.get("severity")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            "total_blocks": total_blocks,
            "total_events": total_events,
            "event_breakdown": event_counts,
            "severity_distribution": severity_counts,
            "chain_valid": self.verify_chain_integrity()
        }
