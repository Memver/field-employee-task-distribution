export const queryKeys = {
  users: {
    all: ["users"] as const,
  },
  tasks: {
    all: ["tasks"] as const,
    admin: ["tasks-admin"] as const,
  },
  items: {
    all: ["items"] as const,
  },
  taskTypes: {
    all: ["task-types"] as const,
  },
  taskStatuses: {
    all: ["task-statuses"] as const,
  },
  employees: {
    all: ["employees"] as const,
  },
  locations: {
    all: ["locations"] as const,
  },
  agentPoints: {
    all: ["agent-points"] as const,
  },
  grades: {
    all: ["grades"] as const,
  },
  priorities: {
    all: ["priorities"] as const,
  },
  roles: {
    all: ["roles"] as const,
  },
  currentUser: {
    all: ["currentUser"] as const,
  },
}
