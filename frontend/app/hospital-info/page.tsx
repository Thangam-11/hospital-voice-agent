"use client";

import { PatientHome } from "@/components/patient/PatientHome";
import { HospitalInfoPanel } from "@/components/public/hospital-info-panel";

export default function HospitalInfoPage() {
  return (
    <PatientHome>
      <HospitalInfoPanel />
    </PatientHome>
  );
}
