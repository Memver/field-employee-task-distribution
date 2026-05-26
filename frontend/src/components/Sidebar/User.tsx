import { LogOut } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useAuth from "@/hooks/useAuth"
import { formatRoleName } from "@/lib/i18n/ru"

interface UserInfoProps {
  name?: string
  surname?: string
  middle_name?: string
  role_name?: string
}

function UserInfo({ name, surname, middle_name, role_name }: UserInfoProps) {
  return (
    <div className="flex max-w-[2.5in] shrink-0 items-center justify-end gap-2.5 px-2 py-1 text-left">
      <div className="flex min-w-0 flex-1 flex-col items-start">
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

  if (!user) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="cursor-pointer rounded-md border-0 bg-transparent hover:bg-accent"
        >
          <UserInfo
            name={user?.name}
            surname={user?.surname}
            middle_name={user?.middle_name}
            role_name={formatRoleName(user?.role?.name)}
          />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          onSelect={(event) => {
            event.preventDefault()
            logout()
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Выйти
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
