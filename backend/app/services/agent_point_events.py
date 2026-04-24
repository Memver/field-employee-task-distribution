from dataclasses import dataclass
from datetime import datetime, timezone

from app.models import AgentPointEvent
from sqlmodel import Session, select


@dataclass
class AgentPointMetricsSnapshot:
    approved_applications: int = 0
    cards_gived: int = 0
    is_cards_delivered: bool = False
    days_since_last_card_gived: int | None = None


def build_agent_point_metrics_snapshots(
    *,
    session: Session,
    agent_point_ids: list[int],
    report_time: datetime | None = None,
) -> dict[int, AgentPointMetricsSnapshot]:
    if report_time is None:
        report_time = datetime.now(timezone.utc)
    elif report_time.tzinfo is None:
        report_time = report_time.replace(tzinfo=timezone.utc)

    snapshots = {
        agent_point_id: AgentPointMetricsSnapshot() for agent_point_id in agent_point_ids
    }
    if not agent_point_ids:
        return snapshots

    events = session.exec(
        select(AgentPointEvent)
        .where(AgentPointEvent.agent_point_id.in_(agent_point_ids))
        .order_by(AgentPointEvent.event_time, AgentPointEvent.id)
    ).all()

    last_card_gived_at_by_agent_point: dict[int, datetime] = {}
    cards_gived_previous_value: dict[int, int] = {}

    for event in events:
        snapshot = snapshots.get(event.agent_point_id)
        if snapshot is None:
            continue

        event_time = event.event_time
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        if event.metric_name == "approved_applications":
            if event.metric_delta is not None:
                snapshot.approved_applications += event.metric_delta
            elif event.metric_value_num is not None:
                snapshot.approved_applications = event.metric_value_num
        elif event.metric_name == "cards_gived":
            prev_value = cards_gived_previous_value.get(
                event.agent_point_id, snapshot.cards_gived
            )
            if event.metric_delta is not None:
                snapshot.cards_gived += event.metric_delta
                if event.metric_delta > 0:
                    last_card_gived_at_by_agent_point[event.agent_point_id] = event_time
            elif event.metric_value_num is not None:
                snapshot.cards_gived = event.metric_value_num
                if event.metric_value_num > prev_value:
                    last_card_gived_at_by_agent_point[event.agent_point_id] = event_time
            cards_gived_previous_value[event.agent_point_id] = snapshot.cards_gived
        elif event.metric_name == "is_cards_delivered" and event.metric_value_bool is not None:
            snapshot.is_cards_delivered = event.metric_value_bool

    for agent_point_id, snapshot in snapshots.items():
        last_card_gived_at = last_card_gived_at_by_agent_point.get(agent_point_id)
        if last_card_gived_at is None:
            snapshot.days_since_last_card_gived = None
            continue
        snapshot.days_since_last_card_gived = (
            report_time.date() - last_card_gived_at.date()
        ).days

    return snapshots
