"use client";

import { NAV_SECTIONS } from "@/lib/categories";
import { GlobeIcon } from "@/icons/Icons";

export default function Sidebar({
  active,
  onSelect,
}: {
  active: string;
  onSelect: (key: string) => void;
}) {
  return (
    <aside className="w-60 shrink-0 border-r border-base-border bg-base-panel h-screen sticky top-0 flex flex-col">
      <div className="px-5 py-5 flex items-center gap-2 border-b border-base-border">
        <div className="w-7 h-7 rounded-md bg-accent/20 flex items-center justify-center">
          <GlobeIcon width={16} height={16} className="text-accent" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight">TIPS</div>
          <div className="text-[11px] text-base-muted -mt-0.5">Opportunity Radar</div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            <div className="px-2 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-base-muted/70">
              {section.title}
            </div>
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = active === item.key;
                return (
                  <button
                    key={item.key}
                    onClick={() => onSelect(item.key)}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-[13px] transition-colors ${
                      isActive
                        ? "bg-accent-soft text-white"
                        : "text-base-muted hover:bg-base-panel2 hover:text-base-text"
                    }`}
                  >
                    <Icon width={16} height={16} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-base-border text-[11px] text-base-muted">
        Live radar &middot; updates every 30 min
      </div>
    </aside>
  );
}
