import type { Note } from "../data/mock";

export default function NoteRow({ note }: { note: Note }) {
  return (
    <div className="flex items-center gap-4 rounded-tile bg-surface px-4 py-4 shadow-card">
      <div
        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-xl ${note.iconBg}`}
      >
        {note.icon}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-base font-semibold text-ink">{note.title}</p>
        <p className="truncate text-sm text-ink/50">{note.preview}</p>
      </div>
      <span className={`h-2 w-2 shrink-0 rounded-full ${note.accent}`} />
    </div>
  );
}
