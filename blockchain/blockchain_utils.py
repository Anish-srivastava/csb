"""Utilities for blockchain integration with detector and logger."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from blockchain.blockchain import Blockchain, Block

# Initialize global blockchain instance
_blockchain: Blockchain = None
BLOCKCHAIN_PERSISTENCE_FILE = Path(__file__).parent.parent / "blockchain_data.json"


def initialize_blockchain(difficulty: int = 2) -> Blockchain:
    """
    Initialize global blockchain instance.
    Load from file if exists, otherwise create new.
    
    Args:
        difficulty: Proof of work difficulty level
    
    Returns:
        Blockchain instance
    """
    global _blockchain
    
    # Try to load from file first
    if BLOCKCHAIN_PERSISTENCE_FILE.exists():
        try:
            _blockchain = load_blockchain_from_file()
            print(f"✅ Blockchain loaded from {BLOCKCHAIN_PERSISTENCE_FILE}")
            return _blockchain
        except Exception as e:
            print(f"⚠️ Could not load blockchain from file: {e}")
    
    # Create new blockchain if file doesn't exist
    _blockchain = Blockchain(difficulty=difficulty)
    print(f"✨ New blockchain created")
    return _blockchain


def save_blockchain_to_file() -> None:
    """Save blockchain to JSON file for persistence."""
    try:
        if _blockchain is None:
            return
        
        blockchain_data = {
            "difficulty": _blockchain.difficulty,
            "chain": []
        }
        
        for block in _blockchain.chain:
            blockchain_data["chain"].append({
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.hash
            })
        
        BLOCKCHAIN_PERSISTENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(BLOCKCHAIN_PERSISTENCE_FILE, 'w') as f:
            json.dump(blockchain_data, f, indent=2)
        
        print(f"💾 Blockchain saved ({len(_blockchain.chain)} blocks)")
    except Exception as e:
        print(f"❌ Error saving blockchain: {e}")


def load_blockchain_from_file() -> Blockchain:
    """Load blockchain from JSON file."""
    with open(BLOCKCHAIN_PERSISTENCE_FILE, 'r') as f:
        blockchain_data = json.load(f)
    
    blockchain = Blockchain(difficulty=blockchain_data.get("difficulty", 2))
    blockchain.chain = []
    
    # Reconstruct blockchain from saved data
    for block_data in blockchain_data["chain"]:
        block = Block(
            index=block_data["index"],
            timestamp=block_data["timestamp"],
            data=block_data["data"],
            previous_hash=block_data["previous_hash"]
        )
        block.nonce = block_data["nonce"]
        block.hash = block_data["hash"]
        blockchain.chain.append(block)
    
    return blockchain


def get_blockchain() -> Blockchain:
    """Get the global blockchain instance."""
    global _blockchain
    if _blockchain is None:
        _blockchain = initialize_blockchain()
    return _blockchain


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hex string of file hash
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return "ERROR"


def log_suspicious_activity(file_path: str, activity_type: str, 
                            severity: str, details: str) -> None:
    """
    Log suspicious activity to blockchain.
    
    Args:
        file_path: Path of affected file
        activity_type: Type of activity (rapid_changes, extension_change, etc.)
        severity: HIGH, MEDIUM, LOW
        details: Additional details
    """
    blockchain = get_blockchain()
    file_hash = calculate_file_hash(Path(file_path)) if Path(file_path).exists() else "FILE_MISSING"
    
    blockchain.add_attack_log(
        event_type=f"SUSPICIOUS_{activity_type.upper()}",
        file_path=file_path,
        file_hash=file_hash,
        severity=severity,
        details=details
    )
    
    save_blockchain_to_file()
    print(f"📝 Blockchain Log Added: {activity_type} on {file_path}")


def log_file_encrypted(file_path: str, encryption_method: str, details: str = "") -> None:
    """
    Log file encryption event.
    
    Args:
        file_path: Path of encrypted file
        encryption_method: Method used (Fernet, AES, etc.)
        details: Additional details
    """
    blockchain = get_blockchain()
    file_hash = calculate_file_hash(Path(file_path)) if Path(file_path).exists() else "FILE_MODIFIED"
    
    blockchain.add_attack_log(
        event_type="FILE_ENCRYPTED",
        file_path=file_path,
        file_hash=file_hash,
        severity="HIGH",
        details=f"Encryption method: {encryption_method}. {details}"
    )
    
    save_blockchain_to_file()
    print(f"🔐 Blockchain Log: FILE_ENCRYPTED - {file_path}")


def log_file_recovered(file_path: str, recovery_method: str, success: bool, 
                       details: str = "") -> None:
    """
    Log file recovery attempt.
    
    Args:
        file_path: Path of recovered file
        recovery_method: Recovery method (backup_restore, decryption, etc.)
        success: Whether recovery succeeded
        details: Additional details
    """
    blockchain = get_blockchain()
    file_hash = calculate_file_hash(Path(file_path)) if Path(file_path).exists() else "RECOVERY_FAILED"
    
    blockchain.add_recovery_log(
        file_path=file_path,
        file_hash=file_hash,
        recovery_method=recovery_method,
        success=success,
        details=details
    )
    
    save_blockchain_to_file()
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"🔄 Blockchain Log: FILE_RECOVERY {status} - {file_path}")


def export_blockchain_report(output_path: Path) -> None:
    """
    Export blockchain as JSON report.
    
    Args:
        output_path: Where to save the report
    """
    blockchain = get_blockchain()
    stats = blockchain.get_statistics()
    
    report = {
        "timestamp": str(datetime.now().isoformat()),
        "output_file": str(output_path),
        "statistics": stats,
        "chain": json.loads(blockchain.get_chain_as_json())
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Blockchain report saved to: {output_path}")


def print_blockchain_summary() -> None:
    """Print summary of blockchain to console."""
    blockchain = get_blockchain()
    stats = blockchain.get_statistics()
    
    print("\n" + "="*60)
    print("🔗 BLOCKCHAIN SUMMARY 🔗")
    print("="*60)
    print(f"Total Blocks: {stats['total_blocks']}")
    print(f"Total Events: {stats['total_events']}")
    print(f"Chain Valid (No Tampering): {stats['chain_valid']}")
    print("\nEvent Breakdown:")
    for event_type, count in stats['event_breakdown'].items():
        print(f"  - {event_type}: {count}")
    print("\nSeverity Distribution:")
    for severity, count in stats['severity_distribution'].items():
        print(f"  - {severity}: {count}")
    print("="*60 + "\n")
