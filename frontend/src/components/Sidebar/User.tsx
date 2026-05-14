import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import useAuth from "@/hooks/useAuth"

interface UserInfoProps {
  name?: string
  surname?: string
  middle_name?: string
  role_name?: string
  onClick?: () => void
}

function UserInfo({
  name,
  surname,
  middle_name,
  role_name,
  onClick,
}: UserInfoProps) {
  return (
    <button
      type="button"
      className="flex max-w-[2.5in] shrink-0 cursor-pointer items-center justify-end gap-2.5 rounded-md border-0 bg-transparent px-2 py-1 text-left hover:bg-accent"
      onClick={onClick}
    >
      <div className="flex min-w-0 flex-1 flex-col items-start">
        <p className="text-sm font-medium truncate w-full opacity-70">
          {`${surname} ${name} ${middle_name}`}
        </p>
        <p className="text-xs truncate w-full opacity-70">{role_name}</p>
      </div>
      <Avatar className="size-7">
        <AvatarFallback className="bg-blue-400 text-white" />
      </Avatar>
    </button>
  )
}

export function User({ user }: { user: any }) {
  const { logout } = useAuth()
  const handleLogout = async () => {
    logout()
  }

  if (!user) return null

  return (
    <UserInfo
      onClick={handleLogout}
      name={user?.name}
      surname={user?.surname}
      middle_name={user?.middle_name}
      role_name={user?.role.name}
    />
  )
}
