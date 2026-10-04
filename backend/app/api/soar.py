from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.database.database import get_db
from app.models.soar import SOARAction, SOARPlaybook, WebhookConfig
from app.models.user import User
from app.schemas.soar import (
    SOARActionRequest, SOARActionResponse,
    SOARPlaybookCreate, SOARPlaybookResponse,
    WebhookCreate, WebhookResponse, WebhookTestRequest
)
from app.services.soar import soar_engine
from app.dependencies import get_current_user

router = APIRouter(prefix="/soar", tags=["SOAR Active Defense"])


@router.post("/execute", response_model=SOARActionResponse, status_code=status.HTTP_201_CREATED)
async def execute_containment_action(
    payload: SOARActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes an active SOAR containment action (Block IP, Isolate Host, Revoke User, Kill Process)."""
    return await soar_engine.execute_action(
        session=db,
        req=payload,
        initiated_by=current_user.username
    )


@router.get("/actions", response_model=List[SOARActionResponse])
async def list_soar_actions(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves chronological history of all executed active defense containment actions."""
    stmt = select(SOARAction).order_by(desc(SOARAction.created_at)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/actions/{action_id}/rollback", response_model=SOARActionResponse)
async def rollback_containment(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rolls back an existing containment action (Unblocks IP, lifts host isolation, restores account)."""
    try:
        return await soar_engine.rollback_action(db, action_id, actor=current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/playbooks", response_model=List[SOARPlaybookResponse])
async def list_playbooks(db: AsyncSession = Depends(get_db)):
    """Lists all automated incident response playbooks."""
    stmt = select(SOARPlaybook).order_by(desc(SOARPlaybook.created_at))
    res = await db.execute(stmt)
    playbooks = res.scalars().all()
    if not playbooks:
        # Seed default playbooks if empty
        default_pbks = [
            SOARPlaybook(
                id="pbk-ransomware-auto",
                name="Ransomware Rapid Containment",
                description="Automatically isolates endpoint host and kills suspicious encryption processes upon mass file modifications.",
                trigger_rule_category="Execution",
                severity_threshold="CRITICAL",
                enabled=True,
                actions_sequence=[
                    {"action": "ISOLATE_HOST", "target": "$HOST"},
                    {"action": "KILL_PROCESS", "target": "$PROCESS"},
                    {"action": "TRIGGER_WEBHOOK", "target": "SOC Emergency Channel"}
                ],
                execution_count=4
            ),
            SOARPlaybook(
                id="pbk-c2-perimeter-block",
                name="Adversary C2 Beacon Perimeter Defense",
                description="Immediately deploys firewall drop rules on external C2 IPs and domain sinks.",
                trigger_rule_category="Command & Control",
                severity_threshold="HIGH",
                enabled=True,
                actions_sequence=[
                    {"action": "BLOCK_IP", "target": "$SRC_IP"},
                    {"action": "TRIGGER_WEBHOOK", "target": "Slack #soc-critical"}
                ],
                execution_count=12
            ),
            SOARPlaybook(
                id="pbk-credential-spray-lock",
                name="Account Takeover Active Lockout",
                description="Revokes JWT sessions and suspends user account following brute-force compromise.",
                trigger_rule_category="Authentication",
                severity_threshold="HIGH",
                enabled=True,
                actions_sequence=[
                    {"action": "DISABLE_USER", "target": "$USER"},
                    {"action": "BLOCK_IP", "target": "$ATTACKER_IP"}
                ],
                execution_count=7
            )
        ]
        for p in default_pbks:
            db.add(p)
        await db.commit()
        return default_pbks
    return playbooks


@router.post("/playbooks", response_model=SOARPlaybookResponse, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    payload: SOARPlaybookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registers a new automated response playbook."""
    pbk = SOARPlaybook(
        name=payload.name,
        description=payload.description,
        trigger_rule_category=payload.trigger_rule_category,
        severity_threshold=payload.severity_threshold,
        enabled=payload.enabled,
        actions_sequence=payload.actions_sequence
    )
    db.add(pbk)
    await db.commit()
    await db.refresh(pbk)
    return pbk


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(db: AsyncSession = Depends(get_db)):
    """Retrieves all configured notification webhooks (Slack, Discord, PagerDuty)."""
    stmt = select(WebhookConfig).order_by(desc(WebhookConfig.created_at))
    res = await db.execute(stmt)
    webhooks = res.scalars().all()
    if not webhooks:
        # Default mock config
        default_wh = WebhookConfig(
            id="whk-slack-secops",
            name="SOC SecOps Alerts (Slack)",
            webhook_type="SLACK",
            url="https://hooks.slack.com/services/T000/B000/XXXXX",
            enabled=True,
            events=["CRITICAL_ALERT", "INCIDENT_CREATED", "CONTAINMENT_TRIGGERED"]
        )
        db.add(default_wh)
        await db.commit()
        return [default_wh]
    return webhooks


@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registers a new external alert notification webhook."""
    wh = WebhookConfig(
        name=payload.name,
        webhook_type=payload.webhook_type.upper(),
        url=payload.url,
        enabled=payload.enabled,
        events=payload.events,
        secret_token=payload.secret_token
    )
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.post("/webhooks/test")
async def test_webhook_delivery(payload: WebhookTestRequest):
    """Sends a live test notification to verify webhook channel configuration."""
    success = await soar_engine.send_webhook_payload(
        url=payload.url,
        webhook_type=payload.webhook_type,
        title="🛡️ Specter Live SOAR Webhook Test Alert",
        details=payload.message or "Verification message sent by SOC Administrator."
    )
    return {
        "success": success,
        "url": payload.url,
        "channel_type": payload.webhook_type,
        "status": "Delivered successfully" if success else "Simulated delivery / Invalid endpoint URL"
    }
