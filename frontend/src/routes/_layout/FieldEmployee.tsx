import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import { useSuspenseQuery } from "@tanstack/react-query"
import L from "leaflet"
import icon from "leaflet/dist/images/marker-icon.png"
import iconShadow from "leaflet/dist/images/marker-shadow.png"
import { useEffect, useMemo, useState } from "react"
import { renderToString } from "react-dom/server"
import { EmptyState } from "@/components/Common/EmptyState"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useUpdateMyTaskStatusMutation } from "@/features/tasks/mutations"
import {
  getFieldEmployeeTasksQueryOptions,
  getTaskStatusesQueryOptions,
} from "@/features/tasks/queries"
import useCustomToast from "@/hooks/useCustomToast"

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

function createNumberedIcon(index: number) {
  // Создаем HTML для кастомного маркера
  const html = renderToString(
    <div className="relative">
      {/* Стандартный маркер Leaflet */}
      <img src={icon} alt="marker" className="w-6 h-10 brightness-0" />
      {/* Номер поверх маркера */}
      <div className="absolute top-1 left-1/2 transform -translate-x-1/2 text-white font-bold text-xs bg-black rounded-full w-4 h-4 flex items-center justify-center">
        {index}
      </div>
    </div>,
  )

  // Создаем divIcon с кастомным HTML
  return L.divIcon({
    html: html,
    className: "custom-marker", // пустой класс, чтобы не добавлять лишние стили
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41],
  })
}

function isValidCoordinatePair(point: unknown): point is [number, number] {
  return (
    Array.isArray(point) &&
    point.length >= 2 &&
    typeof point[0] === "number" &&
    Number.isFinite(point[0]) &&
    typeof point[1] === "number" &&
    Number.isFinite(point[1])
  )
}

