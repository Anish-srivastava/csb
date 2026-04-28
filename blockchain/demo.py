"""Blockchain demonstration and testing script."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from blockchain import (
    initialize_blockchain,
    get_blockchain,
    log_suspicious_activity,
    log_file_encrypted,
    log_file_recovered,
    print_blockchain_summary,
    export_blockchain_report
)


def demo_blockchain():
    """Demonstrate blockchain functionality."""
    
    print("\n" + "="*70)
    print("🔗 BLOCKCHAIN DEMONSTRATION FOR RANSOMWARE DETECTION 🔗")
    print("="*70 + "\n")
    
    # Initialize blockchain
    print("1️⃣  Initializing blockchain...")
    blockchain = initialize_blockchain(difficulty=2)
    print("   ✅ Blockchain initialized\n")
    
    # Simulate ransomware attacks
    print("2️⃣  Logging ransomware attack events...\n")
    
    attack_events = [
        {
            "file": "test_folder/document.txt",
            "type": "rapid_changes",
            "severity": "HIGH",
            "details": "5 file modifications in 10 seconds"
        },
        {
            "file": "test_folder/photo.jpg",
            "type": "extension_change",
            "severity": "HIGH",
            "details": "File extension changed to .locked"
        },
        {
            "file": "test_folder/data.xlsx",
            "type": "encryption",
            "severity": "HIGH",
            "details": "File encrypted with unknown encryption method"
        },
        {
            "file": "test_folder/backup.zip",
            "type": "suspicious_access",
            "severity": "MEDIUM",
            "details": "Backup file accessed by unknown process"
        }
    ]
    
    for i, event in enumerate(attack_events, 1):
        log_suspicious_activity(
            file_path=event["file"],
            activity_type=event["type"],
            severity=event["severity"],
            details=event["details"]
        )
        print(f"   ✅ Event {i} logged to blockchain\n")
    
    # Simulate file encryption events
    print("3️⃣  Logging file encryption events...\n")
    
    encryption_events = [
        ("test_folder/document.txt", "Fernet", "Encrypted with Fernet cipher"),
        ("test_folder/photo.jpg", "AES-256", "Encrypted with AES-256"),
        ("test_folder/data.xlsx", "Hybrid Cipher", "Encrypted with hybrid cipher")
    ]
    
    for i, (file_path, method, details) in enumerate(encryption_events, 1):
        log_file_encrypted(
            file_path=file_path,
            encryption_method=method,
            details=details
        )
        print(f"   ✅ Encryption event {i} logged\n")
    
    # Simulate recovery attempts
    print("4️⃣  Logging file recovery attempts...\n")
    
    recovery_events = [
        ("test_folder/document.txt", "backup_restore", True, "Restored from backup"),
        ("test_folder/photo.jpg", "decryption", False, "Decryption key not available"),
        ("test_folder/data.xlsx", "backup_restore", True, "Restored from encrypted backup")
    ]
    
    for i, (file_path, method, success, details) in enumerate(recovery_events, 1):
        log_file_recovered(
            file_path=file_path,
            recovery_method=method,
            success=success,
            details=details
        )
        print(f"   ✅ Recovery event {i} logged\n")
    
    # Verify blockchain integrity
    print("5️⃣  Verifying blockchain integrity...")
    blockchain = get_blockchain()
    is_valid = blockchain.verify_chain_integrity()
    if is_valid:
        print("   ✅ Blockchain is valid - NO TAMPERING DETECTED!\n")
    else:
        print("   ❌ Blockchain has been tampered with!\n")
    
    # Print blockchain summary
    print("6️⃣  Blockchain Statistics:\n")
    print_blockchain_summary()
    
    # Search functionality demo
    print("7️⃣  Searching blockchain...\n")
    
    file_to_search = "test_folder/document.txt"
    results = blockchain.search_by_file_hash("abc123")
    print(f"   📍 Events for {file_to_search}: {len(results)} found")
    
    encrypted_events = blockchain.search_by_event_type("FILE_ENCRYPTED")
    print(f"   📍 Total FILE_ENCRYPTED events: {len(encrypted_events)}\n")
    
    recovery_events = blockchain.search_by_event_type("FILE_RECOVERY")
    print(f"   📍 Total FILE_RECOVERY events: {len(recovery_events)}\n")
    
    # Export report
    print("8️⃣  Exporting blockchain report...\n")
    report_path = Path(__file__).resolve().parent.parent / "logs" / "blockchain_demo_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    export_blockchain_report(report_path)
    
    # Print blockchain as JSON
    print("\n9️⃣  Complete Blockchain in JSON Format:\n")
    print(blockchain.get_chain_as_json())
    
    print("\n" + "="*70)
    print("✅ BLOCKCHAIN DEMONSTRATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Blockchain report saved to: {report_path}\n")


if __name__ == "__main__":
    demo_blockchain()
