import { colorForCategory } from "@/lib/categories";

export default function CategoryBars({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, v]) => v), 1);

  if (entries.length === 0) {
    return <div className="text-sm text-base-muted py-6 text-center">No data yet.</div>;
  }

  return (
    <div className="space-y-2.5">
      {entries.map(([category, count]) => {
        const color = colorForCategory(category);
        const pct = (count / max) * 100;
        return (
          <div key={category} className="flex items-center gap-3">
            <div className="w-28 shrink-0 text-[12px] text-base-muted truncate">{category}</div>
            <div className="flex-1 h-2 rounded-full bg-base-panel2 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
            <div className="w-6 text-right text-[12px] tabular-nums text-base-muted">{count}</div>
          </div>
        );
      })}
    </div>
  );
}
