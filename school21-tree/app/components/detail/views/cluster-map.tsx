'use client';

import { useState, useMemo } from 'react';

interface Workplace {
  row: string;
  number: number;
  login: string | null;
}

interface Props {
  clusterMap: Workplace[];
  clusterName?: string;
  onPeerClick?: (login: string) => void;
}

export function ClusterMapGrid({ clusterMap, clusterName, onPeerClick }: Props) {
  const [hoveredSeat, setHoveredSeat] = useState<string | null>(null);

  // Derive grid dimensions from data
  const { rows, cols, seatMap, occupied, total } = useMemo(() => {
    const rowSet = new Set<string>();
    const colSet = new Set<number>();
    const map = new Map<string, Workplace>();

    for (const wp of clusterMap) {
      rowSet.add(wp.row);
      colSet.add(wp.number);
      map.set(`${wp.row}:${wp.number}`, wp);
    }

    return {
      rows: [...rowSet].sort(),
      cols: [...colSet].sort((a, b) => a - b),
      seatMap: map,
      occupied: clusterMap.filter((wp) => wp.login).length,
      total: clusterMap.length,
    };
  }, [clusterMap]);

  const occupancyPct = total > 0 ? Math.round((occupied / total) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Header stats */}
      <div className="flex items-center justify-between">
        <div>
          {clusterName && (
            <h3 className="text-base font-semibold text-white mb-0.5">{clusterName}</h3>
          )}
          <p className="text-[11px] text-gray-500">
            <span className="text-sky-400 font-medium">{occupied}</span> / {total} band
            <span className="text-gray-600 ml-2">({occupancyPct}%)</span>
          </p>
        </div>
        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px] text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded bg-[#1a2332] border border-[#2d3748]" /> Bo&apos;sh
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded bg-sky-500/80" /> Band
          </span>
        </div>
      </div>

      {/* Occupancy bar */}
      <div className="h-1.5 bg-[#1a2332] rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-sky-500 to-emerald-400 rounded-full transition-all duration-700"
          style={{ width: `${occupancyPct}%` }}
        />
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Column headers */}
          <div className="flex items-center mb-1" style={{ paddingLeft: '28px' }}>
            {cols.map((col) => (
              <div
                key={col}
                className="text-[10px] text-gray-600 font-mono text-center"
                style={{ width: '44px' }}
              >
                {col}
              </div>
            ))}
          </div>

          {/* Rows */}
          <div className="space-y-1">
            {rows.map((row) => (
              <div key={row} className="flex items-center gap-0">
                {/* Row label */}
                <div className="w-7 text-[11px] text-gray-500 font-mono font-medium text-center shrink-0">
                  {row.toUpperCase()}
                </div>

                {/* Seats */}
                <div className="flex gap-1">
                  {cols.map((col) => {
                    const key = `${row}:${col}`;
                    const wp = seatMap.get(key);
                    const login = wp?.login || null;
                    const isOccupied = !!login;
                    const isHovered = hoveredSeat === key;

                    return (
                      <div
                        key={key}
                        className="relative"
                        onMouseEnter={() => setHoveredSeat(key)}
                        onMouseLeave={() => setHoveredSeat(null)}
                      >
                        <button
                          onClick={() => login && onPeerClick?.(login)}
                          className={`
                            w-10 h-8 rounded-md text-[10px] font-mono
                            transition-all duration-150 border
                            flex items-center justify-center
                            ${isOccupied
                              ? 'bg-sky-500/20 border-sky-500/40 text-sky-300 hover:bg-sky-500/30 hover:scale-105 cursor-pointer'
                              : 'bg-[#111827] border-[#1e293b] text-gray-700 cursor-default'
                            }
                            ${isHovered && isOccupied ? 'ring-1 ring-sky-400/50 scale-105' : ''}
                          `}
                          disabled={!isOccupied}
                          aria-label={isOccupied ? `${row.toUpperCase()}${col}: ${login}` : `${row.toUpperCase()}${col}: bo'sh`}
                        >
                          {isOccupied ? '👤' : '·'}
                        </button>

                        {/* Tooltip */}
                        {isHovered && isOccupied && (
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none">
                            <div className="bg-[#1e293b] border border-[#334155] rounded-lg px-2.5 py-1.5 shadow-xl whitespace-nowrap">
                              <p className="text-[11px] text-white font-medium">{login}</p>
                              <p className="text-[9px] text-gray-400">{row.toUpperCase()}{col}</p>
                            </div>
                            {/* Arrow */}
                            <div className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 bg-[#1e293b] border-r border-b border-[#334155] rotate-45 -mt-1" />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Occupied list */}
      {occupied > 0 && (
        <div className="mt-4 pt-4 border-t border-[#1e293b]">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Hozir klasterda ({occupied})</p>
          <div className="flex flex-wrap gap-1.5">
            {clusterMap
              .filter((wp) => wp.login)
              .sort((a, b) => `${a.row}${a.number}`.localeCompare(`${b.row}${b.number}`))
              .map((wp) => (
                <button
                  key={`${wp.row}${wp.number}`}
                  onClick={() => wp.login && onPeerClick?.(wp.login)}
                  className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#1a2332] border border-[#2d3748] hover:border-sky-500/40 hover:bg-sky-500/10 transition-colors text-[11px]"
                >
                  <span className="text-gray-500 font-mono">{wp.row.toUpperCase()}{wp.number}</span>
                  <span className="text-sky-300">{wp.login}</span>
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
