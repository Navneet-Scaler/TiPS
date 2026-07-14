"use client";

import { useEffect, useMemo, useState } from "react";
import Sidebar from "@/components/Sidebar";
import SearchBar from "@/components/SearchBar";
import StatTile from "@/components/StatTile";
import OpportunityCard from "@/components/OpportunityCard";
import Timeline from "@/components/Timeline";
import CategoryBars from "@/components/CategoryBars";
import ResearchView from "@/components/ResearchView";
import StartupView from "@/components/StartupView";
import CompetitionsView from "@/components/CompetitionsView";
import { ALL_NAV_ITEMS } from "@/lib/categories";
import { fetchOpportunities, fetchStats, fetchTimeline, Opportunity, Stats } from "@/lib/api";

const PAGE_SIZE = 60;

export default function Page() {
  const [active, setActive] = useState("home");
  const [query, setQuery] = useState("");
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [timelineItems, setTimelineItems] = useState<Opportunity[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const activeItem = useMemo(() => ALL_NAV_ITEMS.find((i) => i.key === active), [active]);

  const isResearch = active === "research";
  const isStartup = active === "startup";
  const isCompetitions = active === "competitions";

  useEffect(() => {
    if (isResearch || isStartup || isCompetitions) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setHasMore(true);

    const sort = active === "trending" ? "trending" : "recent";
    const category = active === "timeline" || active === "calendar" ? undefined : activeItem?.category;

    Promise.all([
      fetchOpportunities({ category, q: query || undefined, sort, limit: PAGE_SIZE }),
      fetchStats(),
      fetchTimeline(72),
    ])
      .then(([opps, s, tl]) => {
        if (cancelled) return;
        setOpportunities(opps);
        setStats(s);
        setTimelineItems(tl);
        setHasMore(opps.length === PAGE_SIZE);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [active, query, activeItem, isResearch, isStartup, isCompetitions]);

  const loadMore = () => {
    const sort = active === "trending" ? "trending" : "recent";
    const category = active === "timeline" || active === "calendar" ? undefined : activeItem?.category;

    setLoadingMore(true);
    fetchOpportunities({ category, q: query || undefined, sort, limit: PAGE_SIZE, offset: opportunities.length })
      .then((more) => {
        setOpportunities((prev) => [...prev, ...more]);
        setHasMore(more.length === PAGE_SIZE);
      })
      .finally(() => setLoadingMore(false));
  };

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
    <div className="flex flex-col md:flex-row min-h-screen">
      <Sidebar active={active} onSelect={setActive} />

      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 max-w-6xl w-full min-w-0">
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
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
        ) : isStartup ? (
          <StartupView query={query} />
        ) : isCompetitions ? (
          <CompetitionsView query={query} />
        ) : (
          <div>
            <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">
              {loading
                ? "Loading"
                : `${filtered.length} loaded${stats?.by_category && activeItem?.category ? ` of ${stats.by_category[activeItem.category] ?? filtered.length}` : ""}`}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {filtered.map((o) => (
                <OpportunityCard key={o.id} opportunity={o} />
              ))}
            </div>
            {!loading && filtered.length === 0 && (
              <div className="text-sm text-base-muted py-16 text-center">
                Nothing here yet — the radar checks sources every 30 minutes.
              </div>
            )}
            {!loading && hasMore && filtered.length > 0 && (
              <div className="flex justify-center mt-6">
                <button
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="px-4 py-2 rounded-lg border border-base-border text-[13px] text-base-muted hover:text-base-text hover:border-accent/50 transition-colors disabled:opacity-50"
                >
                  {loadingMore ? "Loading..." : "Load more"}
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
