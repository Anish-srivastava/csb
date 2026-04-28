# Blockchain Integration for Ransomware Detection

This module adds blockchain-based immutable logging to the HybridRansomware detection and simulation system.

## Overview

The blockchain implementation provides:
- **Immutable Event Logging**: All ransomware attack events are logged to an immutable blockchain
- **Tamper-Proof Records**: Hash-based chain integrity verification prevents unauthorized modifications
- **Proof of Work**: Difficulty-based mining ensures computational integrity
- **Complete Audit Trail**: Every attack, encryption, and recovery attempt is recorded
- **Chain Verification**: Ability to verify that no blockchain records have been tampered with

## Components

### 1. **blockchain/blockchain.py**
Main blockchain implementation with:
- `Block`: Individual block in the chain
- `Blockchain`: Main blockchain class with mining, verification, and search capabilities

**Key Methods**:
- `add_attack_log()`: Log ransomware attack events
- `add_recovery_log()`: Log file recovery attempts
- `verify_chain_integrity()`: Check if blockchain has been tampered
- `search_by_file_hash()`: Find all events related to a file
- `search_by_event_type()`: Find events by type
- `get_statistics()`: Get blockchain statistics

### 2. **blockchain/blockchain_utils.py**
Integration utilities for:
- `initialize_blockchain()`: Set up global blockchain instance
- `log_suspicious_activity()`: Log attack events to blockchain
- `log_file_encrypted()`: Log encryption events
- `log_file_recovered()`: Log recovery events
- `export_blockchain_report()`: Export blockchain as JSON
- `print_blockchain_summary()`: Display blockchain statistics

### 3. **blockchain/demo.py**
Complete demonstration of blockchain functionality with:
- Creating attack events
- Logging encryption attempts
- Recording recovery operations
- Verifying chain integrity
- Exporting reports

## Features

### Event Types Logged

1. **SUSPICIOUS_RAPID_CHANGES**: Rapid file modifications (ransomware signature)
2. **SUSPICIOUS_EXTENSION_CHANGE**: Files renamed with .locked extension
3. **SUSPICIOUS_ENCRYPTION**: Files encrypted with unknown methods
4. **SUSPICIOUS_SUSPICIOUS_ACCESS**: Suspicious file access patterns
5. **FILE_ENCRYPTED**: Specific file encryption recorded
6. **FILE_RECOVERY**: File recovery attempts (success/failure)

### Severity Levels

- **HIGH**: Critical threats (encryption, .locked files)
- **MEDIUM**: Suspicious activity
- **LOW**: Normal operations

## Integration with Detector

The blockchain is automatically integrated into the ransomware detector:

```python
# When suspicious activity is detected
log_suspicious_activity(
    file_path="test_folder/file.txt",
    activity_type="rapid_changes",
    severity="HIGH",
    details="5 modifications in 10 seconds"
)

# When .locked file is detected
log_suspicious_activity(
    file_path="test_folder/file.locked",
    activity_type="locked_extension",
    severity="HIGH",
    details="File renamed with .locked extension"
)
```

## Usage

### Basic Usage

```python
from blockchain import initialize_blockchain, get_blockchain

# Initialize blockchain
blockchain = initialize_blockchain(difficulty=2)

# Log an attack event
blockchain.add_attack_log(
    event_type="FILE_ENCRYPTED",
    file_path="test_folder/important.docx",
    file_hash="abc123...",
    severity="HIGH",
    details="File encrypted with Fernet"
)

# Verify integrity
is_valid = blockchain.verify_chain_integrity()
print(f"Chain valid: {is_valid}")
```

### Run the Demo

```bash
python blockchain/demo.py
```

This will:
1. Initialize a blockchain
2. Log simulated ransomware attack events
3. Log encryption attempts
4. Log recovery operations
5. Verify chain integrity
6. Export a comprehensive report
7. Display blockchain statistics

### Integration with Detector

```bash
python detector/monitor.py
```

The detector automatically:
- Initializes blockchain on startup
- Logs all suspicious activities
- Exports blockchain report on shutdown
- Displays blockchain summary

## Blockchain Report Format

Example JSON export structure:

```json
{
  "timestamp": "2026-04-28T10:30:00",
  "output_file": "logs/blockchain_report.json",
  "statistics": {
    "total_blocks": 11,
    "total_events": 10,
    "event_breakdown": {
      "FILE_ENCRYPTED": 3,
      "FILE_RECOVERY": 3,
      "SUSPICIOUS_RAPID_CHANGES": 1
    },
    "severity_distribution": {
      "HIGH": 6,
      "MEDIUM": 1,
      "LOW": 0
    },
    "chain_valid": true
  },
  "chain": [
    {
      "index": 0,
      "timestamp": "2026-04-28T20:19:27",
      "data": {
        "event": "GENESIS",
        "description": "Blockchain initialized",
        "source": "HybridRansomware"
      },
      "previous_hash": "0",
      "nonce": 181,
      "hash": "00a1b2c3d4e5f6..."
    }
  ]
}
```

## Proof of Work

The blockchain uses a simple Proof of Work mechanism:
- **Difficulty**: Configurable number of leading zeros required in block hash
- **Default**: 2 leading zeros per block
- **Mining**: Adjusts nonce until target difficulty is reached
- **Verification**: Re-calculates hashes to detect tampering

## Security Features

1. **Hash Chain**: Each block links to previous block's hash
2. **Tamper Detection**: Any modification breaks the chain
3. **File Integrity**: SHA-256 hashes of files recorded
4. **Immutability**: Past records cannot be changed without invalidating entire chain
5. **Timestamp**: All events timestamped
6. **Event Details**: Complete context recorded

## Performance Characteristics

- **Block Creation**: ~50-100ms per block (difficulty=2)
- **Chain Verification**: O(n) - must check all blocks
- **Search Operations**: O(n) - linear scan of chain
- **Memory**: Entire chain stored in memory (~1KB per event)

## Future Enhancements

Possible additions:
- Distributed blockchain network
- Smart contracts for ransom tracking
- Real-time blockchain explorer UI
- Merkle tree optimization
- Persistent blockchain storage (SQLite/PostgreSQL)
- Integration with Ethereum mainnet
- Multi-signature verification

## Files

```
blockchain/
├── __init__.py              # Package initialization
├── blockchain.py            # Core blockchain implementation
├── blockchain_utils.py      # Integration utilities
├── demo.py                  # Demonstration script
└── README.md               # This file
```

## License

Educational/Research use only. See main project README for license details.
