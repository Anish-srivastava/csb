"""Comprehensive incident response chain tracking on blockchain."""

import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


class IncidentPhase(Enum):
    """Phases of incident response."""
    DETECTION = "DETECTION"
    ANALYSIS = "ANALYSIS"
    CONTAINMENT = "CONTAINMENT"
    ERADICATION = "ERADICATION"
    RECOVERY = "RECOVERY"
    POST_INCIDENT = "POST_INCIDENT"
    CLOSED = "CLOSED"


class IncidentSeverity(Enum):
    """Incident severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class IncidentAction:
    """Single action taken during incident response."""
    action_id: str
    action_type: str  # detect, isolate, decrypt, backup, etc.
    timestamp: str
    phase: str
    responsible_team: str
    description: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    duration_minutes: int = 0
    affected_systems: int = 0
    affected_files: int = 0
    result_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class IncidentTimeline:
    """Timeline event in incident."""
    event_id: str
    event_type: str
    timestamp: str
    details: str
    evidence: Optional[str] = None
    investigation_notes: str = ""


class IncidentResponseChain:
    """Track incident response as immutable chain on blockchain."""
    
    def __init__(self, incident_id: str, severity: str, attack_type: str):
        """
        Initialize incident response chain.
        
        Args:
            incident_id: Unique incident identifier
            severity: Incident severity level
            attack_type: Type of attack (ransomware, etc.)
        """
        self.incident_id = incident_id
        self.severity = severity
        self.attack_type = attack_type
        self.creation_time = datetime.now()
        self.incident_start_time = self.creation_time
        self.current_phase = IncidentPhase.DETECTION.value
        
        self.actions: List[IncidentAction] = []
        self.timeline: List[IncidentTimeline] = []
        self.systems_affected: List[str] = []
        self.files_affected: List[str] = []
        self.threats_identified: List[str] = []
        self.mitigations_applied: List[str] = []
        
        self.estimated_impact = 0
        self.estimated_cost = 0
        self.total_recovery_time_hours = 0
        
        self.incident_chain_hash = self.calculate_incident_hash()
    
    def calculate_incident_hash(self) -> str:
        """Calculate incident chain hash."""
        incident_data = {
            "incident_id": self.incident_id,
            "severity": self.severity,
            "attack_type": self.attack_type,
            "creation_time": self.creation_time.isoformat()
        }
        incident_string = json.dumps(incident_data, sort_keys=True)
        return hashlib.sha256(incident_string.encode()).hexdigest()
    
    def add_action(self, action_type: str, description: str, responsible_team: str = "Security",
                  affected_systems: int = 0, affected_files: int = 0) -> IncidentAction:
        """
        Add action to incident response chain.
        
        Args:
            action_type: Type of action taken
            description: Detailed description
            responsible_team: Team responsible
            affected_systems: Number of systems affected
            affected_files: Number of files affected
        
        Returns:
            IncidentAction object
        """
        action_id = f"ACT_{hashlib.sha256(f'{self.incident_id}_{len(self.actions)}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
        
        action = IncidentAction(
            action_id=action_id,
            action_type=action_type,
            timestamp=datetime.now().isoformat(),
            phase=self.current_phase,
            responsible_team=responsible_team,
            description=description,
            status="COMPLETED",
            affected_systems=affected_systems,
            affected_files=affected_files
        )
        
        self.actions.append(action)
        
        # Add to timeline
        self.add_timeline_event(
            event_type=f"ACTION_{action_type}",
            details=description,
            evidence=action_id
        )
        
        return action
    
    def add_timeline_event(self, event_type: str, details: str, evidence: str = None) -> IncidentTimeline:
        """
        Add event to incident timeline.
        
        Args:
            event_type: Type of event
            details: Event details
            evidence: Evidence identifier
        
        Returns:
            IncidentTimeline object
        """
        event_id = f"EVT_{len(self.timeline):04d}"
        
        event = IncidentTimeline(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            details=details,
            evidence=evidence
        )
        
        self.timeline.append(event)
        return event
    
    def transition_phase(self, new_phase: str, notes: str = "") -> bool:
        """
        Transition to next incident response phase.
        
        Args:
            new_phase: Phase to transition to
            notes: Transition notes
        
        Returns:
            True if transition successful
        """
        try:
            phase = IncidentPhase[new_phase]
            old_phase = self.current_phase
            self.current_phase = phase.value
            
            self.add_timeline_event(
                event_type="PHASE_TRANSITION",
                details=f"Moved from {old_phase} to {new_phase}",
                evidence=notes
            )
            
            return True
        except KeyError:
            return False
    
    def add_affected_system(self, system_id: str) -> None:
        """Add affected system to incident."""
        if system_id not in self.systems_affected:
            self.systems_affected.append(system_id)
    
    def add_affected_file(self, file_path: str) -> None:
        """Add affected file to incident."""
        if file_path not in self.files_affected:
            self.files_affected.append(file_path)
    
    def identify_threat(self, threat_name: str, threat_hash: str) -> None:
        """Identify threat/malware."""
        threat_info = f"{threat_name}:{threat_hash[:16]}"
        if threat_info not in self.threats_identified:
            self.threats_identified.append(threat_info)
    
    def apply_mitigation(self, mitigation_action: str) -> None:
        """Record mitigation action applied."""
        if mitigation_action not in self.mitigations_applied:
            self.mitigations_applied.append(mitigation_action)
    
    def close_incident(self, resolution_notes: str, lessons_learned: str = "") -> Dict[str, Any]:
        """
        Close incident and generate final report.
        
        Args:
            resolution_notes: How incident was resolved
            lessons_learned: Lessons learned from incident
        
        Returns:
            Incident closure summary
        """
        self.transition_phase("CLOSED", resolution_notes)
        
        incident_duration = datetime.now() - self.incident_start_time
        total_hours = incident_duration.total_seconds() / 3600
        self.total_recovery_time_hours = total_hours
        
        closure_summary = {
            "incident_id": self.incident_id,
            "severity": self.severity,
            "status": "CLOSED",
            "incident_duration_hours": f"{total_hours:.2f}",
            "systems_affected": len(self.systems_affected),
            "files_affected": len(self.files_affected),
            "threats_identified": len(self.threats_identified),
            "actions_taken": len(self.actions),
            "resolution": resolution_notes,
            "lessons_learned": lessons_learned,
            "closure_time": datetime.now().isoformat()
        }
        
        self.add_timeline_event(
            event_type="INCIDENT_CLOSED",
            details=closure_summary["resolution"],
            evidence=json.dumps(closure_summary)
        )
        
        return closure_summary
    
    def get_incident_summary(self) -> Dict[str, Any]:
        """Get incident summary."""
        return {
            "incident_id": self.incident_id,
            "severity": self.severity,
            "attack_type": self.attack_type,
            "current_phase": self.current_phase,
            "creation_time": self.creation_time.isoformat(),
            "systems_affected": len(self.systems_affected),
            "files_affected": len(self.files_affected),
            "threats_identified": len(self.threats_identified),
            "actions_taken": len(self.actions),
            "timeline_events": len(self.timeline),
            "incident_chain_hash": self.incident_chain_hash
        }
    
    def get_detailed_chain(self) -> Dict[str, Any]:
        """Get complete incident response chain."""
        return {
            "summary": self.get_incident_summary(),
            "phases": [
                {
                    "phase": phase.value,
                    "actions": [a.to_dict() for a in self.actions if a.phase == phase.value]
                }
                for phase in IncidentPhase
            ],
            "timeline": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "details": e.details
                }
                for e in self.timeline
            ],
            "systems_affected": self.systems_affected,
            "files_affected": self.files_affected[:20],  # First 20 for report
            "threats_identified": self.threats_identified,
            "mitigations_applied": self.mitigations_applied
        }
    
    def export_to_blockchain(self) -> str:
        """Export incident chain for blockchain storage."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "incident_chain": self.get_detailed_chain(),
            "total_actions": len(self.actions),
            "total_timeline_events": len(self.timeline),
            "chain_hash": self.incident_chain_hash
        }
        
        return json.dumps(export_data, indent=2)


