import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { AgentPointsService, type AgentPointPublic, type AgentPointUpdate } from "@/client"
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
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  created_time: z.string().min(1),
  is_cards_delivered: z.boolean(),
  days_since_last_card_gived: z.coerce.number().int().nonnegative(),
  approved_applications: z.coerce.number().int().nonnegative(),
  cards_gived: z.coerce.number().int().nonnegative(),
  location_id: z.coerce.number().int().positive(),
})

type FormData = z.infer<typeof formSchema>

interface EditUserProps {
  agentPoint: AgentPointPublic
  onSuccess: () => void
}

const EditUser = ({ agentPoint, onSuccess }: EditUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      created_time: agentPoint.created_time,
      is_cards_delivered: agentPoint.is_cards_delivered,
      days_since_last_card_gived: agentPoint.days_since_last_card_gived,
      approved_applications: agentPoint.approved_applications,
      cards_gived: agentPoint.cards_gived,
      location_id: agentPoint.location.id,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: AgentPointUpdate) =>
      AgentPointsService.updateAgentPoint({ id: agentPoint.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Agent point updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["agent-points"] }),
  })

  const onSubmit = (data: FormData) => mutation.mutate(data)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil /> Редактировать
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader><DialogTitle>Редактировать агентскую точку</DialogTitle><DialogDescription>Обновите данные точки</DialogDescription></DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField control={form.control} name="created_time" render={({ field }) => (
                <FormItem><FormLabel>Время создания (ISO)</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="is_cards_delivered" render={({ field }) => (
                <FormItem><FormLabel>Карты доставлены</FormLabel><FormControl><Checkbox checked={field.value} onCheckedChange={(v) => field.onChange(Boolean(v))} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="days_since_last_card_gived" render={({ field }) => (
                <FormItem><FormLabel>Дней с последней выдачи</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="approved_applications" render={({ field }) => (
                <FormItem><FormLabel>Одобренные заявки</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="cards_gived" render={({ field }) => (
                <FormItem><FormLabel>Выдано карт</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="location_id" render={({ field }) => (
                <FormItem><FormLabel>ID локации</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </div>
            <DialogFooter>
              <DialogClose asChild><Button variant="outline" disabled={mutation.isPending}>Отменить</Button></DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>Сохранить</LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default EditUser
