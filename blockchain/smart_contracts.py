"""Smart Contracts for ransom payment tracking on blockchain."""

import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


class PaymentStatus(Enum):
    """Status of ransom payment."""
    PENDING = "PENDING"
    INITIATED = "INITIATED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class CryptoType(Enum):
    """Types of cryptocurrency supported."""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    MONERO = "XMR"
    SIMULATED = "SIM"  # For demo purposes


@dataclass
class PaymentTransaction:
    """Represents a ransom payment transaction."""
    transaction_id: str
    timestamp: str
    amount: float
    crypto_type: str
    wallet_address: str
    status: str
    victim_identifier: str
    attacker_identifier: str
    files_count: int
    decryption_key: Optional[str] = None
    confirmation_time: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash."""
        tx_data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(tx_data.encode()).hexdigest()


class SmartContract:
    """Smart contract for managing ransom payments."""
    
    def __init__(self, contract_id: str, victim_id: str, ransom_amount: float, 
                 crypto_type: str = "SIM", files_encrypted: int = 0):
        """
        Initialize smart contract.
        
        Args:
            contract_id: Unique contract identifier
            victim_id: Identifier of victim
            ransom_amount: Amount of ransom demanded
            crypto_type: Type of cryptocurrency
            files_encrypted: Number of encrypted files
        """
        self.contract_id = contract_id
        self.victim_id = victim_id
        self.attacker_id = f"ATTACKER_{hashlib.sha256(contract_id.encode()).hexdigest()[:16]}"
        self.ransom_amount = ransom_amount
        self.crypto_type = crypto_type
        self.files_encrypted = files_encrypted
        self.creation_time = datetime.now()
        self.deadline = self.creation_time + timedelta(days=7)  # 7-day deadline
        self.transactions: List[PaymentTransaction] = []
        self.status = "ACTIVE"
        self.contract_hash = self.calculate_contract_hash()
        self.escrow_balance = 0.0
        self.payment_confirmations = 0
        self.decryption_keys_released = []
    
    def calculate_contract_hash(self) -> str:
        """Calculate contract hash."""
        contract_data = {
            "contract_id": self.contract_id,
            "victim_id": self.victim_id,
            "ransom_amount": self.ransom_amount,
            "crypto_type": self.crypto_type,
            "creation_time": self.creation_time.isoformat()
        }
        contract_string = json.dumps(contract_data, sort_keys=True)
        return hashlib.sha256(contract_string.encode()).hexdigest()
    
    def initiate_payment(self, wallet_address: str, amount: float) -> PaymentTransaction:
        """
        Initiate payment transaction.
        
        Args:
            wallet_address: Cryptocurrency wallet address
            amount: Payment amount
        
        Returns:
            PaymentTransaction object
        """
        tx_id = f"TX_{hashlib.sha256(f'{self.contract_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        transaction = PaymentTransaction(
            transaction_id=tx_id,
            timestamp=datetime.now().isoformat(),
            amount=amount,
            crypto_type=self.crypto_type,
            wallet_address=wallet_address,
            status=PaymentStatus.INITIATED.value,
            victim_identifier=self.victim_id,
            attacker_identifier=self.attacker_id,
            files_count=self.files_encrypted,
            notes=f"Payment initiated for contract {self.contract_id}"
        )
        
        self.transactions.append(transaction)
        self.escrow_balance += amount
        
        return transaction
    
    def confirm_payment(self, transaction_id: str, confirmation_hash: str) -> bool:
        """
        Confirm payment received.
        
        Args:
            transaction_id: Transaction to confirm
            confirmation_hash: Blockchain confirmation hash
        
        Returns:
            True if confirmed, False otherwise
        """
        for tx in self.transactions:
            if tx.transaction_id == transaction_id:
                if tx.status == PaymentStatus.INITIATED.value:
                    tx.status = PaymentStatus.CONFIRMED.value
                    tx.confirmation_time = datetime.now().isoformat()
                    self.payment_confirmations += 1
                    
                    # Check if full payment received
                    if self.escrow_balance >= self.ransom_amount:
                        self.complete_payment()
                    
                    return True
        return False
    
    def complete_payment(self) -> Dict[str, Any]:
        """
        Complete payment and release decryption key.
        
        Returns:
            Payment completion details with decryption key
        """
        for tx in self.transactions:
            if tx.status == PaymentStatus.CONFIRMED.value:
                tx.status = PaymentStatus.COMPLETED.value
        
        # Generate simulated decryption key
        decryption_key = hashlib.sha256(
            f"{self.contract_id}_{self.creation_time.isoformat()}".encode()
        ).hexdigest()
        
        self.status = "COMPLETED"
        self.decryption_keys_released.append(decryption_key)
        
        return {
            "status": "PAYMENT_COMPLETED",
            "decryption_key": decryption_key,
            "files_count": self.files_encrypted,
            "timestamp": datetime.now().isoformat()
        }
    
    def fail_payment(self, transaction_id: str, reason: str) -> bool:
        """
        Mark payment as failed.
        
        Args:
            transaction_id: Transaction to mark as failed
            reason: Reason for failure
        
        Returns:
            True if marked failed
        """
        for tx in self.transactions:
            if tx.transaction_id == transaction_id:
                tx.status = PaymentStatus.FAILED.value
                tx.notes = reason
                self.escrow_balance -= tx.amount
                return True
        return False
    
    def is_deadline_passed(self) -> bool:
        """Check if payment deadline has passed."""
        return datetime.now() > self.deadline
    
    def get_contract_details(self) -> Dict[str, Any]:
        """Get complete contract details."""
        return {
            "contract_id": self.contract_id,
            "victim_id": self.victim_id,
            "attacker_id": self.attacker_id,
            "ransom_amount": self.ransom_amount,
            "crypto_type": self.crypto_type,
            "files_encrypted": self.files_encrypted,
            "creation_time": self.creation_time.isoformat(),
            "deadline": self.deadline.isoformat(),
            "deadline_passed": self.is_deadline_passed(),
            "status": self.status,
            "contract_hash": self.contract_hash,
            "escrow_balance": self.escrow_balance,
            "payment_confirmations": self.payment_confirmations,
            "transactions_count": len(self.transactions),
            "decryption_keys_released": len(self.decryption_keys_released)
        }
    
    def get_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions for this contract."""
        return [tx.to_dict() for tx in self.transactions]
    
    def refund_payment(self, reason: str = "Ransomware payment refund") -> bool:
        """Refund all payments."""
        for tx in self.transactions:
            if tx.status in [PaymentStatus.CONFIRMED.value, PaymentStatus.INITIATED.value]:
                tx.status = PaymentStatus.REFUNDED.value
                tx.notes = reason
        
        self.status = "REFUNDED"
        self.escrow_balance = 0.0
        return True


