"use client";

import { useEffect, useMemo, useState } from "react";
import {
  fetchCompetitionDomains,
  fetchCompetitionTiers,
  fetchOpportunities,
  Opportunity,
} from "@/lib/api";
import OpportunityCard from "@/components/OpportunityCard";

const PAGE_SIZE = 60;

const TIERS = [
  { key: "tier1", label: "Tier 1", hint: "Official hosts" },
  { key: "tier2", label: "Tier 2", hint: "Discovery & community" },
  { key: "tier3", label: "Tier 3", hint: "Elite & grand challenges" },
];

const DOMAIN_ORDER = [
  "Agents",
  "NLP",
  "Computer Vision",
  "Speech",
  "Robotics",
  "Reinforcement Learning",
  "Multimodal / Generative",
  "Data Science",
  "AI Safety",
  "General ML",
  "General",
];

export default function CompetitionsView({ query }: { query: string }) {
  const [activeTier, setActiveTier] = useState<string | null>(null);
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [tierCounts, setTierCounts] = useState<Record<string, number>>({});
  const [domainCounts, setDomainCounts] = useState<Record<string, number>>({});
  const [items, setItems] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setHasMore(true);

    Promise.all([
      fetchOpportunities({
        category: "Competitions",
        tier: activeTier ?? undefined,
        domain: activeDomain ?? undefined,
        q: query || undefined,
        sort: "recent",
        limit: PAGE_SIZE,
      }),
      fetchCompetitionTiers(),
      fetchCompetitionDomains(activeTier ?? undefined),
    ])
      .then(([opps, tiers, domains]) => {
        if (cancelled) return;
        setItems(opps);
        setTierCounts(tiers);
        setDomainCounts(domains);
        setHasMore(opps.length === PAGE_SIZE);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [query, activeTier, activeDomain]);

  const loadMore = () => {
    setLoadingMore(true);
    fetchOpportunities({
      category: "Competitions",
      tier: activeTier ?? undefined,
      domain: activeDomain ?? undefined,
      q: query || undefined,
      sort: "recent",
      limit: PAGE_SIZE,
      offset: items.length,
    })
      .then((more) => {
        setItems((prev) => [...prev, ...more]);
        setHasMore(more.length === PAGE_SIZE);
      })
      .finally(() => setLoadingMore(false));
  };

  const orderedDomains = DOMAIN_ORDER.filter((d) => domainCounts[d]).concat(
    Object.keys(domainCounts).filter((d) => !DOMAIN_ORDER.includes(d))
  );
  const totalCount = Object.values(tierCounts).reduce((a, b) => a + b, 0);

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={() => {
            setActiveTier(null);
            setActiveDomain(null);
          }}
          className={`px-3 py-1.5 rounded-lg text-[13px] border transition-colors ${
            activeTier === null
              ? "bg-accent-soft border-accent text-white"
              : "border-base-border text-base-muted hover:text-base-text"
          }`}
        >
          All ({totalCount})
        </button>
        {TIERS.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setActiveTier(t.key === activeTier ? null : t.key);
              setActiveDomain(null);
            }}
            className={`flex flex-col items-start px-3 py-1.5 rounded-lg text-[13px] border transition-colors ${
              activeTier === t.key
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            <span>
              {t.label} ({tierCounts[t.key] ?? 0})
            </span>
            <span className="text-[10px] opacity-70 -mt-0.5">{t.hint}</span>
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-5">
        <button
          onClick={() => setActiveDomain(null)}
          className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
            activeDomain === null
              ? "bg-accent-soft border-accent text-white"
              : "border-base-border text-base-muted hover:text-base-text"
          }`}
        >
          Any field
        </button>
        {orderedDomains.map((d) => (
          <button
            key={d}
            onClick={() => setActiveDomain(d === activeDomain ? null : d)}
            className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
              activeDomain === d
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            {d} ({domainCounts[d]})
          </button>
        ))}
      </div>

      <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">
        {loading ? "Loading" : `${items.length} loaded${totalCount ? ` of ${activeTier ? tierCounts[activeTier] ?? items.length : totalCount}` : ""}`}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {items.map((o) => (
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
