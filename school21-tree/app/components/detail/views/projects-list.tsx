'use client';

import { useState } from 'react';

interface Project {
  id: number;
  title?: string;
  name?: string;
  status: string;
  finalPercentage: number | null;
  type?: string;
}

interface Props {
  projects: Project[];
}

export function ProjectsList({ projects }: Props) {
  const [filter, setFilter] = useState<'all' | 'done' | 'active'>('all');

  const done = projects.filter((p) => p.finalPercentage !== null);
  const active = projects.filter((p) => p.finalPercentage === null);

  const filtered = filter === 'all' ? projects : filter === 'done' ? done : active;

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="flex gap-2">
        <FilterBtn active={filter === 'all'} onClick={() => setFilter('all')} label={`Hammasi (${projects.length})`} />
        <FilterBtn active={filter === 'done'} onClick={() => setFilter('done')} label={`Tugatilgan (${done.length})`} />
        <FilterBtn active={filter === 'active'} onClick={() => setFilter('active')} label={`Jarayonda (${active.length})`} />
      </div>

      {/* List */}
      <div className="space-y-1">
        {filtered.slice(0, 60).map((p) => (
          <div key={p.id} className="flex items-center gap-2 px-2.5 py-2 rounded-lg hover:bg-[#1a2332] transition-colors group">
            <span className="text-[12px] shrink-0">
              {p.finalPercentage !== null ? '✅' : '🔄'}
            </span>
            <span className="text-[12px] text-gray-300 truncate flex-1 group-hover:text-white transition-colors">
              {p.title || p.name || `Project #${p.id}`}
            </span>
            {p.finalPercentage !== null && (
              <span className={`text-[11px] font-mono shrink-0 ${
                p.finalPercentage >= 80 ? 'text-emerald-400' : p.finalPercentage >= 50 ? 'text-amber-400' : 'text-red-400'
              }`}>
                {p.finalPercentage}%
              </span>
            )}
            {p.type && (
              <span className="text-[9px] text-gray-600 shrink-0 uppercase">{p.type}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function FilterBtn({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`px-2.5 py-1 text-[11px] rounded-md transition-colors ${
        active
          ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30'
          : 'text-gray-500 hover:text-gray-300 border border-transparent hover:bg-[#1a2332]'
      }`}
    >
      {label}
    </button>
  );
}
