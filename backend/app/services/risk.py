from typing import Dict, Any, List
import logging

logger = logging.getLogger("specter.services.risk")


class RiskScoringEngine:
    """Transparent multi-factor risk scoring engine normalizing metrics between 0 and 100."""

    @staticmethod
    def calculate_risk(
        severity: str = "informational",
        confidence: float = 0.8,
        entity_criticality: str = "medium",
        anomaly_score: float = 0.0,
        ioc_matched: bool = False,
        attack_chain_depth: int = 1
    ) -> Dict[str, Any]:
        # 1. Severity Base Weights
        sev_weights = {
            "informational": 10,
            "low": 25,
            "medium": 50,
            "high": 75,
            "critical": 90
        }
        base_sev = sev_weights.get(severity.lower(), 25)

        # 2. Criticality Multiplier
        crit_weights = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.2,
            "critical": 1.4
        }
        crit_factor = crit_weights.get(entity_criticality.lower(), 1.0)

        # 3. Anomaly Contribution
        anomaly_points = int(anomaly_score * 20)

        # 4. IOC Contribution
        ioc_points = 20 if ioc_matched else 0

        # 5. Attack-Chain Depth Multiplier (1-5 stages)
        depth_points = min(25, (attack_chain_depth - 1) * 6)

        raw_score = (base_sev * crit_factor * confidence) + anomaly_points + ioc_points + depth_points
        normalized_score = max(0, min(100, int(raw_score)))

        # Categorization
        if normalized_score < 25:
            category = "informational"
        elif normalized_score < 50:
            category = "low"
        elif normalized_score < 75:
            category = "medium"
        elif normalized_score < 90:
            category = "high"
        else:
            category = "critical"

        return {
            "risk_score": normalized_score,
            "category": category,
            "factors": {
                "base_severity_weight": base_sev,
                "criticality_factor": crit_factor,
                "confidence": confidence,
                "anomaly_points": anomaly_points,
                "ioc_points": ioc_points,
                "chain_depth_points": depth_points
            }
        }


risk_engine = RiskScoringEngine()
