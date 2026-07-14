"use client";

import { useEffect, useMemo, useState } from "react";
import Sidebar from "@/components/Sidebar";
import SearchBar from "@/components/SearchBar";
import StatTile from "@/components/StatTile";
import OpportunityCard from "@/components/OpportunityCard";
import Timeline from "@/components/Timeline";
import CategoryBars from "@/components/CategoryBars";
import ResearchView from "@/components/ResearchView";
import { ALL_NAV_ITEMS } from "@/lib/categories";
import { fetchOpportunities, fetchStats, fetchTimeline, Opportunity, Stats } from "@/lib/api";

export default function Page() {
  const [active, setActive] = useState("home");
  const [query, setQuery] = useState("");
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [timelineItems, setTimelineItems] = useState<Opportunity[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const activeItem = useMemo(() => ALL_NAV_ITEMS.find((i) => i.key === active), [active]);

  const isResearch = active === "research";

  useEffect(() => {
    if (isResearch) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);

    const sort = active === "trending" ? "trending" : "recent";
    const category = active === "timeline" || active === "calendar" ? undefined : activeItem?.category;

    Promise.all([
      fetchOpportunities({ category, q: query || undefined, sort, limit: 60 }),
      fetchStats(),
      fetchTimeline(72),
    ])
      .then(([opps, s, tl]) => {
        if (cancelled) return;
        setOpportunities(opps);
        setStats(s);
        setTimelineItems(tl);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [active, query, activeItem, isResearch]);

  const filtered = useMemo(() => {
    if (active === "closing") return opportunities.filter((o) => o.deadline);
    if (active === "new") {
      const dayAgo = Date.now() - 24 * 3600 * 1000;
      return opportunities.filter((o) => new Date(o.discovered_at + "Z").getTime() >= dayAgo);
    }
    return opportunities;
  }, [opportunities, active]);

  const showTimeline = active === "timeline";
  const showHome = active === "home";

  return (
    <div className="flex min-h-screen">
      <Sidebar active={active} onSelect={setActive} />

      <main className="flex-1 px-8 py-6 max-w-6xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-lg font-semibold">{activeItem?.label ?? "Home"}</h1>
            <p className="text-[12.5px] text-base-muted mt-0.5">
              What happened in the AI ecosystem that could create leverage for you.
            </p>
          </div>
        </div>

        <div className="mb-6">
          <SearchBar value={query} onChange={setQuery} />
        </div>

        {showHome && stats && (
          <div className="flex flex-wrap gap-3 mb-6">
            <StatTile label="Tracked" value={stats.total} />
            <StatTile label="New Today" value={stats.new_today} accent="#5b8cff" />
            <StatTile label="New This Week" value={stats.new_this_week} accent="#6fe2a8" />
            <StatTile label="Sources" value={Object.keys(stats.by_organization).length} hint="active" />
          </div>
        )}

        {showHome && stats && (
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-base-panel border border-base-border rounded-xl p-4">
              <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">By Category</div>
              <CategoryBars data={stats.by_category} />
            </div>
            <div className="bg-base-panel border border-base-border rounded-xl p-4">
              <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">Live Feed</div>
              <div className="max-h-[280px] overflow-y-auto pr-1">
                <Timeline items={timelineItems.slice(0, 8)} />
              </div>
            </div>
          </div>
        )}

        {showTimeline ? (
          <div className="bg-base-panel border border-base-border rounded-xl p-6">
            <Timeline items={timelineItems} />
          </div>
        ) : isResearch ? (
          <ResearchView query={query} />
        ) : (
          <div>
            <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">
              {loading ? "Loading" : `${filtered.length} opportunities`}
            </div>
            <div className="grid grid-cols-2 gap-3">
              {filtered.map((o) => (
                <OpportunityCard key={o.id} opportunity={o} />
              ))}
            </div>
            {!loading && filtered.length === 0 && (
              <div className="text-sm text-base-muted py-16 text-center">
                Nothing here yet — the radar checks sources every 30 minutes.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
