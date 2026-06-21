'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Spinner } from '../ui/spinner';

interface SearchResult {
  id: string;
  label: string;
  type: 'peer' | 'cluster' | 'campus';
  icon: string;
  description?: string;
  endpoint?: string;
}

interface Props {
  onSelectResult: (result: SearchResult) => void;
}

export function SearchBox({ onSelectResult }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const search = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      if (resp.ok) {
        const data = await resp.json();
        setResults(data.results || []);
        setOpen(true);
      }
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (value: string) => {
    setQuery(value);
    setFocusedIndex(-1);

    // Debounce
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => search(value), 300);
  };

  const handleSelect = (result: SearchResult) => {
    onSelectResult(result);
    setQuery('');
    setResults([]);
    setOpen(false);
    setFocusedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || results.length === 0) {
      if (e.key === 'Enter' && query.trim().length >= 2) {
        // Direct peer search
        handleSelect({
          id: query.trim(),
          label: query.trim(),
          type: 'peer',
          icon: '🧑‍💻',
          endpoint: `participants/${query.trim()}`,
        });
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedIndex((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusedIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (focusedIndex >= 0) {
        handleSelect(results[focusedIndex]);
      } else if (results.length > 0) {
        handleSelect(results[0]);
      }
    } else if (e.key === 'Escape') {
      setOpen(false);
      setFocusedIndex(-1);
    }
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (inputRef.current && !inputRef.current.parentElement?.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div className="relative">
      {/* Input */}
      <div className="flex items-center gap-1.5 px-2.5 py-[6px] bg-[#1a2332] rounded-md border border-[#2d3748] focus-within:border-sky-500/40 transition-colors">
        <svg className="w-3.5 h-3.5 text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="Peer, klaster, campus qidirish..."
          className="bg-transparent text-[12px] text-gray-300 placeholder:text-gray-600 outline-none w-full"
        />
        {loading && <Spinner className="w-3 h-3" />}
      </div>

      {/* Dropdown */}
      {open && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-[#141e2e] border border-[#2d3748] rounded-lg shadow-2xl overflow-hidden">
          {results.map((result, i) => (
            <button
              key={`${result.type}-${result.id}`}
              onClick={() => handleSelect(result)}
              className={`
                w-full flex items-center gap-2.5 px-3 py-2 text-left transition-colors
                ${i === focusedIndex ? 'bg-sky-500/10' : 'hover:bg-[#1a2332]'}
                ${i > 0 ? 'border-t border-[#1e293b]' : ''}
              `}
            >
              <span className="text-sm shrink-0">{result.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-[12px] text-gray-200 truncate">{result.label}</p>
                {result.description && (
                  <p className="text-[10px] text-gray-500 truncate">{result.description}</p>
                )}
              </div>
              <span className={`text-[9px] px-1.5 py-0.5 rounded shrink-0 ${
                result.type === 'peer' ? 'bg-sky-500/10 text-sky-400' :
                result.type === 'cluster' ? 'bg-emerald-500/10 text-emerald-400' :
                'bg-purple-500/10 text-purple-400'
              }`}>
                {result.type}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* No results */}
      {open && query.length >= 2 && results.length === 0 && !loading && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-[#141e2e] border border-[#2d3748] rounded-lg shadow-2xl px-3 py-3 text-center">
          <p className="text-[11px] text-gray-500">Natija topilmadi</p>
          <p className="text-[10px] text-gray-600 mt-0.5">Enter bosing &quot;{query}&quot; ni to&apos;g&apos;ridan-to&apos;g&apos;ri qidirish uchun</p>
        </div>
      )}
    </div>
  );
}
