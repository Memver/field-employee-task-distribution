import { User } from "@/components/Sidebar/User"
import useAuth from "@/hooks/useAuth"

export function Header() {
  const _currentYear = new Date().getFullYear()

  const { user: currentUser } = useAuth()
  return (
    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-end gap-2 px-4">
      <User user={currentUser} />
    </header>
  )
}
