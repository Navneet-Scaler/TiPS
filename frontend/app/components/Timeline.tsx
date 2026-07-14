import { Opportunity } from "@/lib/api";
import { colorForCategory } from "@/lib/categories";

function formatTime(iso: string): string {
  const d = new Date(iso + "Z");
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function Timeline({ items }: { items: Opportunity[] }) {
  if (items.length === 0) {
    return <div className="text-sm text-base-muted py-8 text-center">No activity in this window yet.</div>;
  }

  return (
    <div className="relative pl-6">
      <div className="absolute left-[7px] top-1 bottom-1 w-px bg-base-border" />
      <div className="space-y-5">
        {items.map((item) => {
          const color = colorForCategory(item.category);
          return (
            <div key={item.id} className="relative">
              <span
                className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full border-2 border-base-bg"
                style={{ backgroundColor: color }}
              />
              <div className="flex items-baseline gap-2 text-[11px] text-base-muted mb-0.5">
                <span className="font-mono">{formatTime(item.discovered_at)}</span>
                <span style={{ color }}>{item.category}</span>
                {item.organization && <span>&middot; {item.organization}</span>}
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-base-text hover:text-accent transition-colors"
              >
                {item.title}
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
