import { useMutation, useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Loader2 } from "lucide-react"
import { useState } from "react"
import type { DistributionReportPublic } from "@/client"
import { TasksService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddTask from "@/components/Task/AddTask"
import { DistributionReportPanel } from "@/components/Task/DistributionReportPanel"
import { columns, type TaskTableData } from "@/components/Task/columns"
import { getAdminTasksQueryOptions } from "@/features/tasks/queries"
import useAuth from "@/hooks/useAuth"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { emptyTable, pageTitles, toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
  head: () => ({
    meta: [{ title: pageTitles.tasks }],
  }),
})

function Tasks() {
  const { user: currentUser } = useAuth()
  const isEmployeeManager = currentUser?.role?.name === "EMPLOYEE_MANAGER"
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data } = useSuspenseQuery(getAdminTasksQueryOptions())
  const tableData: TaskTableData[] = data.data
  const [distributionReport, setDistributionReport] =
    useState<DistributionReportPublic | null>(null)

  const distributeTasksMutation = useMutation({
    mutationFn: TasksService.distributeTasks,
    onSuccess: (report) => {
      setDistributionReport(report)
      showSuccessToast(toasts.distributeSuccess)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.admin })
    },
  })

  const isDistributing = distributeTasksMutation.isPending

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
              loading={isDistributing}
              disabled={isDistributing}
              onClick={() => distributeTasksMutation.mutate()}
              className="bg-[#FF4B5F] text-white hover:bg-[#E54457]"
            >
              {isDistributing ? "Распределение..." : "Распределить задачи"}
            </LoadingButton>
          )}
          <AddTask disabled={isDistributing} />
        </div>
      </div>

      {distributionReport && (
        <DistributionReportPanel report={distributionReport} />
      )}

      <div className="relative">
        {isDistributing && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 rounded-lg bg-background/80 backdrop-blur-sm">
            <Loader2 className="h-10 w-10 animate-spin text-[#FF4B5F]" />
            <p className="text-sm font-medium">Идёт распределение задач…</p>
          </div>
        )}
        <div
          className={cn(isDistributing && "pointer-events-none opacity-50")}
        >
          <DataTable
            columns={columns}
            data={tableData}
            emptyTitle={emptyTable.tasks}
          />
        </div>
      </div>
    </div>
  )
}
