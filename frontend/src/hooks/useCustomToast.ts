import { toast } from "sonner"
import { toastTitles } from "@/lib/i18n/ru"

const useCustomToast = () => {
  const showSuccessToast = (description: string) => {
    toast.success(toastTitles.success, {
      description,
    })
  }

  const showErrorToast = (description: string) => {
    toast.error(toastTitles.error, {
      description,
    })
  }

  return { showSuccessToast, showErrorToast }
}

export default useCustomToast
