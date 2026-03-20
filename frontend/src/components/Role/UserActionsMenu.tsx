import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { RolePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteUser from "./DeleteRole"
import EditUser from "./EditUser"

interface UserActionsMenuProps {
  role: RolePublic
}

export const UserActionsMenu = ({ role }: UserActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditUser role={role} onSuccess={() => setOpen(false)} />
        <DeleteUser id={role.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
