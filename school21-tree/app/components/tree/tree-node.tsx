'use client';

import { memo, useState, useCallback } from 'react';
import { TreeNode as TreeNodeType } from '../../lib/types';
import { resolveChildren } from '../../lib/tree-resolver';
import { Spinner } from '../ui/spinner';

interface Props {
  node: TreeNodeType;
  depth: number;
  selectedId: string | null;
  onSelect: (node: TreeNodeType) => void;
}

function TreeNodeInner({ node, depth, selectedId, onSelect }: Props) {
  const [expanded, setExpanded] = useState(depth === 0);
  const [children, setChildren] = useState<TreeNodeType[] | undefined>(node.children);
  const [loaded, setLoaded] = useState(node.childrenLoaded ?? false);
  const [loading, setLoading] = useState(false);

  const isBranch = children !== undefined;
  const isLeaf = !!node.endpoint && !isBranch;
  const isHybrid = !!node.endpoint && isBranch; // has both endpoint and children
  const isSelected = selectedId === node.id;

  const toggle = useCallback(async () => {
    // Hybrid node: click selects it AND toggles expand
    if (isHybrid) {
      onSelect(node);
      if (!loaded && !loading) {
        setLoading(true);
        try {
          const result = await resolveChildren(node.id);
          setChildren(result);
          setLoaded(true);
          setExpanded(true);
        } catch {
          setChildren([]);
          setLoaded(true);
        } finally {
          setLoading(false);
        }
      } else {
        setExpanded((e) => !e);
      }
      return;
    }

    if (isLeaf) {
      onSelect(node);
      return;
    }

    if (!loaded && !loading) {
      setLoading(true);
      try {
        const result = await resolveChildren(node.id);
        setChildren(result);
        setLoaded(true);
        setExpanded(true);
      } catch {
        setChildren([]);
        setLoaded(true);
      } finally {
        setLoading(false);
      }
    } else {
      setExpanded((e) => !e);
    }
  }, [isLeaf, isHybrid, loaded, loading, node, onSelect]);

  return (
    <li role="treeitem" aria-expanded={isBranch ? expanded : undefined} aria-selected={isSelected}>
      {/* Row */}
      <div
        onClick={toggle}
        className={`
          relative flex items-center h-[28px] cursor-pointer
          transition-colors duration-75 group
          hover:bg-[#1c2536]
          ${isSelected ? 'bg-[#1a3352]' : ''}
        `}
        style={{ paddingLeft: `${depth * 14 + 10}px` }}
      >
        {isSelected && <div className="absolute inset-y-0 left-0 w-[2px] bg-sky-400" />}

        {/* Chevron / Loading */}
        <span className="w-4 h-4 flex items-center justify-center shrink-0">
          {loading && <Spinner />}
          {!loading && isBranch && (
            <svg
              className={`w-3 h-3 text-gray-500 transition-transform duration-150 ${expanded ? 'rotate-90' : ''}`}
              viewBox="0 0 16 16" fill="currentColor"
            >
              <path d="M6 3l5 5-5 5V3z" />
            </svg>
          )}
        </span>

        {/* Icon */}
        <span className="text-[13px] mr-1.5 shrink-0">{node.icon}</span>

        {/* Label */}
        <span className={`text-[12.5px] truncate leading-none ${
          isSelected ? 'text-white' : 'text-[#cdd6e4] group-hover:text-white'
        }`}>
          {node.label}
        </span>
      </div>

      {/* Children */}
      {isBranch && expanded && children && children.length > 0 && (
        <ul role="group" className="relative">
          {/* Indent guide line */}
          <div
            className="absolute top-0 bottom-0 w-px bg-[#2d3748]"
            style={{ left: `${depth * 14 + 20}px` }}
          />
          {children.map((child) => (
            <TreeNodeInner
              key={child.id}
              node={child}
              depth={depth + 1}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}

      {/* Empty */}
      {isBranch && expanded && loaded && (!children || children.length === 0) && (
        <div
          className="h-6 flex items-center text-[11px] text-gray-600 italic"
          style={{ paddingLeft: `${(depth + 1) * 14 + 30}px` }}
        >
          bo&apos;sh
        </div>
      )}
    </li>
  );
}

export const TreeNodeComponent = memo(TreeNodeInner);
