@'
"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { isAuthenticated } from "@/lib/api/auth";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else {
      setChecked(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] text-sm text-slate-400">
        Checking session…
      </div>
    );
  }

  return <>{children}</>;
}
'@ | Set-Content components\admin\ProtectedRoute.tsx