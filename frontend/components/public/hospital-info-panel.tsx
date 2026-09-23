import { Clock3, MapPin, Phone, ShieldCheck } from "lucide-react";

const SECTIONS = [
  {
    icon: Clock3,
    title: "Visiting Hours",
    body: "General wards: 10:00 AM – 12:00 PM and 5:00 PM – 7:00 PM daily. ICU visiting is restricted to immediate family, 2 visitors at a time.",
  },
  {
    icon: Phone,
    title: "Contact & Emergencies",
    body: "For emergencies, call our 24/7 toll-free line or come directly to the Emergency department, open around the clock.",
  },
  {
    icon: ShieldCheck,
    title: "Insurance & Billing",
    body: "We accept most major insurance providers. Please bring your insurance card and a valid ID at check-in. Billing questions can be directed to our front desk.",
  },
  {
    icon: MapPin,
    title: "Departments",
    body: "Cardiology, General Medicine, Neurology, Emergency, Surgery, Diagnostics, and Pediatrics are all available for appointment booking.",
  },
];

export function HospitalInfoPanel() {
  return (
    <div className="mx-auto w-full max-w-2xl">
      <h2 className="text-xl font-semibold text-slate-900">Hospital Info</h2>
      <p className="mt-1 text-sm text-slate-500">
        Common questions answered — for anything else, use Talk to AI.
      </p>

      <div className="mt-6 space-y-4">
        {SECTIONS.map((section) => {
          const Icon = section.icon;
          return (
            <div
              key={section.title}
              className="flex gap-4 rounded-xl border border-slate-200 bg-white p-5"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#0D9488]/10 text-[#0D9488]">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  {section.title}
                </h3>
                <p className="mt-1 text-sm text-slate-500">{section.body}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
