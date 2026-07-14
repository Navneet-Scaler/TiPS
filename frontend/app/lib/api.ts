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
  isPaid?: boolean;
}): Promise<Opportunity[]> {
  const search = new URLSearchParams();
  if (params.category) search.set("category", params.category);
  if (params.subcategory) search.set("subcategory", params.subcategory);
  if (params.q) search.set("q", params.q);
  if (params.sort) search.set("sort", params.sort);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.isPaid) search.set("is_paid", "true");
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
