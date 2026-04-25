from dataclasses import dataclass


@dataclass(frozen=True)
class AgentPointEventRule:
    event_type: str
    metric_name: str
    allowed_value_fields: frozenset[str]


EVENT_RULES: tuple[AgentPointEventRule, ...] = (
    AgentPointEventRule(
        event_type="cards_delivery_status_changed",
        metric_name="is_cards_delivered",
        allowed_value_fields=frozenset({"metric_value_bool"}),
    ),
    AgentPointEventRule(
        event_type="approved_applications_changed",
        metric_name="approved_applications",
        allowed_value_fields=frozenset({"metric_delta", "metric_value_num"}),
    ),
    AgentPointEventRule(
        event_type="cards_gived_changed",
        metric_name="cards_gived",
        allowed_value_fields=frozenset({"metric_delta", "metric_value_num"}),
    ),
)

EVENT_RULES_BY_PAIR: dict[tuple[str, str], AgentPointEventRule] = {
    (rule.event_type, rule.metric_name): rule for rule in EVENT_RULES
}

VALUE_FIELDS: tuple[str, ...] = ("metric_delta", "metric_value_num", "metric_value_bool")


def validate_agent_point_event_payload(
    *,
    event_type: str,
    metric_name: str | None,
    metric_delta: int | None,
    metric_value_num: int | None,
    metric_value_bool: bool | None,
) -> None:
    present_value_fields = [
        field_name
        for field_name, field_value in (
            ("metric_delta", metric_delta),
            ("metric_value_num", metric_value_num),
            ("metric_value_bool", metric_value_bool),
        )
        if field_value is not None
    ]
    if len(present_value_fields) != 1:
        raise ValueError(
            "Exactly one of metric_delta, metric_value_num, metric_value_bool must be set"
        )

    if metric_name is None:
        raise ValueError("metric_name must be set")

    rule = EVENT_RULES_BY_PAIR.get((event_type, metric_name))
    if rule is None:
        raise ValueError("Unsupported event_type and metric_name combination")

    selected_value_field = present_value_fields[0]
    if selected_value_field not in rule.allowed_value_fields:
        raise ValueError(
            "Selected metric value field is not allowed for event_type and metric_name"
        )
