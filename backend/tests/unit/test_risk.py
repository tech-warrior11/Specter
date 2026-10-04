from app.services.risk import risk_engine


def test_low_risk_calculation():
    result = risk_engine.calculate_risk(
        severity="low",
        confidence=0.7,
        entity_criticality="low",
        anomaly_score=0.1,
        ioc_matched=False,
        attack_chain_depth=1
    )
    assert result["risk_score"] < 50
    assert result["category"] in ["informational", "low"]
    assert "factors" in result


def test_critical_multi_stage_risk_calculation():
    result = risk_engine.calculate_risk(
        severity="critical",
        confidence=0.95,
        entity_criticality="critical",
        anomaly_score=0.8,
        ioc_matched=True,
        attack_chain_depth=5
    )
    assert result["risk_score"] >= 90
    assert result["category"] == "critical"
    assert result["factors"]["ioc_points"] == 20
    assert result["factors"]["chain_depth_points"] == 24
