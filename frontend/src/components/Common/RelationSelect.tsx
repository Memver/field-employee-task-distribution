import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export type RelationOption<T> = {
  value: string
  label: string
  item: T
}

type RelationSelectProps = {
  value: string
  onChange: (value: string) => void
  options: RelationOption<unknown>[]
  placeholder?: string
  disabled?: boolean
}

export function RelationSelect({
  value,
  onChange,
  options,
  placeholder = "Выберите значение",
  disabled = false,
}: RelationSelectProps) {
  return (
    <Select
      value={value || undefined}
      onValueChange={onChange}
      disabled={disabled}
    >
      <SelectTrigger className="w-full">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function toSelectOptions<T>(
  items: T[],
  getValue: (item: T) => number | string,
  getLabel: (item: T) => string,
): RelationOption<T>[] {
  return items.map((item) => ({
    value: String(getValue(item)),
    label: getLabel(item),
    item,
  }))
}
