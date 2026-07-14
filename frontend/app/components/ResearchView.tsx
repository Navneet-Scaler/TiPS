"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchOpportunities, fetchResearchSubcategories, Opportunity } from "@/lib/api";
import OpportunityCard from "@/components/OpportunityCard";
import { CoinIcon, PeopleIcon } from "@/icons/Icons";

const SUBCATEGORY_ORDER = [
  "Seeking Collaborators",
  "Recruiting Students",
  "Fellowship",
  "PhD Fellowship",
  "PhD / Postdoc",
  "Compute Grant",
  "Undergrad Research",
  "Government Program",
  "General",
];

const PAGE_SIZE = 80;

export default function ResearchView({ query }: { query: string }) {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [subcounts, setSubcounts] = useState<Record<string, number>>({});
  const [activeSubcategory, setActiveSubcategory] = useState<string | null>(null);
  const [fundedOnly, setFundedOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setHasMore(true);

    Promise.all([
      fetchOpportunities({
        category: "Research",
        subcategory: activeSubcategory ?? undefined,
        q: query || undefined,
        isPaid: fundedOnly || undefined,
        limit: PAGE_SIZE,
      }),
      fetchResearchSubcategories(),
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
  }, [query, activeSubcategory, fundedOnly]);

  const loadMore = () => {
    setLoadingMore(true);
    fetchOpportunities({
      category: "Research",
      subcategory: activeSubcategory ?? undefined,
      q: query || undefined,
      isPaid: fundedOnly || undefined,
      limit: PAGE_SIZE,
      offset: items.length,
    })
      .then((more) => {
        setItems((prev) => [...prev, ...more]);
        setHasMore(more.length === PAGE_SIZE);
      })
      .finally(() => setLoadingMore(false));
  };

  const collaborators = useMemo(
    () => items.filter((o) => o.subcategory === "Seeking Collaborators" || o.subcategory === "Recruiting Students"),
    [items]
  );
  const rest = useMemo(
    () => items.filter((o) => o.subcategory !== "Seeking Collaborators" && o.subcategory !== "Recruiting Students"),
    [items]
  );

  const orderedSubs = SUBCATEGORY_ORDER.filter((s) => subcounts[s]).concat(
    Object.keys(subcounts).filter((s) => !SUBCATEGORY_ORDER.includes(s))
  );

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2 mb-5">
        <button
          onClick={() => setActiveSubcategory(null)}
          className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
            activeSubcategory === null
              ? "bg-accent-soft border-accent text-white"
              : "border-base-border text-base-muted hover:text-base-text"
          }`}
        >
          All ({Object.values(subcounts).reduce((a, b) => a + b, 0)})
        </button>
        {orderedSubs.map((sub) => (
          <button
            key={sub}
            onClick={() => setActiveSubcategory(sub === activeSubcategory ? null : sub)}
            className={`px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
              activeSubcategory === sub
                ? "bg-accent-soft border-accent text-white"
                : "border-base-border text-base-muted hover:text-base-text"
            }`}
          >
            {sub} ({subcounts[sub]})
          </button>
        ))}

        <button
          onClick={() => setFundedOnly((v) => !v)}
          className={`ml-auto flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] border transition-colors ${
            fundedOnly
              ? "bg-emerald-500/15 border-emerald-500/50 text-emerald-300"
              : "border-base-border text-base-muted hover:text-base-text"
          }`}
        >
          <CoinIcon width={13} height={13} />
          Funded only
        </button>
      </div>

      {!activeSubcategory && collaborators.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <PeopleIcon width={15} height={15} className="text-amber-400" />
            <div className="text-[11px] uppercase tracking-wider text-amber-400">
              Seeking Collaborators &middot; time-sensitive
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {collaborators.map((o) => (
              <OpportunityCard key={o.id} opportunity={o} />
            ))}
          </div>
        </div>
      )}

      <div className="text-[11px] uppercase tracking-wider text-base-muted mb-3">
        {loading ? "Loading" : `${activeSubcategory ? items.length : rest.length} opportunities`}
      </div>
      <div className="grid grid-cols-2 gap-3">
        {(activeSubcategory ? items : rest).map((o) => (
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
