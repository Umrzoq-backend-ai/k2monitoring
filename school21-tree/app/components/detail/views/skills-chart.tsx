interface Skill {
  name: string;
  points: number;
}

interface Props {
  skills: Skill[];
}

export function SkillsChart({ skills }: Props) {
  const sorted = [...skills].sort((a, b) => b.points - a.points);
  const max = sorted[0]?.points || 1;
  const total = sorted.reduce((sum, s) => sum + s.points, 0);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center gap-4 mb-2">
        <div className="bg-[#111827] rounded-lg px-3 py-2 border border-[#1e293b]">
          <p className="text-[10px] text-gray-500">Skills</p>
          <p className="text-lg font-bold text-sky-400">{skills.length}</p>
        </div>
        <div className="bg-[#111827] rounded-lg px-3 py-2 border border-[#1e293b]">
          <p className="text-[10px] text-gray-500">Jami XP</p>
          <p className="text-lg font-bold text-emerald-400">{total.toLocaleString()}</p>
        </div>
      </div>

      {/* Bars */}
      <div className="space-y-2.5">
        {sorted.map((skill) => {
          const pct = (skill.points / max) * 100;
          return (
            <div key={skill.name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[12px] text-gray-300">{skill.name}</span>
                <span className="text-[11px] font-mono text-gray-500">{skill.points}</span>
              </div>
              <div className="h-[6px] bg-[#1a2332] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-sky-500 to-emerald-400 transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
