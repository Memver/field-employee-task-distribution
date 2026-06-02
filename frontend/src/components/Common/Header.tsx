import { Link as RouterLink, useRouterState } from "@tanstack/react-router"

import { User } from "@/components/Sidebar/User"
import { getSidebarSections } from "@/features/navigation/roleSections"
import useAuth from "@/hooks/useAuth"
import { cn } from "@/lib/utils"

export function Header() {
  const { user: currentUser } = useAuth()
  const router = useRouterState()
  const currentPath = router.location.pathname
  const sections = getSidebarSections(currentUser?.role?.name)

  return (
    <header className="sticky top-0 z-[1000] h-16 shrink-0 border-b bg-background/95 px-4 backdrop-blur">
      <div className="mx-auto flex h-full max-w-7xl items-center gap-4">
        <nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto">
          {sections.map((section) => {
            const Icon = section.icon
            const isActive = currentPath === section.path

            return (
              <RouterLink
                key={section.key}
                to={section.path}
                className={cn(
                  "flex h-9 shrink-0 items-center gap-2 rounded-md px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
                  isActive && "bg-accent text-accent-foreground",
                )}
              >
                <Icon className="size-4" />
                <span>{section.title}</span>
              </RouterLink>
            )
          })}
        </nav>
        <User user={currentUser} />
      </div>
    </header>
  )
}
