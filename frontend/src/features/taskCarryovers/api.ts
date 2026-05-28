import type { Message } from "@/client"
import { OpenAPI } from "@/client"
import type {
  TaskCarryoverCreate,
  TaskCarryoverPublic,
  TaskCarryoversPublic,
  TaskCarryoverUpdate,
} from "./types"

function authHeaders() {
  const token = localStorage.getItem("access_token")
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  }
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${OpenAPI.BASE}${url}`, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
  })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const TaskCarryoversApi = {
  readTaskCarryovers: (skip = 0, limit = 100) =>
    requestJson<TaskCarryoversPublic>(
      `/api/v1/task-carryovers/?skip=${skip}&limit=${limit}`,
      { method: "GET" },
    ),
  createTaskCarryover: (requestBody: TaskCarryoverCreate) =>
    requestJson<TaskCarryoverPublic>(`/api/v1/task-carryovers/`, {
      method: "POST",
      body: JSON.stringify(requestBody),
    }),
  updateTaskCarryover: (
    taskCarryoverId: number,
    requestBody: TaskCarryoverUpdate,
  ) =>
    requestJson<TaskCarryoverPublic>(
      `/api/v1/task-carryovers/${taskCarryoverId}`,
      {
        method: "PUT",
        body: JSON.stringify(requestBody),
      },
    ),
  deleteTaskCarryover: (taskCarryoverId: number) =>
    requestJson<Message>(`/api/v1/task-carryovers/${taskCarryoverId}`, {
      method: "DELETE",
    }),
}
