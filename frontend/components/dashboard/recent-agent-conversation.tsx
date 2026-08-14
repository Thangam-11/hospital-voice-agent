import {
  CalendarDays,
  CheckCircle2,
  Clock3,
  MessageSquare,
  PhoneCall,
} from "lucide-react";

const conversations = [
  {
    patient: "Ravi Kumar",
    type: "Appointment Booking",
    summary: "Requested a cardiology appointment",
    time: "2 min ago",
    duration: "03:24",
    status: "Completed",
  },
  {
    patient: "Priya Sharma",
    type: "Appointment Rescheduling",
    summary: "Requested to reschedule an appointment",
    time: "18 min ago",
    duration: "02:41",
    status: "Completed",
  },
  {
    patient: "Arun Singh",
    type: "Hospital Information",
    summary: "Asked about visiting hours",
    time: "32 min ago",
    duration: "01:52",
    status: "Completed",
  },
  {
    patient: "Meena Devi",
    type: "Appointment Booking",
    summary: "Booked a pediatrics appointment",
    time: "45 min ago",
    duration: "04:16",
    status: "Completed",
  },
];

export function RecentAgentConversation() {
  return (
    <div className="rounded-xl border bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">
            Recent AI Conversations
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            Latest voice-agent interactions
          </p>
        </div>

        <button
          type="button"
          className="text-xs font-medium text-primary hover:underline"
        >
          View all
        </button>
      </div>

      {/* Conversations */}
      <div className="divide-y">
        {conversations.map((conversation) => (
          <div
            key={`${conversation.patient}-${conversation.time}`}
            className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-muted/30"
          >
            {/* Voice icon */}
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
              <PhoneCall className="h-4 w-4" />
            </div>

            {/* Conversation details */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="truncate text-sm font-medium">
                  {conversation.patient}
                </p>

                <span className="hidden rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground sm:inline-flex">
                  AI Voice
                </span>
              </div>

              <p className="mt-1 truncate text-xs font-medium">
                {conversation.type}
              </p>

              <p className="mt-0.5 truncate text-xs text-muted-foreground">
                {conversation.summary}
              </p>
            </div>

            {/* Metadata */}
            <div className="hidden shrink-0 text-right md:block">
              <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                <Clock3 className="h-3.5 w-3.5" />
                {conversation.duration}
              </div>

              <p className="mt-1 text-[11px] text-muted-foreground">
                {conversation.time}
              </p>
            </div>

            {/* Status */}
            <div className="hidden sm:block">
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {conversation.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}