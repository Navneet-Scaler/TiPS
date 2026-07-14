"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchOpportunities, fetchStartupSubtypes, Opportunity } from "@/lib/api";
import OpportunityCard from "@/components/OpportunityCard";
import { GlobeIcon, ClockIcon } from "@/icons/Icons";

const SUBTYPE_ORDER = [
  "Accelerator",
  "Incubator",
  "Venture Studio",
  "Founder Fellowship",
  "Grant (non-dilutive)",
  "Compute/Credit Program",
  "Pitch Competition",
  "Demo Day",
  "Co-founder Matching",
  "Startup Visa / Relocation",
  "General",
];

const PAGE_SIZE = 80;

export default function StartupView({ query }: { query: string }) {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [subcounts, setSubcounts] = useState<Record<string, number>>({});
  const [activeSubtype, setActiveSubtype] = useState<string | null>(null);
  const [region, setRegion] = useState<"All" | "India" | "Global">("All");
  const [dilution, setDilution] = useState<"All" | "equity" | "non-dilutive">("All");
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setHasMore(true);

    Promise.all([
      fetchOpportunities({
        category: "Startup",
        subcategory: activeSubtype ?? undefined,
        q: query || undefined,
        geography: region === "All" ? undefined : region,
        dilutionType: dilution === "All" ? undefined : dilution,
        limit: PAGE_SIZE,
      }),
      fetchStartupSubtypes(),
    ])
      .then(([opps, subs]) => {
        if (cancelled) return;
        setItems(opps);
        setSubcounts(subs);
        setHasMore(opps.length === PAGE_SIZE);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [query, activeSubtype, region, dilution]);

  const loadMore = () => {
    setLoadingMore(true);
    fetchOpportunities({
      category: "Startup",
      subcategory: activeSubtype ?? undefined,
      q: query || undefined,
      geography: region === "All" ? undefined : region,
      dilutionType: dilution === "All" ? undefined : dilution,
      limit: PAGE_SIZE,
      offset: items.length,
    })
      .then((more) => {
        setItems((prev) => [...prev, ...more]);
        setHasMore(more.length === PAGE_SIZE);
      })
      .finally(() => setLoadingMore(false));
  };

  const rolling = useMemo(() => items.filter((o) => o.is_rolling), [items]);
  const deadlineBased = useMemo(() => items.filter((o) => !o.is_rolling), [items]);

  const orderedSubs = SUBTYPE_ORDER.filter((s) => subcounts[s]).concat(
    Object.keys(subcounts).filter((s) => !SUBTYPE_ORDER.includes(s))
  );

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2 mb-4">
        {(["All", "India", "Global"] as const).map((r) => (
          <button
            key={r}
            onClick={() => setRegion(r)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
              region === r
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            <GlobeIcon width={12} height={12} />
            {r}
          </button>
        ))}

        <div className="w-px h-4 bg-base-border mx-1" />

        {(["All", "equity", "non-dilutive"] as const).map((d) => (
          <button
            key={d}
            onClick={() => setDilution(d)}
            className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
              dilution === d
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            {d === "All" ? "Any dilution" : d}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-5">
        <button
          onClick={() => setActiveSubtype(null)}
          className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
            activeSubtype === null
              ? "bg-accent-soft border-accent text-white"
              : "border-base-border text-base-muted hover:text-base-text"
          }`}
        >
          All types ({Object.values(subcounts).reduce((a, b) => a + b, 0)})
        </button>
        {orderedSubs.map((sub) => (
          <button
            key={sub}
            onClick={() => setActiveSubtype(sub === activeSubtype ? null : sub)}
            className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
              activeSubtype === sub
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            {sub} ({subcounts[sub]})
          </button>
        ))}
      </div>

      {!loading && rolling.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <ClockIcon width={15} height={15} className="text-sky-400" />
            <div className="text-[11px] uppercase tracking-wider text-sky-400">
              Always Open &middot; rolling, no fixed deadline
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {rolling.map((o) => (
              <OpportunityCard key={o.id} opportunity={o} />
            ))}
          </div>
        </div>
      )}

      <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">
        {loading ? "Loading" : `Open / Closing Soon (${deadlineBased.length})`}
      </div>
      <div className="grid grid-cols-2 gap-3">
        {deadlineBased.map((o) => (
          <OpportunityCard key={o.id} opportunity={o} />
        ))}
      </div>

      {!loading && items.length === 0 && (
        <div className="text-sm text-base-muted py-16 text-center">
          Nothing here yet for this filter combination.
        </div>
      )}
      {!loading && hasMore && items.length > 0 && (
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
  );
}