class IncidentResponseRegistry:
    """Registry to manage multiple incidents."""
    
    def __init__(self):
        """Initialize incident registry."""
        self.incidents: Dict[str, IncidentResponseChain] = {}
        self.active_incidents = 0
        self.closed_incidents = 0
        self.total_recovery_hours = 0
    
    def create_incident(self, attack_type: str, severity: str) -> IncidentResponseChain:
        """Create new incident."""
        incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.sha256(attack_type.encode()).hexdigest()[:8]}"
        
        incident = IncidentResponseChain(
            incident_id=incident_id,
            severity=severity,
            attack_type=attack_type
        )
        
        self.incidents[incident_id] = incident
        self.active_incidents += 1
        
        return incident
    
    def close_incident(self, incident_id: str, resolution_notes: str) -> bool:
        """Close incident."""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.close_incident(resolution_notes)
            
            self.active_incidents -= 1
            self.closed_incidents += 1
            self.total_recovery_hours += incident.total_recovery_time_hours
            
            return True
        return False
    
    def get_registry_report(self) -> Dict[str, Any]:
        """Get registry statistics."""
        severity_counts = {}
        for incident in self.incidents.values():
            severity = incident.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_incidents": len(self.incidents),
            "active_incidents": self.active_incidents,
            "closed_incidents": self.closed_incidents,
            "severity_distribution": severity_counts,
            "total_recovery_hours": f"{self.total_recovery_hours:.2f}",
            "avg_recovery_hours": f"{(self.total_recovery_hours / self.closed_incidents if self.closed_incidents > 0 else 0):.2f}"
        }
    
    def export_registry(self) -> str:
        """Export entire registry."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_registry_report(),
            "incidents": [
                incident.get_incident_summary()
                for incident in self.incidents.values()
            ]
        }
        
        return json.dumps(export_data, indent=2)
