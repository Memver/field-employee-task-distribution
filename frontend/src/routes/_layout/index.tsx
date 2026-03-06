import { createFileRoute } from "@tanstack/react-router";

import useAuth from "@/hooks/useAuth";
import { LoadingButton } from "@/components/ui/loading-button";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Cloud",
      },
    ],
  }),
});

function Dashboard() {
  const { user: currentUser } = useAuth();

  return (
    <div>
      <div className="flex flex-col items-start gap-4">
        <h1 className="text-2xl truncate max-w-sm opacity-70 text-[#001F5A]">
          Сотрудники
        </h1>
        <div>"Карусель сотрудников"</div>
        <LoadingButton type="submit">Сформировать отчет</LoadingButton>
      </div>
    </div>
  );
}
