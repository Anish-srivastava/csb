# Hybrid Ransomware Attack Simulation & Detection System

Educational sandbox project for understanding hybrid ransomware behavior and detection with blockchain-based immutable logging.

## Features

- 🔐 **Hybrid Encryption**: Fernet cipher for file encryption
- 🔍 **Real-time Detection**: Watchdog-based file system monitoring
- 🤖 **Machine Learning**: Scikit-learn models for behavior classification
- 📊 **Dashboard**: Flask-based web interface for visualization
- 🔗 **Blockchain Logging**: Immutable records of all events
- 📈 **Statistics**: Comprehensive attack analytics
- 🛡️ **Safe Environment**: Isolated test folder only

## Safety Rules

- Operates only on `test_folder`
- Does not touch system directories
- Intended only for controlled lab/learning environments

## Project Structure

```
HybridRansomware/
├── simulator/              # Attack simulation
│   ├── encrypt.py
│   ├── decrypt.py
│   └── key.key
├── detector/               # Attack detection
│   └── monitor.py
├── ml/                     # Machine learning models
│   ├── train_model.py
│   └── model.pkl
├── blockchain/             # NEW: Immutable event logging
│   ├── blockchain.py
│   ├── blockchain_utils.py
│   ├── demo.py
│   └── README.md
├── dashboard/              # Web interface
│   ├── app.py
│   └── templates/index.html
├── logs/                   # Activity logs & blockchain reports
├── test_folder/            # Test environment
├── backup/                 # Encrypted backups
└── requirements.txt
```

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Add some sample files into `test_folder`

3. Train ML model:

   ```bash
   python ml/train_model.py
   ```

4. **NEW**: Test blockchain functionality:

   ```bash
   python blockchain/demo.py
   ```

5. Start detector (with blockchain logging):

   ```bash
   python detector/monitor.py
   ```

6. In another terminal, run encryption simulation:

   ```bash
   python simulator/encrypt.py
   ```

7. Start dashboard:

   ```bash
   python dashboard/app.py
   ```

8. Recover files:

   ```bash
   python simulator/decrypt.py
   ```

## Blockchain Integration (NEW)

All ransomware events are now logged to an immutable blockchain:

- **Attack Events**: Rapid file changes, .locked extensions, encryption attempts
- **Recovery Events**: File recovery attempts and success/failure status
- **Immutability**: Hash-based chain prevents tampering
- **Verification**: Built-in chain integrity checking
- **Reports**: JSON export of complete blockchain history

### Blockchain Features

✅ Immutable attack logs  
✅ File integrity verification  
✅ Tamper detection  
✅ Complete audit trail  
✅ Proof of Work mining  
✅ Chain verification  

### View Blockchain Report

After running the detector, find the blockchain report at:
```
logs/blockchain_report.json
```

For more details, see [blockchain/README.md](blockchain/README.md)

