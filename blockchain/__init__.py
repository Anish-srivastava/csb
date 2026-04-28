"""Blockchain module for immutable ransomware attack logs with 6 advanced features."""

from blockchain.blockchain import Block, Blockchain
from blockchain.blockchain_utils import (
    initialize_blockchain,
    get_blockchain,
    save_blockchain_to_file,
    load_blockchain_from_file,
    calculate_file_hash,
    log_suspicious_activity,
    log_file_encrypted,
    log_file_recovered,
    export_blockchain_report,
    print_blockchain_summary
)

# Feature 3: Smart Contracts
from blockchain.smart_contracts import (
    SmartContract,
    ContractRegistry,
    PaymentTransaction,
    PaymentStatus,
    CryptoType
)

# Feature 4: Distributed Threat Intelligence
from blockchain.distributed_threat_intelligence import (
    ThreatIntelligenceDB,
    ThreatSignature,
    SystemNode
)

# Feature 5: Backup Verification
from blockchain.backup_verification import (
    BackupIntegrityVerifier,
    BackupSnapshot
)

# Feature 6: Incident Response
from blockchain.incident_response import (
    IncidentResponseChain,
    IncidentResponseRegistry,
    IncidentPhase,
    IncidentSeverity,
    IncidentAction,
    IncidentTimeline
)

__all__ = [
    # Core blockchain
    "Block",
    "Blockchain",
    "initialize_blockchain",
    "get_blockchain",
    "calculate_file_hash",
    "log_suspicious_activity",
    "log_file_encrypted",
    "log_file_recovered",
    "export_blockchain_report",
    "print_blockchain_summary",
    
    # Feature 3: Smart Contracts
    "SmartContract",
    "ContractRegistry",
    "PaymentTransaction",
    "PaymentStatus",
    "CryptoType",
    
    # Feature 4: Threat Intelligence
    "ThreatIntelligenceDB",
    "ThreatSignature",
    "SystemNode",
    
    # Feature 5: Backup Verification
    "BackupIntegrityVerifier",
    "BackupSnapshot",
    
    # Feature 6: Incident Response
    "IncidentResponseChain",
    "IncidentResponseRegistry",
    "IncidentPhase",
    "IncidentSeverity",
    "IncidentAction",
    "IncidentTimeline"
]