class ContractRegistry:
    """Registry to manage multiple smart contracts."""
    
    def __init__(self):
        """Initialize contract registry."""
        self.contracts: Dict[str, SmartContract] = {}
        self.total_ransom_value = 0.0
        self.total_payments_received = 0.0
    
    def create_contract(self, victim_id: str, ransom_amount: float, 
                       files_encrypted: int) -> SmartContract:
        """Create new smart contract."""
        contract_id = f"SC_{hashlib.sha256(f'{victim_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        contract = SmartContract(
            contract_id=contract_id,
            victim_id=victim_id,
            ransom_amount=ransom_amount,
            crypto_type="SIM",
            files_encrypted=files_encrypted
        )
        
        self.contracts[contract_id] = contract
        self.total_ransom_value += ransom_amount
        
        return contract
    
    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get contract by ID."""
        return self.contracts.get(contract_id)
    
    def get_all_contracts(self) -> List[SmartContract]:
        """Get all contracts."""
        return list(self.contracts.values())
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        active_contracts = sum(1 for c in self.contracts.values() if c.status == "ACTIVE")
        completed_contracts = sum(1 for c in self.contracts.values() if c.status == "COMPLETED")
        
        total_received = sum(c.escrow_balance for c in self.contracts.values() if c.status == "COMPLETED")
        
        return {
            "total_contracts": len(self.contracts),
            "active_contracts": active_contracts,
            "completed_contracts": completed_contracts,
            "total_ransom_demanded": self.total_ransom_value,
            "total_payments_received": total_received,
            "completion_rate": f"{(completed_contracts / len(self.contracts) * 100):.2f}%" if self.contracts else "0%"
        }
    
    def export_registry(self) -> Dict[str, Any]:
        """Export entire registry as dictionary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_registry_statistics(),
            "contracts": [
                {
                    "details": c.get_contract_details(),
                    "transactions": c.get_transactions()
                }
                for c in self.contracts.values()
            ]
        }
