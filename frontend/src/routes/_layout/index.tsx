import { createFileRoute, Navigate } from "@tanstack/react-router"
import useAuth from "@/hooks/useAuth"
import "leaflet/dist/leaflet.css"
import {
  getStartPagePath,
  isFieldEmployeeRole,
} from "@/features/navigation/roleSections"
import { pageTitles } from "@/lib/i18n/ru"
import { FieldEmployee } from "./FieldEmployee"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: pageTitles.dashboard,
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const roleName = currentUser?.role?.name
  if (isFieldEmployeeRole(roleName)) {
    return <FieldEmployee />
  }

  const startPagePath = getStartPagePath(roleName)
  if (startPagePath) {
    return <Navigate to={startPagePath} replace />
  }

  return null
}
