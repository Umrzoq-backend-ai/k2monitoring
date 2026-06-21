import { NextRequest, NextResponse } from 'next/server';
import { getToken } from '../auth/route';

const BASE_URL = process.env.SCHOOL21_BASE_URL!;

const CAMPUSES = [
  { id: 'bad03b39-ffd4-4217-9d24-65535fe1f293', name: '21 Tashkent', type: 'campus' },
  { id: '667a42af-5469-4a33-9858-677d9d20956a', name: '21 Samarkand', type: 'campus' },
];

const TASHKENT_CLUSTERS = [
  { id: 36809, name: 'Andijan', campus: 'Tashkent' },
  { id: 36802, name: 'Bukhara', campus: 'Tashkent' },
  { id: 36808, name: 'Jizzakh', campus: 'Tashkent' },
  { id: 36803, name: 'Khiva', campus: 'Tashkent' },
  { id: 36804, name: 'Kokand', campus: 'Tashkent' },
  { id: 36807, name: 'Nukus', campus: 'Tashkent' },
  { id: 36801, name: 'Samarkand', campus: 'Tashkent' },
  { id: 36805, name: 'Shakhrisabz', campus: 'Tashkent' },
  { id: 36800, name: 'Tashkent', campus: 'Tashkent' },
  { id: 36806, name: 'Termez', campus: 'Tashkent' },
];

const SAMARKAND_CLUSTERS = [
  { id: 36735, name: 'Registan', campus: 'Samarkand' },
  { id: 36737, name: 'Sherdor', campus: 'Samarkand' },
  { id: 36738, name: 'Tillakori', campus: 'Samarkand' },
  { id: 36736, name: 'Ulugbek', campus: 'Samarkand' },
];

const ALL_CLUSTERS = [...TASHKENT_CLUSTERS, ...SAMARKAND_CLUSTERS];

export interface SearchResult {
  id: string;
  label: string;
  type: 'peer' | 'cluster' | 'campus';
  icon: string;
  description?: string;
  endpoint?: string;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = (searchParams.get('q') || '').trim().toLowerCase();

  if (!query || query.length < 2) {
    return NextResponse.json({ results: [] });
  }

  const results: SearchResult[] = [];

  // 1. Search campuses (local)
  for (const campus of CAMPUSES) {
    if (campus.name.toLowerCase().includes(query)) {
      results.push({
        id: campus.id,
        label: campus.name,
        type: 'campus',
        icon: '🏫',
        description: 'Campus',
        endpoint: `campuses/${campus.id}`,
      });
    }
  }

  // 2. Search clusters (local)
  for (const cluster of ALL_CLUSTERS) {
    if (cluster.name.toLowerCase().includes(query)) {
      results.push({
        id: String(cluster.id),
        label: cluster.name,
        type: 'cluster',
        icon: '🖥️',
        description: `${cluster.campus} campus`,
        endpoint: `clusters/${cluster.id}/map`,
      });
    }
  }

  // 3. Search peer (try direct API call)
  // First, try to fetch the exact login
  try {
    const token = await getToken();
    const resp = await fetch(`${BASE_URL}/participants/${query}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (resp.ok) {
      const data = await resp.json();
      results.push({
        id: query,
        label: data.login || query,
        type: 'peer',
        icon: '🧑‍💻',
        description: `Level ${data.level || '?'} • ${data.className || ''}`,
        endpoint: `participants/${query}`,
      });
    }
  } catch {
    // Not found — that's OK
  }

  // 4. If query is 3+ chars, also search in campus participants list
  if (query.length >= 3 && results.filter(r => r.type === 'peer').length === 0) {
    try {
      const token = await getToken();
      // Search in Tashkent participants
      const resp = await fetch(
        `${BASE_URL}/campuses/bad03b39-ffd4-4217-9d24-65535fe1f293/participants?limit=50&offset=0`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (resp.ok) {
        const data = await resp.json();
        const participants: string[] = data.participants || [];
        const matches = participants.filter((p: string) => p.toLowerCase().includes(query));
        for (const login of matches.slice(0, 5)) {
          results.push({
            id: login,
            label: login,
            type: 'peer',
            icon: '🧑‍💻',
            description: 'Tashkent campus',
            endpoint: `participants/${login}`,
          });
        }
      }
    } catch {
      // Ignore
    }
  }

  return NextResponse.json({ results: results.slice(0, 10) });
}
