import { Opportunity } from "@/lib/api";
import { colorForCategory } from "@/lib/categories";
import { ArrowUpRightIcon } from "@/icons/Icons";

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso + "Z").getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${Math.max(mins, 0)}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function deadlineLabel(iso: string | null): string | null {
  if (!iso) return null;
  const days = Math.ceil((new Date(iso + "Z").getTime() - Date.now()) / 86400000);
  if (days < 0) return "closed";
  if (days === 0) return "closes today";
  if (days <= 7) return `closes in ${days}d`;
  return `closes in ${days}d`;
}

export default function OpportunityCard({ opportunity }: { opportunity: Opportunity }) {
  const color = colorForCategory(opportunity.category);
  const deadline = deadlineLabel(opportunity.deadline);

  return (
    <a
      href={opportunity.url}
      target="_blank"
      rel="noreferrer"
      className="group block bg-base-panel border border-base-border rounded-xl p-4 hover:border-accent/50 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span
            className="text-[10px] font-medium uppercase tracking-wide px-2 py-0.5 rounded-full"
            style={{ color, backgroundColor: `${color}22` }}
          >
            {opportunity.category}
          </span>
          {opportunity.organization && (
            <span className="text-[11px] text-base-muted">{opportunity.organization}</span>
          )}
        </div>
        <ArrowUpRightIcon
          width={14}
          height={14}
          className="text-base-muted opacity-0 group-hover:opacity-100 transition-opacity"
        />
      </div>

      <h3 className="text-sm font-medium leading-snug text-base-text">{opportunity.title}</h3>

      {opportunity.summary && (
        <p className="mt-1.5 text-[12.5px] text-base-muted line-clamp-2 leading-relaxed">
          {opportunity.summary.replace(/<[^>]*>/g, "")}
        </p>
      )}

      <div className="mt-3 flex items-center gap-3 text-[11px] text-base-muted">
        <span>{timeAgo(opportunity.published_at)}</span>
        <span>&middot;</span>
        <span>{opportunity.geography}</span>
        {opportunity.is_remote && (
          <>
            <span>&middot;</span>
            <span>remote</span>
          </>
        )}
        {deadline && (
          <>
            <span>&middot;</span>
            <span className={deadline.includes("today") ? "text-amber-400" : ""}>{deadline}</span>
          </>
        )}
      </div>
    </a>
  );
}
