"""Имена ролей совпадают с сидом БД (app/db/db.sql)."""

ROLE_ADMIN = "ADMIN"
ROLE_EMPLOYEE_MANAGER = "EMPLOYEE_MANAGER"
ROLE_FIELD_EMPLOYEE = "FIELD_EMPLOYEE"
ROLE_AGENT_POINT_MANAGER = "AGENT_POINT_MANAGER"

DETAIL_ADMIN_ONLY_USERS_ROLES = (
    "Администратору доступны только разделы пользователей и ролей"
)
DETAIL_APM_ONLY_AGENT_POINTS = (
    "Менеджеру агентских точек доступна только таблица агентских точек"
)


def role_name(role: object | None) -> str | None:
    if role is None:
        return None
    return getattr(role, "name", None)


def is_admin_user(role: object | None) -> bool:
    return role_name(role) == ROLE_ADMIN


def is_employee_manager_user(role: object | None) -> bool:
    return role_name(role) == ROLE_EMPLOYEE_MANAGER


def is_agent_point_manager_user(role: object | None) -> bool:
    return role_name(role) == ROLE_AGENT_POINT_MANAGER


def is_field_employee_user(role: object | None) -> bool:
    return role_name(role) == ROLE_FIELD_EMPLOYEE


def is_agent_point_table_editor(role: object | None) -> bool:
    return is_employee_manager_user(role) or is_agent_point_manager_user(role)
