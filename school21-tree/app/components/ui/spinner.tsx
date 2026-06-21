export function Spinner({ className = '' }: { className?: string }) {
  return (
    <div className={`w-3.5 h-3.5 border-2 border-gray-700 border-t-emerald-400 rounded-full animate-spin ${className}`} />
  );
}