function normalizeRoute(route: unknown): [number, number][] {
  if (!Array.isArray(route)) {
    return []
  }
  // Backend returns points as [lon, lat], Leaflet expects [lat, lon].
  return route.filter(isValidCoordinatePair).map(([lon, lat]) => [lat, lon])
}
export function FieldEmployee() {
  const { showErrorToast } = useCustomToast()
  const { data } = useSuspenseQuery(getFieldEmployeeTasksQueryOptions())
  const { data: taskStatuses } = useSuspenseQuery(getTaskStatusesQueryOptions())
  const updateMyTaskStatusMutation = useUpdateMyTaskStatusMutation()
  const [taskForms, setTaskForms] = useState<
    Record<number, { comment: string; task_status_id: string }>
  >({})

  const hasValidStartLocation =
    !!data &&
    !!data.start_location &&
    typeof data.start_location.lat === "number" &&
    Number.isFinite(data.start_location.lat) &&
    typeof data.start_location.lon === "number" &&
    Number.isFinite(data.start_location.lon)

  if (!data || !data.tasks || !hasValidStartLocation) {
    return (
      <div className="h-screen flex items-center justify-center">
        <EmptyState
          title="Нет данных о маршруте"
          description="Информация о начальной точке отсутствует"
        />
      </div>
    )
  }

  const position = [data.start_location.lat, data.start_location.lon]

  const routePoints = normalizeRoute(data.route)
  const hasTasks = data.tasks.length > 0
  const hasValidRoute = routePoints.length >= 2
  const statusesById = useMemo(
    () => new Map(taskStatuses.data.map((status) => [status.id, status.name])),
    [taskStatuses.data],
  )

  useEffect(() => {
    setTaskForms((previousForms) => {
      const nextForms: Record<number, { comment: string; task_status_id: string }> = {}
      for (const task of data.tasks) {
        nextForms[task.id] = {
          comment: previousForms[task.id]?.comment ?? task.comment ?? "",
          task_status_id: previousForms[task.id]?.task_status_id ?? "",
        }
      }

      const previousKeys = Object.keys(previousForms)
      const nextKeys = Object.keys(nextForms)
      if (previousKeys.length !== nextKeys.length) {
        return nextForms
      }

      for (const key of nextKeys) {
        const taskId = Number(key)
        const prev = previousForms[taskId]
        const next = nextForms[taskId]
        if (!prev || prev.comment !== next.comment || prev.task_status_id !== next.task_status_id) {
          return nextForms
        }
      }

      return previousForms
    })
  }, [data.tasks])

  if (!hasTasks && !hasValidRoute) {
    return (
      <div className="h-screen flex items-center justify-center">
        <EmptyState
          title="Нет данных о маршруте"
          description="Для сотрудника пока нет назначенных задач"
        />
      </div>
    )
  }

  // Опции для линии маршрута
  const routeOptions = {
    color: "#1de81c", // синий цвет
    weight: 4,
    opacity: 0.7,
    lineCap: "round" as const,
    lineJoin: "round" as const,
  }

  const handleTaskFieldChange = (
    taskId: number,
    field: "comment" | "task_status_id",
    value: string,
  ) => {
    setTaskForms((previousForms) => ({
      ...previousForms,
      [taskId]: {
        comment: previousForms[taskId]?.comment ?? "",
        task_status_id: previousForms[taskId]?.task_status_id ?? "",
        [field]: value,
      },
    }))
  }

  const getStatusName = (taskId: number): string => {
    const formStatusId = Number(taskForms[taskId]?.task_status_id)
    if (formStatusId && statusesById.has(formStatusId)) {
      return statusesById.get(formStatusId) ?? "Не выбран"
    }

    return "Не выбран"
  }

  const saveTaskChanges = (taskId: number) => {
    const formData = taskForms[taskId]
    const statusId = Number(formData?.task_status_id)

    if (!statusId) {
      showErrorToast("Выберите новый статус перед сохранением")
      return
    }

    updateMyTaskStatusMutation.mutate({
      taskId,
      requestBody: {
        comment: formData.comment.trim() ? formData.comment : null,
        task_status_id: statusId,
      },
    })
  }

  return (
    <div>
      <style>
        {`
          .leaflet-attribution-flag {
            display: none !important;
          }
        `}
      </style>
      <div className="flex flex-col items-start gap-4">
        <div className="flex justify-center w-full gap-6 flex-wrap">
          <div
            className="rounded-xl overflow-hidden shadow-lg"
            style={{ height: "600px", width: "326px", marginTop: "20px" }}
          >
            <MapContainer
              style={{ height: "100%", width: "100%" }}
              center={position}
              zoom={12}
              scrollWheelZoom={false}
            >
              <TileLayer
                attribution='<a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {hasValidRoute && (
                <Polyline positions={routePoints} pathOptions={routeOptions} />
              )}
              {data.tasks.map((task, index) => (
                <Marker
                  key={task.id}
                  position={[
                    task.agent_point.location.lat,
                    task.agent_point.location.lon,
                  ]}
                  icon={createNumberedIcon(index + 1)}
                >
                  <Popup>
                    <div className="space-y-1">
                      <div className="font-semibold">
                        Задача #{task.id || "Не указано"}
                      </div>
                      <div className="text-xs">
                        Статус: <span className="font-medium">{getStatusName(task.id)}</span>
                      </div>
                      <div className="text-xs">
                        Комментарий:{" "}
                        <span className="font-medium">
                          {taskForms[task.id]?.comment || task.comment || "Нет комментария"}
                        </span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}

              <Marker position={position} icon={createNumberedIcon(0)} />
            </MapContainer>
          </div>
          <div className="w-full max-w-xl space-y-4 mt-5">
            <h2 className="text-xl font-semibold">Мои задачи</h2>
            {data.tasks.map((task) => (
              <div key={task.id} className="rounded-xl border p-4 space-y-3">
                <div className="space-y-1">
                  <div className="font-semibold">Задача #{task.id}</div>
                  <div className="text-sm text-muted-foreground">
                    Текущий статус: {getStatusName(task.id)}
                  </div>
                </div>
                <Select
                  value={taskForms[task.id]?.task_status_id ?? ""}
                  onValueChange={(value) =>
                    handleTaskFieldChange(task.id, "task_status_id", value)
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Выберите статус" />
                  </SelectTrigger>
                  <SelectContent>
                    {taskStatuses.data.map((status) => (
                      <SelectItem key={status.id} value={String(status.id)}>
                        {status.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  value={taskForms[task.id]?.comment ?? ""}
                  placeholder="Комментарий к задаче"
                  onChange={(event) =>
                    handleTaskFieldChange(task.id, "comment", event.target.value)
                  }
                />
                <LoadingButton
                  loading={
                    updateMyTaskStatusMutation.isPending &&
                    updateMyTaskStatusMutation.variables?.taskId === task.id
                  }
                  onClick={() => saveTaskChanges(task.id)}
                >
                  Сохранить изменения
                </LoadingButton>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
