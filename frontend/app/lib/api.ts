export type Opportunity = {
  id: string;
  title: string;
  summary: string | null;
  url: string;
  category: string;
  subcategory: string | null;
  organization: string | null;
  geography: string;
  is_remote: boolean;
  is_paid: boolean;
  deadline: string | null;
  is_rolling: boolean;
  dilution_type: string | null;
  tier: string | null;
  domain: string | null;
  published_at: string | null;
  discovered_at: string;
  score: number;
};

export type Stats = {
  total: number;
  new_today: number;
  new_this_week: number;
  by_category: Record<string, number>;
  by_organization: Record<string, number>;
};

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed: ${path}`);
  return res.json() as Promise<T>;
}

export function fetchOpportunities(params: {
  category?: string;
  subcategory?: string;
  q?: string;
  sort?: "recent" | "trending";
  limit?: number;
  offset?: number;
  isPaid?: boolean;
  geography?: string;
  dilutionType?: string;
  isRolling?: boolean;
  tier?: string;
  domain?: string;
}): Promise<Opportunity[]> {
  const search = new URLSearchParams();
  if (params.category) search.set("category", params.category);
  if (params.subcategory) search.set("subcategory", params.subcategory);
  if (params.q) search.set("q", params.q);
  if (params.sort) search.set("sort", params.sort);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  if (params.isPaid) search.set("is_paid", "true");
  if (params.geography) search.set("geography", params.geography);
  if (params.dilutionType) search.set("dilution_type", params.dilutionType);
  if (params.isRolling !== undefined) search.set("is_rolling", String(params.isRolling));
  if (params.tier) search.set("tier", params.tier);
  if (params.domain) search.set("domain", params.domain);
  return apiGet(`/api/opportunities?${search.toString()}`);
}

export function fetchTimeline(hours = 48): Promise<Opportunity[]> {
  return apiGet(`/api/opportunities/timeline?hours=${hours}`);
}

export function fetchStats(): Promise<Stats> {
  return apiGet(`/api/opportunities/stats`);
}

export function fetchResearchSubcategories(): Promise<Record<string, number>> {
  return apiGet(`/api/opportunities/research/subcategories`);
}

export function fetchStartupSubtypes(): Promise<Record<string, number>> {
  return apiGet(`/api/opportunities/startup/subtypes`);
}

export function fetchCompetitionTiers(): Promise<Record<string, number>> {
  return apiGet(`/api/opportunities/competitions/tiers`);
}

export function fetchCompetitionDomains(tier?: string): Promise<Record<string, number>> {
  const search = tier ? `?tier=${encodeURIComponent(tier)}` : "";
  return apiGet(`/api/opportunities/competitions/domains${search}`);
}
