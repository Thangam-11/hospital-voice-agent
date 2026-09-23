import { ProtectedRoute } from "@/components/admin/ProtectedRoute";
import Header from "@/components/layout/header";
import Sidebar from "@/components/layout/sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <div className="flex-1">
          <Header />
          <main className="p-6 lg:p-8">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
