"use client";

import { useState } from "react";
import { NAV_SECTIONS } from "@/lib/categories";
import { GlobeIcon, RefreshIcon } from "@/icons/Icons";
import { triggerIngestRun } from "@/lib/api";

function MenuIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" {...props}>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}

function CloseIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" {...props}>
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  );
}

export default function Sidebar({
  active,
  onSelect,
}: {
  active: string;
  onSelect: (key: string) => void;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshFailed, setRefreshFailed] = useState(false);

  const handleSelect = (key: string) => {
    onSelect(key);
    setMobileOpen(false);
  };

  const handleRefresh = async () => {
    if (refreshing) return;
    setRefreshing(true);
    setRefreshFailed(false);
    try {
      await triggerIngestRun();
      window.location.reload();
    } catch {
      setRefreshing(false);
      setRefreshFailed(true);
    }
  };

  return (
    <>
      <div className="md:hidden sticky top-0 z-30 flex items-center gap-3 px-4 py-3 border-b border-base-border bg-base-panel">
        <button
          onClick={() => setMobileOpen(true)}
          className="w-8 h-8 flex items-center justify-center rounded-md text-base-muted hover:text-base-text hover:bg-base-panel2"
          aria-label="Open menu"
        >
          <MenuIcon />
        </button>
        <div className="w-6 h-6 rounded-md bg-accent/20 flex items-center justify-center">
          <GlobeIcon width={14} height={14} className="text-accent" />
        </div>
        <div className="text-sm font-semibold tracking-tight">TIPS</div>
      </div>

      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/60"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`
          fixed md:sticky top-0 left-0 z-50 md:z-auto
          w-72 md:w-60 shrink-0 h-screen
          border-r border-base-border bg-base-panel flex flex-col
          transition-transform duration-200
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0
        `}
      >
        <div className="px-5 py-5 flex items-center justify-between border-b border-base-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-accent/20 flex items-center justify-center">
              <GlobeIcon width={16} height={16} className="text-accent" />
            </div>
            <div>
              <div className="text-sm font-semibold tracking-tight">TIPS</div>
              <div className="text-[11px] text-base-muted -mt-0.5">Opportunity Radar</div>
            </div>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="md:hidden w-7 h-7 flex items-center justify-center rounded-md text-base-muted hover:text-base-text"
            aria-label="Close menu"
          >
            <CloseIcon />
          </button>
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
                      onClick={() => handleSelect(item.key)}
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

        <div className="px-5 py-4 border-t border-base-border flex items-center justify-between gap-2">
          <span className="text-[11px] text-base-muted">
            {refreshing
              ? "Refreshing now..."
              : refreshFailed
              ? "Refresh failed - try again"
              : "Live radar · updates every 30 min"}
          </span>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            title="Pull the latest data right now"
            aria-label="Refresh all tabs now"
            className={`w-7 h-7 shrink-0 flex items-center justify-center rounded-md border border-base-border text-base-muted hover:text-base-text hover:border-accent/50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed ${
              refreshing ? "text-accent" : ""
            }`}
          >
            <RefreshIcon width={14} height={14} className={refreshing ? "animate-spin" : ""} />
          </button>
        </div>
      </aside>
    </>
  );
}
