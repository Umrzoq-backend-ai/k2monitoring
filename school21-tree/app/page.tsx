'use client';

import { useState, useCallback } from 'react';
import { TreePanel } from './components/tree/tree-panel';
import { DetailPanel } from './components/detail/detail-panel';
import { TreeNode } from './lib/types';
import { fetchApi } from './lib/api';

export default function Page() {
  const [selected, setSelected] = useState<TreeNode | null>(null);
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = useCallback(async (node: TreeNode) => {
    if (!node.endpoint) return;

    setSelected(node);
    setData(null);
    setError(null);
    setLoading(true);

    try {
      const result = await fetchApi(node.endpoint);
      setData(result);
    } catch (e: any) {
      setError(e.message || 'Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  }, []);

  const handlePeerClick = useCallback(async (login: string) => {
    // When a peer is clicked from cluster map, show their profile
    const node: TreeNode = {
      id: `peer-map-${login}`,
      label: login,
      icon: '🧑‍💻',
      endpoint: `participants/${login}`,
    };
    handleSelect(node);
  }, [handleSelect]);

  return (
    <div className="flex h-screen overflow-hidden bg-[#0b1120]">
      <TreePanel selectedId={selected?.id || null} onSelect={handleSelect} />
      <main className="flex-1 overflow-hidden border-l border-[#1e293b]">
        <DetailPanel node={selected} data={data} loading={loading} error={error} onPeerClick={handlePeerClick} />
      </main>
    </div>
  );
}
