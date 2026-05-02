import { useMutation, useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { TasksService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddTask from "@/components/Task/AddTask"
import { columns, type TaskTableData } from "@/components/Task/columns"
import { getAdminTasksQueryOptions } from "@/features/tasks/queries"
import useAuth from "@/hooks/useAuth"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
})

function Tasks() {
  const { user: currentUser } = useAuth()
  const isEmployeeManager = currentUser?.role?.name === "EMPLOYEE_MANAGER"
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data } = useSuspenseQuery(getAdminTasksQueryOptions())
  const tableData: TaskTableData[] = data.data

  const distributeTasksMutation = useMutation({
    mutationFn: TasksService.distributeTasks,
    onSuccess: () => {
      showSuccessToast("Задачи успешно распределены")
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.admin })
    },
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Задачи</h1>
          <p className="text-muted-foreground">Управление задачами</p>
        </div>
        <div className="flex items-center gap-3">
          {isEmployeeManager && (
            <LoadingButton
              loading={distributeTasksMutation.isPending}
              onClick={() => distributeTasksMutation.mutate()}
              className="bg-[#FF4B5F] text-white hover:bg-[#E54457]"
            >
              {distributeTasksMutation.isPending
                ? "Распределение..."
                : "Распределить задачи"}
            </LoadingButton>
          )}
          <AddTask />
        </div>
      </div>
      <DataTable columns={columns} data={tableData} />
    </div>
  )
}
