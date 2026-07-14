export default function StatTile({
  label,
  value,
  hint,
  accent,
}: {
  label: string;
  value: string | number;
  hint?: string;
  accent?: string;
}) {
  return (
    <div className="bg-base-panel border border-base-border rounded-xl px-4 py-3.5 flex-1 min-w-[140px]">
      <div className="text-[11px] uppercase tracking-wider text-base-muted">{label}</div>
      <div className="mt-1.5 flex items-baseline gap-1.5">
        <span className="text-2xl font-semibold tabular-nums" style={accent ? { color: accent } : undefined}>
          {value}
        </span>
        {hint && <span className="text-[11px] text-base-muted">{hint}</span>}
      </div>
    </div>
  );
}
