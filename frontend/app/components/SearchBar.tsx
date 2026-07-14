"use client";

import { SearchIcon, BellIcon } from "@/icons/Icons";

export default function SearchBar({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 flex items-center gap-2 bg-base-panel2 border border-base-border rounded-lg px-3 py-2">
        <SearchIcon width={16} height={16} className="text-base-muted" />
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Search the AI ecosystem — e.g. 'AI safety fellowships in Europe'"
          className="bg-transparent outline-none text-sm flex-1 placeholder:text-base-muted/70"
        />
      </div>
      <button className="w-9 h-9 flex items-center justify-center rounded-lg border border-base-border bg-base-panel2 text-base-muted hover:text-base-text">
        <BellIcon width={16} height={16} />
      </button>
    </div>
  );
}
