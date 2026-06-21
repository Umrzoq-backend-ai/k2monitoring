'use client';

import { TreeNode } from '../../lib/types';
import { Spinner } from '../ui/spinner';
import { ProfileCard } from './views/profile-card';
import { SkillsChart } from './views/skills-chart';
import { ProjectsList } from './views/projects-list';
import { PointsCard } from './views/points-card';
import { ClusterMapGrid } from './views/cluster-map';
import { GenericView } from './views/generic-view';

interface Props {
  node: TreeNode | null;
  data: unknown;
  loading: boolean;
  error: string | null;
  onPeerClick?: (login: string) => void;
}

export function DetailPanel({ node, data, loading, error, onPeerClick }: Props) {
  // Empty state
  if (!node) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-600">
        <span className="text-6xl opacity-40 mb-4">🌳</span>
        <p className="text-sm text-gray-500">Daraxtdan element tanlang</p>
      </div>
    );
  }

  // Loading
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full gap-2.5">
        <Spinner className="w-5 h-5" />
        <span className="text-sm text-gray-400">Yuklanmoqda...</span>
      </div>
    );
  }

  // Error
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-2">
        <span className="text-3xl">⚠️</span>
        <p className="text-sm text-red-400">{error}</p>
        <p className="text-[10px] text-gray-600 font-mono">{node.endpoint}</p>
      </div>
    );
  }

  if (!data) return null;

  const endpoint = node.endpoint || '';

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="px-5 py-3 border-b border-[#1e293b] shrink-0 flex items-center gap-2.5">
        <span className="text-lg">{node.icon}</span>
        <div className="min-w-0">
          <h2 className="text-sm font-semibold text-white truncate">{node.label}</h2>
          <p className="text-[10px] text-gray-600 font-mono truncate">{endpoint}</p>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
        <DetailBody endpoint={endpoint} data={data} onPeerClick={onPeerClick} />
      </div>
    </div>
  );
}

function DetailBody({ endpoint, data, onPeerClick }: { endpoint: string; data: unknown; onPeerClick?: (login: string) => void }) {
  // Cluster map
  if (endpoint.match(/clusters\/\d+\/map/) && isObj(data) && 'clusterMap' in data) {
    // Extract cluster name from endpoint
    return <ClusterMapGrid clusterMap={(data as any).clusterMap} onPeerClick={onPeerClick} />;
  }

  // Route to specialized views based on endpoint pattern
  if (endpoint.match(/^participants\/[^/]+$/) && isObj(data) && 'login' in data) {
    return <ProfileCard data={data as Record<string, any>} />;
  }

  if (endpoint.endsWith('/skills') && isObj(data) && 'skills' in data) {
    return <SkillsChart skills={(data as any).skills} />;
  }

  if (endpoint.endsWith('/projects') && isObj(data) && 'projects' in data) {
    return <ProjectsList projects={(data as any).projects} />;
  }

  if (endpoint.endsWith('/points') && isObj(data)) {
    return <PointsCard data={data as Record<string, any>} />;
  }

  if (endpoint.endsWith('/logtime') && typeof data === 'number') {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <span className="text-6xl font-bold text-emerald-400">{data}</span>
        <span className="text-sm text-gray-500 mt-2">soat (bugungi logtime)</span>
      </div>
    );
  }

  // Fallback
  return <GenericView data={data} />;
}

function isObj(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}
