export const APP_NAME = "Диплом"

export const roleLabels: Record<string, string> = {
  ADMIN: "Администратор",
  EMPLOYEE_MANAGER: "Менеджер сотрудников",
  FIELD_EMPLOYEE: "Выездной сотрудник",
  AGENT_POINT_MANAGER: "Менеджер агентской точки",
}

export function formatRoleName(roleName: string | undefined): string {
  if (!roleName) return "—"
  return roleLabels[roleName] ?? roleName
}

export function pageTitle(page: string): string {
  return `${page} — ${APP_NAME}`
}

export const pageTitles = {
  dashboard: pageTitle("Главная"),
  tasks: pageTitle("Задачи"),
  employees: pageTitle("Сотрудники"),
  users: pageTitle("Пользователи"),
  roles: pageTitle("Роли"),
  grades: pageTitle("Грейды"),
  locations: pageTitle("Локации"),
  priorities: pageTitle("Приоритеты"),
  taskStatuses: pageTitle("Статусы задач"),
  taskTypes: pageTitle("Типы задач"),
  agentPoints: pageTitle("Агентские точки"),
  agentPointEvents: pageTitle("События агентских точек"),
  items: pageTitle("Элементы"),
  settings: pageTitle("Настройки"),
  login: pageTitle("Вход"),
  signup: pageTitle("Регистрация"),
  recoverPassword: pageTitle("Восстановление пароля"),
  resetPassword: pageTitle("Сброс пароля"),
  fieldEmployee: pageTitle("Мои задачи"),
}

export const emptyTable = {
  defaultTitle: "Нет данных",
  defaultDescription: "Записи не найдены",
  tasks: "Задач пока нет",
  employees: "Сотрудников не найдено",
  users: "Пользователей не найдено",
  roles: "Ролей не найдено",
  grades: "Грейдов не найдено",
  locations: "Локаций не найдено",
  priorities: "Приоритетов не найдено",
  taskStatuses: "Статусов не найдено",
  taskTypes: "Типов задач не найдено",
  agentPoints: "Агентских точек не найдено",
  agentPointEvents: "Событий не найдено",
  items: "Элементов не найдено",
}

export const toasts = {
  taskCreated: "Задача создана",
  taskUpdated: "Задача обновлена",
  taskDeleted: "Задача удалена",
  employeeCreated: "Сотрудник создан",
  employeeUpdated: "Сотрудник обновлён",
  employeeDeleted: "Сотрудник удалён",
  userCreated: "Пользователь создан",
  userUpdated: "Пользователь обновлён",
  userDeleted: "Пользователь удалён",
  roleCreated: "Роль создана",
  roleUpdated: "Роль обновлена",
  roleDeleted: "Роль удалена",
  gradeCreated: "Грейд создан",
  gradeUpdated: "Грейд обновлён",
  gradeDeleted: "Грейд удалён",
  locationCreated: "Локация создана",
  locationUpdated: "Локация обновлена",
  locationDeleted: "Локация удалена",
  priorityCreated: "Приоритет создан",
  priorityUpdated: "Приоритет обновлён",
  priorityDeleted: "Приоритет удалён",
  taskStatusCreated: "Статус создан",
  taskStatusUpdated: "Статус обновлён",
  taskStatusDeleted: "Статус удалён",
  taskTypeCreated: "Тип задачи создан",
  taskTypeUpdated: "Тип задачи обновлён",
  taskTypeDeleted: "Тип задачи удалён",
  agentPointCreated: "Агентская точка создана",
  agentPointUpdated: "Агентская точка обновлена",
  agentPointDeleted: "Агентская точка удалена",
  itemCreated: "Элемент создан",
  itemUpdated: "Элемент обновлён",
  itemDeleted: "Элемент удалён",
  distributeSuccess: "Распределение завершено",
}

export const nav = {
  dashboard: "Главная",
}

export const pagination = {
  rowsPerPage: "Строк на странице",
  page: "Страница",
  of: "из",
  rowsSelected: "строк выбрано",
}

export const settingsTabs = {
  myProfile: "Мой профиль",
  password: "Пароль",
  dangerZone: "Опасная зона",
}
