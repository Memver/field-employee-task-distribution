import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { dateTime } from "@/lib/i18n/ru"
import { cn } from "@/lib/utils"

type DateTimeFieldProps = {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
  className?: string
}

const HOURS = Array.from({ length: 24 }, (_, index) =>
  String(index).padStart(2, "0"),
)
const MINUTES = Array.from({ length: 60 }, (_, index) =>
  String(index).padStart(2, "0"),
)

function splitDateTime(value: string): { date: string; hour: string; minute: string } {
  if (!value) {
    return { date: "", hour: "", minute: "" }
  }
  const [date, time] = value.split("T")
  const [hour = "", minute = ""] = (time ?? "").split(":")
  return {
    date: date ?? "",
    hour: hour.slice(0, 2),
    minute: minute.slice(0, 2),
  }
}

function joinDateTime(date: string, hour: string, minute: string): string {
  if (!date) {
    return ""
  }
  if (!hour && !minute) {
    return date
  }
  const normalizedHour = hour || "00"
  const normalizedMinute = minute || "00"
  return `${date}T${normalizedHour}:${normalizedMinute}`
}

export function DateTimeField({
  value,
  onChange,
  disabled = false,
  className,
}: DateTimeFieldProps) {
  const { date, hour, minute } = splitDateTime(value)

  const handleDateChange = (nextDate: string) => {
    onChange(joinDateTime(nextDate, hour, minute))
  }

  const handleHourChange = (nextHour: string) => {
    onChange(joinDateTime(date, nextHour, minute || "00"))
  }

  const handleMinuteChange = (nextMinute: string) => {
    onChange(joinDateTime(date, hour || "00", nextMinute))
  }

  return (
    <div lang="ru" className={cn("flex gap-2", className)}>
      <Input
        type="date"
        lang="ru-RU"
        value={date}
        disabled={disabled}
        onChange={(event) => handleDateChange(event.target.value)}
        className="min-w-0 flex-1"
      />
      <Select
        value={hour || undefined}
        onValueChange={handleHourChange}
        disabled={disabled || !date}
      >
        <SelectTrigger className="w-[5.5rem] shrink-0" aria-label={dateTime.hour}>
          <SelectValue placeholder={dateTime.hourPlaceholder} />
        </SelectTrigger>
        <SelectContent>
          {HOURS.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={minute || undefined}
        onValueChange={handleMinuteChange}
        disabled={disabled || !date}
      >
        <SelectTrigger className="w-[5.5rem] shrink-0" aria-label={dateTime.minute}>
          <SelectValue placeholder={dateTime.minutePlaceholder} />
        </SelectTrigger>
        <SelectContent>
          {MINUTES.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
