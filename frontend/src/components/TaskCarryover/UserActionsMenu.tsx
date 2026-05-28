import { EllipsisVertical } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { TaskCarryoverPublic } from "@/features/taskCarryovers/types"
import DeleteTaskCarryover from "./DeleteTaskCarryover"
import EditTaskCarryover from "./EditTaskCarryover"

type Props = {
  taskCarryover: TaskCarryoverPublic
}

export function UserActionsMenu({ taskCarryover }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditTaskCarryover
          taskCarryover={taskCarryover}
          onSuccess={() => setOpen(false)}
        />
        <DeleteTaskCarryover
          id={taskCarryover.id}
          onSuccess={() => setOpen(false)}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
