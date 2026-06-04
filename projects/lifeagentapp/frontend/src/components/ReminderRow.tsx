import { Check } from "lucide-react";
import type { Reminder } from "../data/mock";

export default function ReminderRow({ reminder }: { reminder: Reminder }) {
  return (
    <div className="flex items-center gap-3 rounded-tile bg-surface px-4 py-3.5 shadow-card">
      <span
        className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border ${
          reminder.done
            ? "border-transparent bg-ink text-white"
            : "border-ink/20 text-transparent"
        }`}
      >
        <Check className="h-3.5 w-3.5" strokeWidth={3} />
      </span>
      <span
        className={`flex-1 text-base font-medium ${
          reminder.done ? "text-ink/40 line-through" : "text-ink"
        }`}
      >
        {reminder.title}
      </span>
      <span className="text-sm text-ink/50">{reminder.due}</span>
    </div>
  );
}
