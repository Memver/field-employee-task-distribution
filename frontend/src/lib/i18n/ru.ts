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

const gradeLabels: Record<string, string> = {
  JUNIOR: "Младший",
  MIDDLE: "Средний",
  SENIOR: "Старший",
}

const priorityLabels: Record<string, string> = {
  LOW: "Низкий",
  MIDDLE: "Средний",
  HIGH: "Высокий",
}

const taskStatusLabels: Record<string, string> = {
  ASSIGNED: "Назначена",
  COMPLETED: "Выполнена",
  SKIPPED: "Пропущена",
}

const taskTypeLabels: Record<string, string> = {
  SALES_STIMULATION: "Стимулирование продаж",
  AGENT_TRAINING: "Обучение агента",
  CARDS_DELIVERY: "Доставка карт",
}

const eventTypeLabels: Record<string, string> = {
  cards_delivery_status_changed: "Изменение статуса доставки карт",
  approved_applications_changed: "Изменение одобренных заявок",
  cards_gived_changed: "Изменение выданных карт",
}

const metricLabels: Record<string, string> = {
  is_cards_delivered: "Карты доставлены",
  approved_applications: "Одобренные заявки",
  cards_gived: "Выдано карт",
}

export function formatGradeName(name: string | undefined): string {
  if (!name) return "—"
  return gradeLabels[name] ?? name
}

export function formatPriorityName(name: string | undefined): string {
  if (!name) return "—"
  return priorityLabels[name] ?? name
}

export function formatTaskStatusName(name: string | undefined): string {
  if (!name) return "—"
  return taskStatusLabels[name] ?? name
}

export function formatTaskTypeName(name: string | undefined): string {
  if (!name) return "—"
  return taskTypeLabels[name] ?? name
}

export function formatEventTypeName(name: string | undefined): string {
  if (!name) return "—"
  return eventTypeLabels[name] ?? name
}

export function formatMetricName(name: string | undefined): string {
  if (!name) return "—"
  return metricLabels[name] ?? name
}

export function formatBoolean(value: boolean | null | undefined): string {
  if (value == null) return "—"
  return value ? "Да" : "Нет"
}

export function formatApManagerVerdict(
  confirmed: boolean | null | undefined,
): string {
  if (confirmed == null) return "Вердикт ещё не назначен"
  return confirmed ? "Подтверждено" : "Отклонено"
}

export const validation = {
  required: "Обязательное поле",
  invalidDateTime: "Укажите корректные дату и время",
  invalidNumber: "Укажите корректное число",
  invalidEmail: "Некорректный email",
  passwordRequired: "Введите пароль",
  passwordConfirmRequired: "Подтвердите пароль",
  passwordMin: "Пароль должен быть не короче 8 символов",
  passwordsMismatch: "Пароли не совпадают",
}

export const roleSelectOptions = Object.entries(roleLabels).map(
  ([value, label]) => ({ value, label }),
)

export const apmVerdictOptions = [
  { value: "pending", label: "Вердикт ещё не назначен" },
  { value: "confirmed", label: "Подтверждено" },
  { value: "rejected", label: "Отклонено" },
] as const

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
  myAgentPoints: pageTitle("Мои агентские точки"),
  agentPointEvents: pageTitle("События агентских точек"),
  myAgentPointEvents: pageTitle("Мои события"),
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

export const toastTitles = {
  success: "Успешно",
  error: "Ошибка",
}

export const dateTime = {
  hour: "Часы",
  minute: "Минуты",
  hourPlaceholder: "ЧЧ",
  minutePlaceholder: "ММ",
}

export const toasts = {
  taskCreated: "Задача создана",
  taskUpdated: "Задача обновлена",
  taskDeleted: "Задача удалена",
  taskVerdictSaved: "Вердикт сохранён",
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
  agentPointEventCreated: "Событие создано",
  agentPointEventUpdated: "Событие обновлено",
  agentPointEventDeleted: "Событие удалено",
  itemCreated: "Элемент создан",
  itemUpdated: "Элемент обновлён",
  itemDeleted: "Элемент удалён",
  distributeSuccess: "Распределение завершено",
  passwordUpdated: "Пароль обновлён",
  passwordRecoverySent: "Письмо для восстановления пароля отправлено",
  accountDeleted: "Аккаунт удалён",
  profileUpdated: "Данные обновлены",
  taskStatusUpdatedField: "Статус задачи обновлён",
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

export const eventTypeOptions = [
  {
    value: "cards_delivery_status_changed",
    metric: "is_cards_delivered",
    valueKind: "bool" as const,
  },
  {
    value: "approved_applications_changed",
    metric: "approved_applications",
    valueKind: "num" as const,
  },
  {
    value: "cards_gived_changed",
    metric: "cards_gived",
    valueKind: "num" as const,
  },
]
