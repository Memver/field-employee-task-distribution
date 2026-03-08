import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import useAuth from "@/hooks/useAuth"

interface UserInfoProps {
  name?: string
  surname?: string
  middle_name?: string
  role?: string
}

function UserInfo({ name, surname, middle_name, role }: UserInfoProps) {
  return (
    <div className="flex items-center justify-end gap-2.5 w-full min-w-0">
      <div className="flex flex-col items-start min-w-0">
        <p className="text-sm font-medium truncate w-full opacity-70">
          {`${name} ${surname} ${middle_name}`}
        </p>
        <p className="text-xs truncate w-full opacity-70">{role}</p>
      </div>
      <Avatar className="size-8">
        <AvatarFallback className="bg-blue-400 text-white" />
      </Avatar>
    </div>
  )
}

export function User({ user }: { user: any }) {
  const { logout } = useAuth()

  console.log(user)

  if (!user) return null

  return (
    <UserInfo
      name={user?.name}
      surname={user?.surname}
      middle_name={user?.middle_name}
      role={user?.role}
    />
  )
}
