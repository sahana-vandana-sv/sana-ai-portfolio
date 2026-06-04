import { Bell, Plus, Bell as BellIcon, StickyNote } from "lucide-react";
import NoteRow from "../components/NoteRow";
import ReminderRow from "../components/ReminderRow";
import { notes, reminders, stats, todayEvents, user } from "../data/mock";

export default function Dashboard() {
  return (
    <div className="px-6 pb-10 pt-2">
      {/* Header */}
      <header className="flex items-start justify-between pt-2">
        <div>
          <p className="text-sm text-ink/60">{user.greeting}</p>
          <h1 className="text-4xl font-extrabold tracking-tight text-ink">
            {user.name}!
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button className="relative flex h-12 w-12 items-center justify-center rounded-full bg-cloud">
            <Bell className="h-5 w-5 text-ink" />
            <span className="absolute right-3 top-3 h-2 w-2 rounded-full bg-ink" />
          </button>
          <button className="flex h-12 w-12 items-center justify-center rounded-full bg-ink text-white">
            <Plus className="h-6 w-6" />
          </button>
        </div>
      </header>

      {/* Top grid: Today's Events card + two stat tiles */}
      <section className="mt-6 grid grid-cols-2 gap-4">
        {/* Today's Events */}
        <div className="rounded-card bg-butter p-5">
          <h2 className="text-2xl font-bold text-ink">Today</h2>
          <p className="text-sm text-ink/50">Events</p>
          <div className="mt-4 space-y-3">
            {todayEvents.map((item, i) => (
              <div key={i}>
                <p className="text-sm text-ink/60">{item.time}</p>
                <p className="text-base font-semibold text-ink">{item.title}</p>
                {i < todayEvents.length - 1 && (
                  <div className="mt-3 h-px w-full bg-ink/10" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right column: Reminders + Notes tiles */}
        <div className="flex flex-col gap-4">
          <div className="flex flex-1 flex-col justify-between rounded-card bg-mintSoft p-5">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/70">
              <BellIcon className="h-5 w-5 text-ink" />
            </div>
            <div className="mt-6">
              <p className="text-sm text-ink/60">{stats.reminders} due</p>
              <p className="text-lg font-bold text-ink">Reminders</p>
            </div>
          </div>

          <div className="flex flex-1 flex-col justify-between rounded-card bg-lilacSoft p-5">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/70">
              <StickyNote className="h-5 w-5 text-ink" />
            </div>
            <div className="mt-6">
              <p className="text-sm text-ink/60">{stats.notes} saved</p>
              <p className="text-lg font-bold text-ink">Notes</p>
            </div>
          </div>
        </div>
      </section>

      {/* Reminders */}
      <section className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-ink">
            Reminders
          </h2>
          <button className="flex items-center gap-1 rounded-pill border border-ink/15 px-4 py-2 text-sm font-medium text-ink">
            <Plus className="h-4 w-4" /> Add
          </button>
        </div>
        <p className="mt-1 text-sm text-ink/50">
          You have {reminders.filter((r) => !r.done).length} upcoming reminders.
        </p>

        <div className="mt-4 space-y-3">
          {reminders.map((r) => (
            <ReminderRow key={r.id} reminder={r} />
          ))}
        </div>
      </section>

      {/* Notes */}
      <section className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-ink">
            Notes
          </h2>
          <button className="text-sm font-medium text-ink/50">View all</button>
        </div>
        <p className="mt-1 text-sm text-ink/50">
          Recently saved by your agent.
        </p>

        <div className="mt-4 space-y-3">
          {notes.map((n) => (
            <NoteRow key={n.id} note={n} />
          ))}
        </div>
      </section>
    </div>
  );
}
