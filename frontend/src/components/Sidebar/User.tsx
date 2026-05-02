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
    <div
      className="flex items-center justify-end gap-2.5 w-full min-w-0"
      onClick={onClick}
    >
      <div className="flex flex-col items-start min-w-0">
        <p className="text-sm font-medium truncate w-full opacity-70">
          {`${surname} ${name} ${middle_name}`}
        </p>
        <p className="text-xs truncate w-full opacity-70">{role_name}</p>
      </div>
      <Avatar className="size-7">
        <AvatarFallback className="bg-blue-400 text-white" />
      </Avatar>
    </div>
  )
}

export function User({ user }: { user: any }) {
  const { logout } = useAuth()
  const handleLogout = async () => {
    logout()
  }

  console.log(user)

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
