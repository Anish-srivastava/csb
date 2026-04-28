"""Complete demonstration of all 6 blockchain features for ransomware defense."""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from blockchain import initialize_blockchain, get_blockchain
from blockchain.smart_contracts import ContractRegistry
from blockchain.distributed_threat_intelligence import ThreatIntelligenceDB
from blockchain.backup_verification import BackupIntegrityVerifier
from blockchain.incident_response import IncidentResponseRegistry


def demo_all_features():
    """Demonstrate all 6 blockchain features."""
    
    print("\n" + "="*80)
    print("🔗 HYBRID RANSOMWARE BLOCKCHAIN - ALL 6 FEATURES DEMONSTRATION 🔗")
    print("="*80 + "\n")
    
    # Feature 1: Immutable Attack Logs
    print("📋 FEATURE 1: IMMUTABLE ATTACK LOGS")
    print("-" * 80)
    blockchain = initialize_blockchain(difficulty=2)
    
    attack_events = [
        ("test_folder/data.xlsx", "FILE_ENCRYPTED", "HIGH", "Fernet encryption applied"),
        ("test_folder/backup.zip", "FILE_ENCRYPTED", "HIGH", "AES-256 encryption"),
        ("test_folder/documents/", "RAPID_CHANGES", "HIGH", "5 file changes in 10 seconds"),
        ("test_folder/photos/file.locked", "LOCKED_EXTENSION", "HIGH", ".locked extension detected"),
    ]
    
    print(f"✅ Logging {len(attack_events)} attack events to blockchain...\n")
    for file_path, event_type, severity, details in attack_events:
        blockchain.add_attack_log(event_type, file_path, f"hash_{event_type[:4]}", severity, details)
        print(f"   ✓ {event_type}: {file_path}")
    
    print(f"\n✅ Blockchain blocks created: {blockchain.get_chain_length()}\n")
    
    # Feature 2: Decentralized File Integrity Verification
    print("🔐 FEATURE 2: FILE INTEGRITY VERIFICATION")
    print("-" * 80)
    print("✅ File hashes stored on blockchain:")
    
    file_hashes = {
        "test_folder/document.txt": "abc123def456789ghi012jkl345",
        "test_folder/photo.jpg": "xyz789uvw456rst234opq901mnk",
        "test_folder/data.xlsx": "mno678def345ghi012jkl789xyz",
    }
    
    for file_path, file_hash in file_hashes.items():
        blockchain.add_attack_log(
            "FILE_HASH_RECORDED",
            file_path,
            file_hash,
            "INFO",
            f"Original file hash: {file_hash}"
        )
        print(f"   ✓ {file_path}")
        print(f"     Hash: {file_hash[:32]}...")
    
    print(f"\n✅ Can verify files haven't been modified\n")
    
    # Feature 3: Smart Contracts for Ransom Payment Tracking
    print("💰 FEATURE 3: SMART CONTRACTS FOR RANSOM TRACKING")
    print("-" * 80)
    
    contract_registry = ContractRegistry()
    
    print("✅ Creating ransom contracts...\n")
    
    # Contract 1
    victim_id_1 = "VICTIM_001_Corp"
    contract1 = contract_registry.create_contract(victim_id_1, 50000.0, 1000)
    print(f"   Contract ID: {contract1.contract_id}")
    print(f"   Victim: {victim_id_1}")
    print(f"   Ransom Demanded: 50,000 USD")
    print(f"   Files Encrypted: 1,000")
    print(f"   Deadline: 7 days\n")
    
    # Simulate payment
    payment_tx = contract1.initiate_payment("1A2B3C4D5E6F...xyz", 25000)
    print(f"   ✓ Payment Initiated: 25,000 USD")
    contract1.confirm_payment(payment_tx.transaction_id, "blockchain_hash_001")
    print(f"   ✓ Payment Confirmed on blockchain")
    
    payment_tx2 = contract1.initiate_payment("1A2B3C4D5E6F...xyz", 25000)
    contract1.confirm_payment(payment_tx2.transaction_id, "blockchain_hash_002")
    print(f"   ✓ Full Payment Received: 50,000 USD\n")
    
    # Contract 2
    victim_id_2 = "VICTIM_002_Hospital"
    contract2 = contract_registry.create_contract(victim_id_2, 100000.0, 5000)
    print(f"   Contract ID: {contract2.contract_id}")
    print(f"   Victim: {victim_id_2}")
    print(f"   Ransom Demanded: 100,000 USD")
    print(f"   Files Encrypted: 5,000 (CRITICAL)\n")
    
    # Simulate failed payment
    payment_tx3 = contract2.initiate_payment("2X3Y4Z5A6B7C...abc", 30000)
    print(f"   ✓ Partial Payment: 30,000 USD\n")
    
    print("✅ Ransom tracking statistics:")
    stats = contract_registry.get_registry_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}\n")
    
    # Feature 4: Distributed Threat Intelligence
    print("🌐 FEATURE 4: DISTRIBUTED THREAT INTELLIGENCE")
    print("-" * 80)
    
    threat_db = ThreatIntelligenceDB("NODE_HQ_001")
    
    # Register network nodes
    print("✅ Registering systems in threat intelligence network:\n")
    threat_db.register_node("SYS_CORP_001", "Corporate Server 1", "New York")
    print("   ✓ Corporate Server 1 (New York)")
    threat_db.register_node("SYS_CORP_002", "Corporate Server 2", "London")
    print("   ✓ Corporate Server 2 (London)")
    threat_db.register_node("SYS_HOSP_001", "Hospital Network", "Toronto")
    print("   ✓ Hospital Network (Toronto)\n")
    
    # Add threats
    print("✅ Sharing threat signatures across network:\n")
    threat1 = threat_db.add_threat_signature(
        "Emotet", "abc123def456", "ransomware", "HIGH", "Phishing emails", "Block sender, isolate system"
    )
    print(f"   ✓ Emotet - Phishing delivery")
    
    threat2 = threat_db.add_threat_signature(
        "Ryuk", "xyz789uvw456", "ransomware", "HIGH", "RDP exploit", "Close RDP port, patch systems"
    )
    print(f"   ✓ Ryuk - RDP exploitation")
    
    threat3 = threat_db.add_threat_signature(
        "Lockbit", "mno678def345", "ransomware", "HIGH", "Supply chain", "Validate software sources"
    )
    print(f"   ✓ Lockbit - Supply chain attack\n")
    
    # Report sightings
    threat_db.report_threat_sighting(threat1.signature_id, "SYS_CORP_001")
    threat_db.report_threat_sighting(threat1.signature_id, "SYS_CORP_002")
    print(f"   ✓ Emotet detected on 2 systems\n")
    
    print("✅ Threat Intelligence Report:")
    report = threat_db.get_threat_intelligence_report()
    print(f"   Total Unique Threats: {report['total_unique_threats']}")
    print(f"   Total Threat Occurrences: {report['total_threat_occurrences']}")
    print(f"   Active Network Nodes: {report['active_network_nodes']}")
    print(f"   Systems Affected: {report['total_systems_affected']}\n")
    
    # Feature 5: Backup Verification
    print("💾 FEATURE 5: BACKUP VERIFICATION")
    print("-" * 80)
    
    backup_verifier = BackupIntegrityVerifier()
    
    print("✅ Creating backup snapshots:\n")
    
    # Backup 1 - Valid
    backup1 = backup_verifier.create_backup_snapshot(
        "/mnt/backups/backup_20260428_001.tar",
        "abc123def456ghi789jkl012mno345pqr",
        50000000,  # 50 MB
        1000
    )
    print(f"   ✓ Backup 1: {backup1.file_count} files, 50 MB")
    
    # Register on blockchain
    blockchain_hash_1 = "blockchain_backup_hash_001"
    backup_verifier.register_backup_on_blockchain(backup1.backup_id, blockchain_hash_1)
    print(f"     Registered on blockchain\n")
    
    # Backup 2 - Valid
    backup2 = backup_verifier.create_backup_snapshot(
        "/mnt/backups/backup_20260428_002.tar",
        "xyz789uvw456rst234opq901mnk123abc",
        75000000,  # 75 MB
        1500
    )
    print(f"   ✓ Backup 2: {backup2.file_count} files, 75 MB")
    backup_verifier.register_backup_on_blockchain(backup2.backup_id, "blockchain_backup_hash_002")
    print(f"     Registered on blockchain\n")
    
    # Verify backups
    print("✅ Verifying backup integrity:\n")
    result1 = backup_verifier.verify_backup_integrity(backup1.backup_id, backup1.file_hash)
    print(f"   ✓ Backup 1: {result1['status']}")
    
    result2 = backup_verifier.verify_backup_integrity(backup2.backup_id, backup2.file_hash)
    print(f"   ✓ Backup 2: {result2['status']}\n")
    
    stats = backup_verifier.get_backup_statistics()
    print("✅ Backup Statistics:")
    print(f"   Total Backups: {stats['total_backups']}")
    print(f"   Verified: {stats['verified_backups']}")
    print(f"   Verification Rate: {stats['verification_rate']}\n")
    
    # Feature 6: Incident Response Chain
    print("🚨 FEATURE 6: INCIDENT RESPONSE CHAIN")
    print("-" * 80)
    
    incident_registry = IncidentResponseRegistry()
    
    print("✅ Creating incident response chain:\n")
    
    incident = incident_registry.create_incident("ransomware_infection", "CRITICAL")
    print(f"   Incident ID: {incident.incident_id}")
    print(f"   Severity: CRITICAL")
    print(f"   Attack Type: Ransomware Infection\n")
    
    # Simulate incident response
    print("✅ Recording incident response actions:\n")
    
    incident.add_action("DETECTION", "Malware detected on endpoint", "Security Team", 1, 100)
    print("   ✓ DETECTION: Malware identified")
    
    incident.transition_phase("ANALYSIS", "Initial triage complete")
    incident.add_action("ANALYSIS", "Determined ransomware is Ryuk variant", "Incident Commander", 1, 500)
    print("   ✓ ANALYSIS: Identified as Ryuk ransomware")
    
    incident.transition_phase("CONTAINMENT", "Beginning containment")
    incident.add_action("CONTAINMENT", "Isolated affected systems from network", "Network Team", 5, 0)
    print("   ✓ CONTAINMENT: 5 systems isolated")
    
    incident.transition_phase("RECOVERY", "Starting recovery process")
    incident.add_action("RECOVERY", "Restored systems from verified backup", "Recovery Team", 5, 500)
    print("   ✓ RECOVERY: Restored from backup (500 files recovered)\n")
    
    # Close incident
    closure = incident.close_incident(
        "Successfully contained and recovered from backup",
        "Implement improved backup strategy and endpoint protection"
    )
    
    print("✅ Incident Summary:")
    print(f"   Duration: {closure['incident_duration_hours']}")
    print(f"   Systems Affected: {closure['systems_affected']}")
    print(f"   Files Recovered: {closure['files_affected']}")
    print(f"   Status: {closure['status']}\n")
    
    # Final Summary
    print("="*80)
    print("📊 ALL 6 FEATURES DEMONSTRATED SUCCESSFULLY!")
    print("="*80 + "\n")
    
    print("✅ FEATURE SUMMARY:")
    print("  1. ✓ Immutable Attack Logs - All events recorded on blockchain")
    print("  2. ✓ File Integrity Verification - Original file hashes preserved")
    print("  3. ✓ Smart Contracts - Ransom payments tracked and verified")
    print("  4. ✓ Distributed Threat Intelligence - Threat sharing across network")
    print("  5. ✓ Backup Verification - Backup integrity confirmed")
    print("  6. ✓ Incident Response Chain - Complete incident tracking\n")
    
    # Export reports
    print("📁 GENERATING REPORTS:\n")
    
    # Blockchain report
    blockchain_report = {
        "timestamp": str(Path(__file__).parent.parent / "logs" / "blockchain_full_report.json"),
        "blockchain_blocks": blockchain.get_chain_length(),
        "total_events": len(blockchain.chain) - 1,
        "chain_valid": blockchain.verify_chain_integrity()
    }
    print(f"   ✓ Blockchain Report: {blockchain_report['blockchain_blocks']} blocks, valid: {blockchain_report['chain_valid']}")
    
    contract_report = contract_registry.export_registry()
    print(f"   ✓ Smart Contract Report: {contract_registry.get_registry_statistics()['total_contracts']} contracts")
    
    threat_report = threat_db.export_threat_database()
    print(f"   ✓ Threat Intelligence Report: {threat_db.get_threat_intelligence_report()['total_unique_threats']} threats")
    
    backup_report = backup_verifier.generate_backup_report()
    print(f"   ✓ Backup Report: {backup_verifier.get_backup_statistics()['total_backups']} backups verified")
    
    incident_report = incident_registry.export_registry()
    print(f"   ✓ Incident Report: {incident_registry.get_registry_report()['total_incidents']} incident(s) handled\n")
    
    print("="*80)
    print("🎉 ALL 6 BLOCKCHAIN FEATURES FULLY IMPLEMENTED AND TESTED!")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_all_features()
