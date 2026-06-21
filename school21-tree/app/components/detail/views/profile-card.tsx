interface Props {
  data: Record<string, any>;
}

export function ProfileCard({ data }: Props) {
  const xp = data.expValue || 0;
  const xpNext = data.expToNextLevel || 1;
  const progress = Math.min((xp / (xp + xpNext)) * 100, 100);

  return (
    <div className="space-y-5">
      {/* Level & XP */}
      <div className="bg-gradient-to-br from-sky-500/10 via-transparent to-emerald-500/5 p-5 rounded-xl border border-sky-500/20">
        <div className="flex items-end justify-between mb-4">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Level</p>
            <p className="text-4xl font-black text-sky-400">{data.level || 0}</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Experience</p>
            <p className="text-xl font-bold font-mono text-emerald-400">{xp.toLocaleString()}</p>
            <p className="text-[10px] text-gray-600">+{xpNext.toLocaleString()} keyingi levelga</p>
          </div>
        </div>
        <div className="h-2 bg-[#1a2332] rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-sky-500 to-emerald-400 rounded-full transition-all duration-700"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-[10px] text-gray-600 mt-1 text-right">{progress.toFixed(0)}%</p>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="Login" value={data.login} />
        <Field label="Class" value={data.className} />
        <Field label="Parallel" value={data.parallelName} />
        <Field label="Campus" value={data.campus?.shortName} />
        <Field label="Status" value={data.status} highlight={data.status === 'Active'} />
        {data.email && <Field label="Email" value={data.email} span />}
      </div>
    </div>
  );
}

function Field({ label, value, highlight, span }: { label: string; value: any; highlight?: boolean; span?: boolean }) {
  return (
    <div className={`bg-[#111827] rounded-lg p-3 border border-[#1e293b] ${span ? 'col-span-2' : ''}`}>
      <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">{label}</p>
      <p className={`text-sm font-medium ${highlight ? 'text-emerald-400' : 'text-gray-200'}`}>
        {value || '—'}
      </p>
    </div>
  );
}
