import useAuth from "@/hooks/useAuth";
import { User } from "@/components/Sidebar/User";

export function Header() {
  const currentYear = new Date().getFullYear();

  const { user: currentUser } = useAuth();
  return (
    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-end gap-2 px-4">
      <User user={currentUser} />
    </header>
  );
}
