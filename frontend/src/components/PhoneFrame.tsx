import { ReactNode } from "react";

export default function PhoneFrame({ children }: { children: ReactNode }) {
  return (
    <div className="relative mx-auto w-[390px] max-w-full">
      <div className="relative h-[844px] overflow-hidden rounded-[44px] bg-surface shadow-soft ring-1 ring-black/5">
        {/* Status bar */}
        <div className="flex items-center justify-between px-8 pt-4 text-xs font-semibold text-ink">
          <span>9:41</span>
          <div className="flex items-center gap-1">
            <span className="h-2 w-4 rounded-sm bg-ink/80" />
            <span className="h-2 w-3 rounded-sm bg-ink/50" />
            <span className="h-2 w-5 rounded-sm bg-ink/80" />
          </div>
        </div>
        <div className="no-scrollbar h-[calc(100%-40px)] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
