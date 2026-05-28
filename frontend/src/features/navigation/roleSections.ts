import {
  Briefcase,
  CircleGauge,
  Clock3,
  ListChecks,
  type LucideIcon,
  MapPinned,
  Shield,
  Target,
  Users,
  Wrench,
} from "lucide-react"
import { nav } from "@/lib/i18n/ru"

export type RoleName =
  | "ADMIN"
  | "EMPLOYEE_MANAGER"
  | "FIELD_EMPLOYEE"
  | "AGENT_POINT_MANAGER"

export type NavigationSection = {
  key: string
  title: string
  path: string
  icon: LucideIcon
}

export type StartPagePath = "/admin" | "/tasks"

const dashboardSection: NavigationSection = {
  key: "dashboard",
  title: nav.dashboard,
  path: "/",
  icon: CircleGauge,
}

const sectionsByKey: Record<string, NavigationSection> = {
  users: { key: "users", title: "Пользователи", path: "/admin", icon: Shield },
  roles: { key: "roles", title: "Роли", path: "/roles", icon: Shield },
  grades: { key: "grades", title: "Грейды", path: "/grades", icon: Briefcase },
  locations: {
    key: "locations",
    title: "Локации",
    path: "/locations",
    icon: MapPinned,
  },
  priorities: {
    key: "priorities",
    title: "Приоритеты",
    path: "/priorities",
    icon: ListChecks,
  },
  taskStatuses: {
    key: "taskStatuses",
    title: "Статусы задач",
    path: "/task-statuses",
    icon: ListChecks,
  },
  employees: {
    key: "employees",
    title: "Выездные сотрудники",
    path: "/employees",
    icon: Users,
  },
  taskTypes: {
    key: "taskTypes",
    title: "Типы задач",
    path: "/task-types",
    icon: Wrench,
  },
  taskCarryovers: {
    key: "taskCarryovers",
    title: "Перенесенные задачи",
    path: "/task-carryovers",
    icon: Clock3,
  },
  agentPoints: {
    key: "agentPoints",
    title: "Агентские точки",
    path: "/agent-points",
    icon: Target,
  },
  myAgentPoints: {
    key: "myAgentPoints",
    title: "Мои агентские точки",
    path: "/agent-points",
    icon: Target,
  },
  agentPointEvents: {
    key: "agentPointEvents",
    title: "События агентских точек",
    path: "/agent-point-events",
    icon: Clock3,
  },
  myAgentPointEvents: {
    key: "myAgentPointEvents",
    title: "Мои события",
    path: "/agent-point-events",
    icon: Clock3,
  },
  tasks: { key: "tasks", title: "Задачи", path: "/tasks", icon: Briefcase },
}

const roleSectionKeys: Record<RoleName, string[]> = {
  ADMIN: ["users", "roles"],
  EMPLOYEE_MANAGER: [
    "grades",
    "locations",
    "priorities",
    "taskStatuses",
    "employees",
    "taskTypes",
    "taskCarryovers",
    "agentPoints",
    "agentPointEvents",
    "tasks",
  ],
  FIELD_EMPLOYEE: [],
  AGENT_POINT_MANAGER: ["myAgentPoints", "myAgentPointEvents", "tasks"],
}

const startPageByRole: Partial<Record<RoleName, StartPagePath>> = {
  ADMIN: "/admin",
  EMPLOYEE_MANAGER: "/tasks",
  AGENT_POINT_MANAGER: "/tasks",
}

export function getRoleName(roleName: string | undefined): RoleName | null {
  if (!roleName) {
    return null
  }
  if (roleName in roleSectionKeys) {
    return roleName as RoleName
  }
  return null
}

export function getDashboardSections(
  roleName: string | undefined,
): NavigationSection[] {
  const safeRole = getRoleName(roleName)
  if (!safeRole) {
    return []
  }
  return roleSectionKeys[safeRole]
    .map((key) => sectionsByKey[key])
    .filter(Boolean)
}

export function getSidebarSections(
  roleName: string | undefined,
): NavigationSection[] {
  return [dashboardSection, ...getDashboardSections(roleName)]
}

export function getStartPagePath(
  roleName: string | undefined,
): StartPagePath | null {
  const safeRole = getRoleName(roleName)
  if (!safeRole) {
    return null
  }
  return startPageByRole[safeRole] ?? null
}

export function isFieldEmployeeRole(roleName: string | undefined): boolean {
  return getRoleName(roleName) === "FIELD_EMPLOYEE"
}

export function isAgentPointManagerRole(roleName: string | undefined): boolean {
  return getRoleName(roleName) === "AGENT_POINT_MANAGER"
}

export function isEmployeeManagerRole(roleName: string | undefined): boolean {
  return getRoleName(roleName) === "EMPLOYEE_MANAGER"
}
