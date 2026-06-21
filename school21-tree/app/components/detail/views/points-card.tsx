interface Props {
  data: Record<string, any>;
}

export function PointsCard({ data }: Props) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <Stat icon="🔄" label="Peer Review" value={data.peerReviewPoints} color="text-purple-400" />
      <Stat icon="🪙" label="Coins" value={data.coins} color="text-amber-400" />
      <Stat icon="📝" label="Code Review" value={data.codeReviewPoints} color="text-sky-400" />
    </div>
  );
}

function Stat({ icon, label, value, color }: { icon: string; label: string; value: any; color: string }) {
  return (
    <div className="bg-[#111827] rounded-xl p-4 border border-[#1e293b] text-center">
      <span className="text-2xl">{icon}</span>
      <p className={`text-2xl font-bold mt-2 ${color}`}>{value ?? '—'}</p>
      <p className="text-[10px] text-gray-500 mt-1">{label}</p>
    </div>
  );
}
