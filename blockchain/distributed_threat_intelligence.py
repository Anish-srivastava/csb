"""Distributed Threat Intelligence sharing across blockchain network."""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict


@dataclass
class ThreatSignature:
    """Represents a threat/malware signature."""
    signature_id: str
    threat_name: str
    file_hash: str
    threat_type: str  # ransomware, trojan, backdoor, etc.
    severity: str  # HIGH, MEDIUM, LOW
    first_seen: str
    last_seen: str
    occurrence_count: int
    source_system: str
    attack_vector: str
    mitigation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SystemNode:
    """Represents a node in distributed threat intelligence network."""
    node_id: str
    system_name: str
    location: str
    last_checkin: str
    threat_signatures: List[str]  # List of signature IDs
    files_infected: int
    systems_affected: int
    is_active: bool = True


class ThreatIntelligenceDB:
    """Distributed threat intelligence database."""
    
    def __init__(self, node_id: str = "THREAT_NODE_001"):
        """
        Initialize threat intelligence database.
        
        Args:
            node_id: Unique identifier for this node
        """
        self.node_id = node_id
        self.threat_signatures: Dict[str, ThreatSignature] = {}
        self.network_nodes: Dict[str, SystemNode] = {}
        self.signature_votes: Dict[str, Dict[str, int]] = {}  # Voting for threat confirmation
        self.threat_patterns: List[Dict[str, Any]] = []
        self.last_update = datetime.now()
    
    def register_node(self, node_id: str, system_name: str, location: str) -> SystemNode:
        """Register a new system in the threat intelligence network."""
        node = SystemNode(
            node_id=node_id,
            system_name=system_name,
            location=location,
            last_checkin=datetime.now().isoformat(),
            threat_signatures=[],
            files_infected=0,
            systems_affected=1,
            is_active=True
        )
        
        self.network_nodes[node_id] = node
        return node
    
    def add_threat_signature(self, threat_name: str, file_hash: str, threat_type: str,
                           severity: str, attack_vector: str, mitigation: str,
                           source_system: str = None) -> ThreatSignature:
        """
        Add new threat signature to database.
        
        Args:
            threat_name: Name of threat
            file_hash: SHA-256 hash of malware
            threat_type: Type of threat
            severity: Severity level
            attack_vector: How threat is delivered
            mitigation: How to mitigate threat
            source_system: Which system reported this
        
        Returns:
            ThreatSignature object
        """
        if source_system is None:
            source_system = self.node_id
        
        sig_id = f"SIG_{hashlib.sha256(f'{file_hash}_{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
        
        signature = ThreatSignature(
            signature_id=sig_id,
            threat_name=threat_name,
            file_hash=file_hash,
            threat_type=threat_type,
            severity=severity,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            occurrence_count=1,
            source_system=source_system,
            attack_vector=attack_vector,
            mitigation=mitigation
        )
        
        self.threat_signatures[sig_id] = signature
        
        # Add to source node
        if source_system in self.network_nodes:
            self.network_nodes[source_system].threat_signatures.append(sig_id)
        
        # Initialize voting for this signature
        self.signature_votes[sig_id] = {source_system: 1}
        
        return signature
    
    def report_threat_sighting(self, signature_id: str, system_reporting: str) -> bool:
        """
        Report that threat was seen on another system.
        
        Args:
            signature_id: ID of threat signature
            system_reporting: System that reported sighting
        
        Returns:
            True if reported successfully
        """
        if signature_id in self.threat_signatures:
            sig = self.threat_signatures[signature_id]
            sig.occurrence_count += 1
            sig.last_seen = datetime.now().isoformat()
            
            # Vote for this threat signature
            if signature_id not in self.signature_votes:
                self.signature_votes[signature_id] = {}
            
            self.signature_votes[signature_id][system_reporting] = self.signature_votes[signature_id].get(system_reporting, 0) + 1
            
            # Update reporting system
            if system_reporting in self.network_nodes:
                self.network_nodes[system_reporting].files_infected += 1
                self.network_nodes[system_reporting].last_checkin = datetime.now().isoformat()
            
            return True
        
        return False
    
    def get_threat_by_hash(self, file_hash: str) -> Optional[ThreatSignature]:
        """Search for threat by file hash."""
        for sig in self.threat_signatures.values():
            if sig.file_hash == file_hash:
                return sig
        return None
    
    def get_threats_by_type(self, threat_type: str) -> List[ThreatSignature]:
        """Get all threats of specific type."""
        return [sig for sig in self.threat_signatures.values() if sig.threat_type == threat_type]
    
    def get_threats_by_severity(self, severity: str) -> List[ThreatSignature]:
        """Get all threats with specific severity."""
        return [sig for sig in self.threat_signatures.values() if sig.severity == severity]
    
    def share_threat_intelligence_with_node(self, target_node_id: str) -> Dict[str, Any]:
        """
        Share threat intelligence data with another node.
        
        Args:
            target_node_id: Target node to share with
        
        Returns:
            Threat data to share
        """
        return {
            "source_node": self.node_id,
            "target_node": target_node_id,
            "timestamp": datetime.now().isoformat(),
            "total_threats": len(self.threat_signatures),
            "threats": [sig.to_dict() for sig in self.threat_signatures.values()],
            "network_nodes": len(self.network_nodes),
            "total_occurrences": sum(sig.occurrence_count for sig in self.threat_signatures.values())
        }
    
    def get_threat_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive threat intelligence report."""
        threat_types = {}
        severity_distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for sig in self.threat_signatures.values():
            threat_types[sig.threat_type] = threat_types.get(sig.threat_type, 0) + 1
            severity_distribution[sig.severity] = severity_distribution.get(sig.severity, 0) + 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "node_id": self.node_id,
            "total_unique_threats": len(self.threat_signatures),
            "total_threat_occurrences": sum(sig.occurrence_count for sig in self.threat_signatures.values()),
            "threat_types": threat_types,
            "severity_distribution": severity_distribution,
            "active_network_nodes": sum(1 for n in self.network_nodes.values() if n.is_active),
            "total_files_infected": sum(n.files_infected for n in self.network_nodes.values()),
            "total_systems_affected": len(self.network_nodes),
            "threat_signatures": [sig.to_dict() for sig in sorted(
                self.threat_signatures.values(),
                key=lambda x: x.occurrence_count,
                reverse=True
            )[:10]]  # Top 10 threats
        }
    
    def correlate_threats(self) -> List[Dict[str, Any]]:
        """Correlate related threats based on patterns."""
        correlations = []
        
        # Group threats by attack vector
        attack_vectors = {}
        for sig in self.threat_signatures.values():
            if sig.attack_vector not in attack_vectors:
                attack_vectors[sig.attack_vector] = []
            attack_vectors[sig.attack_vector].append(sig)
        
        # Identify correlated threat patterns
        for vector, threats in attack_vectors.items():
            if len(threats) > 1:
                correlation = {
                    "attack_vector": vector,
                    "threat_count": len(threats),
                    "threats": [sig.threat_name for sig in threats],
                    "total_occurrences": sum(sig.occurrence_count for sig in threats),
                    "avg_severity": "HIGH" if any(t.severity == "HIGH" for t in threats) else "MEDIUM"
                }
                correlations.append(correlation)
        
        return correlations
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        return {
            "total_nodes": len(self.network_nodes),
            "active_nodes": sum(1 for n in self.network_nodes.values() if n.is_active),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "system_name": n.system_name,
                    "location": n.location,
                    "threat_signatures_reported": len(n.threat_signatures),
                    "files_infected": n.files_infected,
                    "is_active": n.is_active
                }
                for n in self.network_nodes.values()
            ]
        }
    
    def get_highest_voted_threats(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get threats with highest consensus vote."""
        voted_threats = []
        
        for sig_id, votes in self.signature_votes.items():
            if sig_id in self.threat_signatures:
                sig = self.threat_signatures[sig_id]
                vote_count = sum(votes.values())
                voted_threats.append({
                    "signature": sig.to_dict(),
                    "vote_count": vote_count,
                    "voting_nodes": list(votes.keys())
                })
        
        # Sort by vote count
        return sorted(voted_threats, key=lambda x: x["vote_count"], reverse=True)[:limit]
    
    def export_threat_database(self) -> str:
        """Export threat database as JSON."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "node_id": self.node_id,
            "statistics": self.get_threat_intelligence_report(),
            "network_nodes": self.get_node_statistics(),
            "threat_correlations": self.correlate_threats(),
            "highest_voted_threats": self.get_highest_voted_threats()
        }
        
        return json.dumps(export_data, indent=2)
