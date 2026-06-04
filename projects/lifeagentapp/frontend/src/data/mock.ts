export interface EventItem {
  time: string;
  title: string;
}

export interface Note {
  id: string;
  title: string;
  preview: string;
  icon: string;
  iconBg: string;
  accent: string; // left accent / tag color
}

export interface Reminder {
  id: string;
  title: string;
  due: string;
  done: boolean;
}

// Today's calendar events (Calendar Agent)
export const todayEvents: EventItem[] = [
  { time: "9:30 AM", title: "Face interview" },
  { time: "11:00 AM", title: "Client meeting" },
  { time: "4:30 PM", title: "Learning design" },
];

// Counts for the stat tiles
export const stats = {
  reminders: 5,
  notes: 12,
};

// Reminders (Task Agent)
export const reminders: Reminder[] = [
  { id: "r1", title: "Call GP", due: "Thu, 10:00 AM", done: false },
  { id: "r2", title: "Pay rent", due: "1st, 9:00 AM", done: false },
  { id: "r3", title: "Renew gym membership", due: "Fri", done: true },
];

// Notes (Notes Agent)
export const notes: Note[] = [
  {
    id: "n1",
    title: "Lunch with Sarah",
    preview: "Spent £18 — try the new ramen place next time",
    icon: "🍜",
    iconBg: "bg-blush",
    accent: "bg-blush",
  },
  {
    id: "n2",
    title: "Project idea",
    preview: "Personal Life OS agent — multi-agent + MCP",
    icon: "💡",
    iconBg: "bg-butter",
    accent: "bg-butter",
  },
  {
    id: "n3",
    title: "Book recommendation",
    preview: "Designing Data-Intensive Applications",
    icon: "📚",
    iconBg: "bg-lilacSoft",
    accent: "bg-lilac",
  },
];

export const user = {
  name: "Marie",
  greeting: "Good evening,",
};
