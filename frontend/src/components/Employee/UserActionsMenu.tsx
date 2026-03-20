import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { EmployeePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteUser from "./DeleteUser"
import EditUser from "./EditUser"

interface UserActionsMenuProps {
  employee: EmployeePublic
}

export const UserActionsMenu = ({ employee }: UserActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditUser employee={employee} onSuccess={() => setOpen(false)} />
        <DeleteUser id={employee.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

