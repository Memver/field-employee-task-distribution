import { createFileRoute } from "@tanstack/react-router"
import useAuth from "@/hooks/useAuth"
import "leaflet/dist/leaflet.css"
import { Link as RouterLink } from "@tanstack/react-router"
import { ChevronRight } from "lucide-react"
import {
  getDashboardSections,
  isFieldEmployeeRole,
} from "@/features/navigation/roleSections"
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

function SectionsDashboard({ roleName }: { roleName: string | undefined }) {
  const sections = getDashboardSections(roleName)
  return (
    <div className="flex flex-col items-start gap-10 text-xl">
      {sections.map((section) => (
        <RouterLink
          key={section.key}
          to={section.path}
          className="flex items-center gap-2"
        >
          <ChevronRight />
          {section.title}
        </RouterLink>
      ))}
    </div>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()
  const roleName = currentUser?.role?.name
  if (isFieldEmployeeRole(roleName)) {
    return <FieldEmployee />
  }

  return <SectionsDashboard roleName={roleName} />
}
