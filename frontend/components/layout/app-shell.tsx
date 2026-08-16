import Header from "@/components/layout/header";
import Sidebar from "@/components/layout/sidebar";

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <div className="flex-1">
        <Header title={title} subtitle={subtitle} />
        <main className="p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
