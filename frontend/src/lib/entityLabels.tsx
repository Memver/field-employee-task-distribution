import type {
  AgentPointPublic,
  EmployeePublic,
  LocationPublic,
  UserRefPublic,
} from "@/client"
import { cn } from "@/lib/utils"

export function formatUserRef(user: UserRefPublic | undefined | null): string {
  if (!user) return "—"
  const fullName = [user.surname, user.name, user.middle_name]
    .filter(Boolean)
    .join(" ")
    .trim()
  return fullName || user.login
}

export function formatLocation(
  location: LocationPublic | undefined | null,
): string {
  if (!location?.address) return "—"
  return location.address
}

export function formatAgentPoint(
  agentPoint: AgentPointPublic | undefined | null,
): string {
  if (!agentPoint) return "—"
  return formatLocation(agentPoint.location)
}

export function formatEmployee(
  employee: EmployeePublic | undefined | null,
): string {
  if (!employee) return "—"
  return formatUserRef(employee.user)
}

export function isEmptyValue(value: unknown): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === "string") return value.trim() === ""
  return false
}

export function formatEmptyCell(
  value: unknown,
  fallback = "—",
): { text: string; isEmpty: boolean } {
  const isEmpty = isEmptyValue(value)
  return {
    text: isEmpty ? fallback : String(value),
    isEmpty,
  }
}

export function EmptyCell({
  value,
  emptyFallback = "—",
}: {
  value: unknown
  emptyFallback?: string
}) {
  const { text, isEmpty } = formatEmptyCell(value, emptyFallback)
  return (
    <span className={cn(isEmpty && "text-muted-foreground italic")}>{text}</span>
  )
}
