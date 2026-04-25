import { createFileRoute } from "@tanstack/react-router"
import useAuth from "@/hooks/useAuth"
import "leaflet/dist/leaflet.css"
import { Link as RouterLink } from "@tanstack/react-router"
import { ChevronRight } from "lucide-react"
import { FieldEmployee } from "./FieldEmployee"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Cloud",
      },
    ],
  }),
})

function EmployeeManagerDashboard() {
  return (
    <div className="flex flex-col items-start gap-10 text-xl">
      <RouterLink to="/grades" className="flex items-center gap-2">
        <ChevronRight />
        Грейды
      </RouterLink>
      <RouterLink to="/locations" className="flex items-center gap-2">
        <ChevronRight />
        Локации
      </RouterLink>
      <RouterLink to="/priorities" className="flex items-center gap-2">
        <ChevronRight />
        Приоритеты
      </RouterLink>
      <RouterLink to="/task-statuses" className="flex items-center gap-2">
        <ChevronRight />
        Статусы задач
      </RouterLink>
      <RouterLink to="/employees" className="flex items-center gap-2">
        <ChevronRight />
        Выездные сотрудники
      </RouterLink>
      <RouterLink to="/task-types" className="flex items-center gap-2">
        <ChevronRight />
        Типы задач
      </RouterLink>
      <RouterLink to="/agent-points" className="flex items-center gap-2">
        <ChevronRight />
        Агентские точки
      </RouterLink>
      <RouterLink to="/tasks" className="flex items-center gap-2">
        <ChevronRight />
        Задачи
      </RouterLink>
    </div>
  )
}

function AdminDashboard() {
  return (
    <div className="flex flex-col items-start gap-10 text-xl">
      <RouterLink to="/admin" className="flex items-center gap-2">
        <ChevronRight />
        Пользователи
      </RouterLink>
    </div>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  if (currentUser?.role.name === "EMPLOYEE_MANAGER") {
    return <EmployeeManagerDashboard />
  }
  if (currentUser?.role.name === "FIELD_EMPLOYEE") {
    return <FieldEmployee />
  }

  return <AdminDashboard />
}
