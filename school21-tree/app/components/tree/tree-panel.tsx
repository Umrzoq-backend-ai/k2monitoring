'use client';

import { useMemo, useState, useCallback } from 'react';
import { TreeNode } from '../../lib/types';
import { buildRootTree, buildPeerNodes, buildClusterNodes } from '../../lib/tree-builder';
import { TreeNodeComponent } from './tree-node';
import { SearchBox } from './search-box';

interface Props {
  selectedId: string | null;
  onSelect: (node: TreeNode) => void;
}

export function TreePanel({ selectedId, onSelect }: Props) {
  const [extraNodes, setExtraNodes] = useState<TreeNode[]>([]);
  const rootNodes = useMemo(() => buildRootTree(), []);

  const handleSearchResult = useCallback((result: { id: string; label: string; type: string; icon: string; endpoint?: string }) => {
    if (result.type === 'peer') {
      // Add peer to tree and select their profile
      const login = result.id;
      const exists = extraNodes.find((n) => n.id === `peer:${login}`);
      if (!exists) {
        setExtraNodes((prev) => [
          {
            id: `peer:${login}`,
            label: login,
            icon: '🧑‍💻',
            children: buildPeerNodes(login),
            childrenLoaded: true,
          },
          ...prev,
        ]);
      }
      // Select their profile
      onSelect({
        id: `p:${login}:info`,
        label: 'Profil',
        icon: '📋',
        endpoint: `participants/${login}`,
      });
    } else if (result.type === 'cluster' && result.endpoint) {
      // Select cluster map
      onSelect({
        id: `search-cluster-${result.id}`,
        label: result.label,
        icon: '🗺️',
        endpoint: result.endpoint,
      });
    } else if (result.type === 'campus' && result.endpoint) {
      // Select campus info
      onSelect({
        id: `search-campus-${result.id}`,
        label: result.label,
        icon: '🏫',
        endpoint: result.endpoint,
      });
    }
  }, [extraNodes, onSelect]);

  return (
    <aside className="w-[280px] min-w-[240px] flex flex-col border-r border-[#1e293b] bg-[#0f1623] select-none">
      {/* Header + Search */}
      <div className="px-3 py-2.5 border-b border-[#1e293b] space-y-2">
        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
          Explorer
        </p>
        <SearchBox onSelectResult={handleSearchResult} />
      </div>

      {/* Tree */}
      <nav className="flex-1 overflow-y-auto py-1 scrollbar-thin" role="tree" aria-label="School21 Explorer">
        <ul>
          {/* Search results / extra nodes */}
          {extraNodes.map((node) => (
            <TreeNodeComponent
              key={node.id}
              node={node}
              depth={0}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
          {/* Separator if extras exist */}
          {extraNodes.length > 0 && (
            <li className="h-px bg-[#1e293b] my-1 mx-3" aria-hidden />
          )}
          {/* Root tree */}
          {rootNodes.map((node) => (
            <TreeNodeComponent
              key={node.id}
              node={node}
              depth={0}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-[#1e293b]">
        <p className="text-[10px] text-gray-600">rrangesi • Tashkent & Samarkand</p>
      </div>
    </aside>
  );
}
