import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type AgentPointCreate, AgentPointsService } from "@/client"
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
  DialogTrigger,
} from "@/components/ui/dialog"
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
import { useAgentPointFormOptions } from "@/features/agentPoints/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import { fromDateTimeLocalToUtcIso } from "@/lib/dateTimeUtc"
import { toasts, validation } from "@/lib/i18n/ru"
import { handleError } from "@/utils"

const formSchema = z.object({
  created_time: z.string().min(1, { message: validation.required }),
  is_cards_delivered: z.boolean(),
  days_since_last_card_gived: z.coerce.number().int().nonnegative(),
  approved_applications: z.coerce.number().int().nonnegative(),
  cards_gived: z.coerce.number().int().nonnegative(),
  location_id: z.coerce.number().int().positive(),
})

type FormData = z.output<typeof formSchema>

const AddUser = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useAgentPointFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { is_cards_delivered: false },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: AgentPointCreate) =>
      AgentPointsService.createAgentPoint({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.agentPointCreated)
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["agent-points"] })
    },
  })

  const onSubmit = (data: FormData) => {
    const created_time = fromDateTimeLocalToUtcIso(data.created_time)
    if (!created_time) {
      showErrorToast(validation.invalidDateTime)
      return
    }
    mutation.mutate({ ...data, created_time })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Добавить точку
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Добавить агентскую точку</DialogTitle>
          <DialogDescription>Заполните форму новой точки.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="created_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Создано</FormLabel>
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
                name="is_cards_delivered"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Карты доставлены</FormLabel>
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
              <FormField
                control={form.control}
                name="days_since_last_card_gived"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Дней с последней выдачи</FormLabel>
                    <FormControl>
                      <Input placeholder="0" type="number" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="approved_applications"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Одобренные заявки</FormLabel>
                    <FormControl>
                      <Input placeholder="0" type="number" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="cards_gived"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Выдано карт</FormLabel>
                    <FormControl>
                      <Input placeholder="0" type="number" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="location_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Локация</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.locationOptions}
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
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
  )
}

export default AddUser
