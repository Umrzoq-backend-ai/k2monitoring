'use client';

import { useState } from 'react';

interface Props {
  data: unknown;
}

export function GenericView({ data }: Props) {
  return <Renderer value={data} depth={0} />;
}

function Renderer({ value, depth }: { value: unknown; depth: number }) {
  if (value === null || value === undefined) {
    return <span className="text-gray-600 text-sm">—</span>;
  }

  if (typeof value === 'number') {
    return <span className="text-amber-300 text-sm font-mono">{value.toLocaleString()}</span>;
  }

  if (typeof value === 'boolean') {
    return <span className={`text-sm ${value ? 'text-emerald-400' : 'text-red-400'}`}>{value ? 'Ha' : 'Yo\'q'}</span>;
  }

  if (typeof value === 'string') {
    return <span className="text-gray-200 text-sm break-all">{value}</span>;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-gray-600 text-sm italic">bo&apos;sh</span>;
    if (typeof value[0] === 'object' && value[0] !== null) return <Table items={value} />;
    return (
      <ul className="space-y-0.5 pl-3 border-l border-[#1e293b]">
        {value.map((item, i) => (
          <li key={i} className="text-sm text-gray-300">{String(item)}</li>
        ))}
      </ul>
    );
  }

  if (typeof value === 'object') {
    return (
      <div className="space-y-1">
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
          <Row key={k} label={k} value={v} depth={depth} />
        ))}
      </div>
    );
  }

  return <span className="text-sm text-gray-400">{String(value)}</span>;
}

function Row({ label, value, depth }: { label: string; value: unknown; depth: number }) {
  const [open, setOpen] = useState(depth < 1);
  const isComplex = typeof value === 'object' && value !== null;

  if (!isComplex) {
    return (
      <div className="flex items-baseline justify-between py-1.5 px-2 rounded hover:bg-[#1a2332]">
        <span className="text-[11px] text-gray-500 shrink-0 mr-3">{formatKey(label)}</span>
        <Renderer value={value} depth={depth + 1} />
      </div>
    );
  }

  return (
    <div className="border border-[#1e293b] rounded-lg my-1 overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-2 px-2.5 py-1.5 hover:bg-[#1a2332] text-left">
        <svg className={`w-2.5 h-2.5 text-gray-500 transition-transform ${open ? 'rotate-90' : ''}`} fill="currentColor" viewBox="0 0 16 16">
          <path d="M6 3l5 5-5 5V3z" />
        </svg>
        <span className="text-[11px] text-sky-400/80 font-medium">{formatKey(label)}</span>
        <span className="text-[9px] text-gray-600 ml-auto">
          {Array.isArray(value) ? `${value.length}` : 'obj'}
        </span>
      </button>
      {open && (
        <div className="px-3 pb-2 pl-5 border-t border-[#1e293b]">
          <Renderer value={value} depth={depth + 1} />
        </div>
      )}
    </div>
  );
}

function Table({ items }: { items: Record<string, any>[] }) {
  const keys = Object.keys(items[0]).filter((k) => typeof items[0][k] !== 'object' || items[0][k] === null).slice(0, 5);
  return (
    <div className="overflow-x-auto rounded-lg border border-[#1e293b]">
      <table className="w-full text-[11px]">
        <thead>
          <tr className="bg-[#111827] border-b border-[#1e293b]">
            {keys.map((k) => (
              <th key={k} className="px-2.5 py-1.5 text-left text-sky-400/60 font-medium">{formatKey(k)}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1e293b]">
          {items.slice(0, 30).map((item, i) => (
            <tr key={i} className="hover:bg-[#1a2332]">
              {keys.map((k) => (
                <td key={k} className="px-2.5 py-1.5 text-gray-300 max-w-[150px] truncate">
                  {item[k] === null ? '—' : typeof item[k] === 'boolean' ? (item[k] ? '✅' : '❌') : String(item[k])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {items.length > 30 && <p className="px-2.5 py-1 text-[9px] text-gray-600 border-t border-[#1e293b]">+{items.length - 30} yana</p>}
    </div>
  );
}

function formatKey(key: string): string {
  return key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase()).trim();
}
