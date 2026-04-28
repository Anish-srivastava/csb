"""Backup verification system using blockchain for data integrity."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class BackupSnapshot:
    """Represents a backup snapshot."""
    backup_id: str
    backup_time: str
    location: str
    file_hash: str
    file_size: int
    file_count: int
    encryption_method: str
    backup_status: str  # SUCCESSFUL, CORRUPTED, INCOMPLETE
    integrity_verified: bool
    verification_hash: Optional[str] = None
    timestamp_verified: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BackupIntegrityVerifier:
    """Verify backup integrity using blockchain hashes."""
    
    def __init__(self):
        """Initialize backup verifier."""
        self.backups: Dict[str, BackupSnapshot] = {}
        self.blockchain_refs: Dict[str, str] = {}  # backup_id -> blockchain_hash
        self.verification_log: List[Dict[str, Any]] = []
        self.total_backups = 0
        self.successful_backups = 0
        self.failed_verifications = 0
    
    def create_backup_snapshot(self, location: str, file_hash: str, file_size: int,
                              file_count: int, encryption_method: str = "Fernet") -> BackupSnapshot:
        """
        Create a backup snapshot record.
        
        Args:
            location: Backup location path
            file_hash: SHA-256 hash of backup file
            file_size: Size of backup in bytes
            file_count: Number of files in backup
            encryption_method: Encryption used
        
        Returns:
            BackupSnapshot object
        """
        backup_id = f"BKP_{hashlib.sha256(f'{location}_{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        snapshot = BackupSnapshot(
            backup_id=backup_id,
            backup_time=datetime.now().isoformat(),
            location=location,
            file_hash=file_hash,
            file_size=file_size,
            file_count=file_count,
            encryption_method=encryption_method,
            backup_status="SUCCESSFUL",
            integrity_verified=False,
            notes=f"Backup created at {location}"
        )
        
        self.backups[backup_id] = snapshot
        self.total_backups += 1
        self.successful_backups += 1
        
        return snapshot
    
    def register_backup_on_blockchain(self, backup_id: str, blockchain_hash: str) -> bool:
        """
        Register backup hash on blockchain.
        
        Args:
            backup_id: Backup ID
            blockchain_hash: Hash from blockchain
        
        Returns:
            True if registered
        """
        if backup_id in self.backups:
            self.blockchain_refs[backup_id] = blockchain_hash
            backup = self.backups[backup_id]
            backup.verification_hash = blockchain_hash
            
            print(f"✅ Backup {backup_id} registered on blockchain")
            print(f"   Blockchain Hash: {blockchain_hash[:32]}...")
            
            return True
        return False
    
    def verify_backup_integrity(self, backup_id: str, current_file_hash: str) -> Dict[str, Any]:
        """
        Verify backup hasn't been corrupted or modified.
        
        Args:
            backup_id: ID of backup to verify
            current_file_hash: Current hash of backup file
        
        Returns:
            Verification result
        """
        if backup_id not in self.backups:
            return {"status": "FAILED", "reason": "Backup not found"}
        
        backup = self.backups[backup_id]
        
        # Check if hash matches
        hash_match = backup.file_hash == current_file_hash
        
        # Check if blockchain reference exists
        blockchain_verified = backup_id in self.blockchain_refs
        
        verification_result = {
            "backup_id": backup_id,
            "verification_time": datetime.now().isoformat(),
            "original_hash": backup.file_hash[:32] + "...",
            "current_hash": current_file_hash[:32] + "...",
            "hash_match": hash_match,
            "blockchain_registered": blockchain_verified,
            "status": "VERIFIED" if (hash_match and blockchain_verified) else "CORRUPTED",
            "integrity_score": 100 if (hash_match and blockchain_verified) else 0,
            "can_recover": hash_match  # Can recover if hash is valid
        }
        
        # Update backup status
        if verification_result["status"] == "VERIFIED":
            backup.integrity_verified = True
            backup.timestamp_verified = datetime.now().isoformat()
            print(f"✅ Backup integrity verified: {backup_id}")
        else:
            backup.backup_status = "CORRUPTED"
            self.failed_verifications += 1
            print(f"❌ Backup integrity check FAILED: {backup_id}")
            print(f"   Expected: {backup.file_hash}")
            print(f"   Got:      {current_file_hash}")
        
        # Log verification
        self.verification_log.append(verification_result)
        
        return verification_result
    
    def verify_batch_backups(self, backup_hashes: Dict[str, str]) -> Dict[str, Any]:
        """
        Verify multiple backups at once.
        
        Args:
            backup_hashes: Dict of backup_id -> current_hash
        
        Returns:
            Batch verification result
        """
        results = []
        verified_count = 0
        corrupted_count = 0
        
        for backup_id, current_hash in backup_hashes.items():
            result = self.verify_backup_integrity(backup_id, current_hash)
            results.append(result)
            
            if result["status"] == "VERIFIED":
                verified_count += 1
            else:
                corrupted_count += 1
        
        return {
            "total_verified": verified_count,
            "total_corrupted": corrupted_count,
            "verification_rate": f"{(verified_count / len(backup_hashes) * 100):.2f}%" if backup_hashes else "0%",
            "results": results
        }
    
    def get_backup_recovery_plan(self, corrupted_backup_id: str) -> Dict[str, Any]:
        """
        Generate recovery plan for corrupted backup.
        
        Args:
            corrupted_backup_id: ID of corrupted backup
        
        Returns:
            Recovery plan
        """
        if corrupted_backup_id not in self.backups:
            return {"status": "FAILED", "reason": "Backup not found"}
        
        # Find alternative backups
        alternative_backups = []
        corrupted = self.backups[corrupted_backup_id]
        
        for bid, backup in self.backups.items():
            if bid != corrupted_backup_id and backup.integrity_verified:
                alternative_backups.append({
                    "backup_id": bid,
                    "backup_time": backup.backup_time,
                    "location": backup.location,
                    "file_count": backup.file_count
                })
        
        recovery_plan = {
            "corrupted_backup": corrupted_backup_id,
            "corruption_detected": corrupted.backup_status == "CORRUPTED",
            "alternative_backups_available": len(alternative_backups),
            "alternatives": alternative_backups,
            "recovery_priority": "HIGH" if corrupted.backup_status == "CORRUPTED" else "NORMAL",
            "recommended_action": "Use alternative backup" if alternative_backups else "Manual recovery required",
            "recovery_steps": [
                "1. Identify alternative verified backup",
                "2. Verify blockchain integrity of alternative",
                "3. Decrypt and restore files from alternative",
                "4. Verify restored file integrity",
                "5. Delete corrupted backup"
            ] if alternative_backups else [
                "1. No verified backups available",
                "2. Contact support for manual recovery",
                "3. Attempt file carving recovery",
                "4. Use disaster recovery procedures"
            ]
        }
        
        return recovery_plan
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        verified_backups = sum(1 for b in self.backups.values() if b.integrity_verified)
        corrupted_backups = sum(1 for b in self.backups.values() if b.backup_status == "CORRUPTED")
        
        total_backup_size = sum(b.file_size for b in self.backups.values())
        total_files = sum(b.file_count for b in self.backups.values())
        
        return {
            "total_backups": len(self.backups),
            "verified_backups": verified_backups,
            "corrupted_backups": corrupted_backups,
            "blockchain_registered": len(self.blockchain_refs),
            "verification_rate": f"{(verified_backups / len(self.backups) * 100):.2f}%" if self.backups else "0%",
            "total_backup_size": f"{total_backup_size / (1024**3):.2f} GB",
            "total_files_backed_up": total_files,
            "failed_verifications": self.failed_verifications
        }
    
    def generate_backup_report(self) -> str:
        """Generate comprehensive backup report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_backup_statistics(),
            "backups": [
                {
                    "backup": b.to_dict(),
                    "blockchain_hash": self.blockchain_refs.get(bid, "NOT_REGISTERED")
                }
                for bid, b in self.backups.items()
            ],
            "verification_log": self.verification_log[-10:],  # Last 10 verifications
            "recommendations": [
                "✓ Regularly verify backup integrity",
                "✓ Maintain multiple backup copies",
                "✓ Store backup hashes on blockchain",
                "✓ Test recovery procedures monthly",
                "✓ Keep offline backup copies"
            ] if self.failed_verifications == 0 else [
                "⚠ CRITICAL: Corrupted backups detected",
                "⚠ Restore from alternative backups immediately",
                "⚠ Investigate cause of corruption",
                "⚠ Implement backup redundancy",
                "⚠ Consider backup service provider"
            ]
        }
        
        return json.dumps(report, indent=2)
    
    def export_backups_to_blockchain(self) -> List[Dict[str, Any]]:
        """Export all backup information for blockchain storage."""
        return [
            {
                "backup": b.to_dict(),
                "blockchain_hash": self.blockchain_refs.get(bid),
                "can_recover": b.integrity_verified
            }
            for bid, b in self.backups.items()
        ]
