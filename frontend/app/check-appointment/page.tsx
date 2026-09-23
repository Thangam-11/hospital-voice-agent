"use client";

import { useRouter } from "next/navigation";

import { PatientHome } from "@/components/patient/PatientHome";
import { CheckAppointmentModal } from "@/components/public/check-appointment-modal";

export default function CheckAppointmentPage() {
  const router = useRouter();

  return (
    <PatientHome>
      <CheckAppointmentModal onClose={() => router.push("/")} />
    </PatientHome>
  );
}
