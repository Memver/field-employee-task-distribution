import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type AgentPointEventPublic,
  AgentPointEventsService,
  type AgentPointEventUpdate,
} from "@/client"
import { DateTimeField } from "@/components/Common/DateTimeField"
import { RelationSelect } from "@/components/Common/RelationSelect"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useAgentPointEventFormOptions } from "@/features/agentPointEvents/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import {
  eventTypeOptions,
  formatEventTypeName,
  toasts,
  validation,
} from "@/lib/i18n/ru"
import { fromDateTimeLocalToUtcIso, toDateTimeLocalUtc } from "@/lib/dateTimeUtc"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

const formSchema = z.object({
  agent_point_id: z.number().int().positive(),
  event_time: z.string().min(1, { message: validation.required }),
  event_type: z.string().min(1),
  metric_value_bool: z.boolean().optional(),
  metric_value_num: z.number().int().optional(),
})

type FormData = z.output<typeof formSchema>

interface EditUserProps {
  event: AgentPointEventPublic
  onSuccess: () => void
}

const EditUser = ({ event, onSuccess }: EditUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useAgentPointEventFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agent_point_id: event.agent_point_id,
      event_time: toDateTimeLocalUtc(event.event_time),
      event_type: event.event_type,
      metric_value_bool: event.metric_value_bool ?? false,
      metric_value_num: event.metric_value_num ?? 0,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const selectedEventType = form.watch("event_type")
  const eventConfig =
    eventTypeOptions.find((item) => item.value === selectedEventType) ??
    eventTypeOptions[0]

  useEffect(() => {
    if (eventConfig.valueKind === "bool") {
      form.setValue("metric_value_num", undefined)
    } else {
      form.setValue("metric_value_bool", undefined)
    }
  }, [eventConfig.valueKind, form])

  const mutation = useMutation({
    mutationFn: (data: AgentPointEventUpdate) =>
      AgentPointEventsService.updateAgentPointEvent({
        id: event.id,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast(toasts.agentPointEventUpdated)
      onSuccess()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agentPointEvents.all })
    },
  })

  const onSubmit = (data: FormData) => {
    const payload: AgentPointEventUpdate = {
      agent_point_id: data.agent_point_id,
      event_time: fromDateTimeLocalToUtcIso(data.event_time),
      event_type: data.event_type,
      metric_name: eventConfig.metric,
      metric_delta: null,
      metric_value_num:
        eventConfig.valueKind === "num" ? (data.metric_value_num ?? 0) : null,
      metric_value_bool:
        eventConfig.valueKind === "bool" ? (data.metric_value_bool ?? false) : null,
    }
    mutation.mutate(payload)
  }

  return (
    <>
      <DropdownMenuItem
        onSelect={(e) => {
          e.preventDefault()
          setIsOpen(true)
        }}
      >
        <Pencil className="mr-2 h-4 w-4" />
        Редактировать
      </DropdownMenuItem>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Редактировать событие</DialogTitle>
            <DialogDescription>Измените данные события.</DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <div className="grid gap-4 py-4">
                <FormField
                  control={form.control}
                  name="agent_point_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Агентская точка</FormLabel>
                      <FormControl>
                        <RelationSelect
                          value={field.value ? String(field.value) : ""}
                          onChange={(v) => field.onChange(Number(v))}
                          options={options.agentPointOptions}
                          disabled={options.isLoading}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="event_time"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Время события</FormLabel>
                      <FormControl>
                        <DateTimeField
                          value={field.value}
                          onChange={field.onChange}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="event_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Тип события</FormLabel>
                      <Select value={field.value} onValueChange={field.onChange}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Выберите тип" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {eventTypeOptions.map((item) => (
                            <SelectItem key={item.value} value={item.value}>
                              {formatEventTypeName(item.value)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {eventConfig.valueKind === "bool" ? (
                  <FormField
                    control={form.control}
                    name="metric_value_bool"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Значение</FormLabel>
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={(v) => field.onChange(Boolean(v))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                ) : (
                  <FormField
                    control={form.control}
                    name="metric_value_num"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Значение</FormLabel>
                        <FormControl>
                          <Input type="number" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" disabled={mutation.isPending}>
                    Отменить
                  </Button>
                </DialogClose>
                <LoadingButton type="submit" loading={mutation.isPending}>
                  Сохранить
                </LoadingButton>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default EditUser
