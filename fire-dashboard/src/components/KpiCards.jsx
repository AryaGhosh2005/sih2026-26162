import React, { useMemo } from "react";
import {
  Flame,
  Activity,
  AlertTriangle,
  Layers3,
  Factory,
} from "lucide-react";

function getRiskCount(fires) {
  return fires.filter((f) => {
    const risk = String(f.risk_level || "").toLowerCase();
    return risk === "high" || risk === "critical";
  }).length;
}

function KpiCard({
  icon: Icon,
  label,
  value,
  accent,
  glow,
  gradient,
  subtitle,
}) {
  return (
    <div
      className="
        group relative overflow-hidden
        rounded-xl
        border
        bg-[#07101b]/80
        backdrop-blur-xl
        px-4 py-3.5
        transition-all duration-300
        hover:-translate-y-[2px]
      "
      style={{
        borderColor: `${accent}55`,
        boxShadow: `
          0 0 14px ${accent}18,
          0 0 30px ${accent}0c,
          inset 0 1px 0 rgba(255,255,255,0.07)
        `,
      }}
    >
      <div
        className="
          pointer-events-none
          absolute inset-0
          rounded-xl
          opacity-80
        "
        style={{
          padding: "1px",
          background: gradient,
          WebkitMask:
            "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
        }}
      />

      <div
        className="
          pointer-events-none
          absolute
          -right-10
          -top-10
          h-28
          w-28
          rounded-full
          blur-3xl
          opacity-20
        "
        style={{ backgroundColor: accent }}
      />

      <div
        className="
          pointer-events-none
          absolute
          -bottom-12
          -left-10
          h-24
          w-24
          rounded-full
          blur-3xl
          opacity-[0.08]
        "
        style={{ backgroundColor: accent }}
      />

      <div
        className="
          pointer-events-none
          absolute
          left-6
          right-6
          top-0
          h-px
          opacity-70
        "
        style={{ background: gradient }}
      />

      <div
        className="
          pointer-events-none
          absolute
          inset-x-0
          top-0
          h-12
          opacity-[0.035]
        "
        style={{
          background:
            "linear-gradient(to bottom, rgba(255,255,255,0.9), transparent)",
        }}
      />

      <div className="relative z-10 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Icon
              size={13}
              strokeWidth={2}
              style={{ color: accent }}
              className="opacity-90"
            />

            <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-400">
              {label}
            </span>
          </div>

          <div className="mt-1.5 text-[28px] leading-none font-bold tracking-tight text-white">
            {value}
          </div>

          <div className="mt-2 text-[9px] font-medium text-slate-500">
            {subtitle}
          </div>
        </div>

        <div
          className="
            flex
            h-9
            w-9
            shrink-0
            items-center
            justify-center
            rounded-lg
            border
            bg-white/[0.025]
            transition-all
            duration-300
            group-hover:bg-white/[0.06]
          "
          style={{
            borderColor: `${accent}35`,
            color: accent,
            boxShadow: `inset 0 0 12px ${accent}08`,
          }}
        >
          <Icon size={17} strokeWidth={1.8} />
        </div>
      </div>

      <div
        className="
          pointer-events-none
          absolute
          bottom-0
          left-0
          right-0
          h-px
          opacity-50
        "
        style={{ background: gradient }}
      />
    </div>
  );
}

export default function KpiCards({ filtered, allFires }) {
  const stats = useMemo(() => {
    const activeEvents = filtered.length;

    const highRisk = getRiskCount(filtered);

    const persistentSources = filtered.filter(
      (f) =>
        f.is_persistent === true ||
        f.persistent === true ||
        String(f.persistence || "").toLowerCase() === "persistent"
    ).length;

    const industrialProximity = filtered.filter((f) => {
      const distance = Number(f.distance_to_industry);
      return !Number.isNaN(distance) && distance <= 50;
    }).length;

    const totalDetections = allFires.length;

    return {
      activeEvents,
      highRisk,
      persistentSources,
      industrialProximity,
      totalDetections,
    };
  }, [filtered, allFires]);

  return (
    <div className="grid grid-cols-5 gap-3">

      <KpiCard
        icon={Flame}
        label="Total Detections"
        value={stats.totalDetections}
        subtitle="No change today"
        accent="#ff3b4f"
        glow="bg-red-500"
        gradient="
          linear-gradient(
            120deg,
            rgba(255,45,70,0.95),
            rgba(255,80,40,0.65),
            rgba(255,130,0,0.45)
          )
        "
      />

      <KpiCard
        icon={Activity}
        label="Active Events"
        value={stats.activeEvents}
        subtitle="Live monitoring"
        accent="#00d9ff"
        glow="bg-cyan-400"
        gradient="
          linear-gradient(
            120deg,
            rgba(0,225,255,0.95),
            rgba(0,145,255,0.65),
            rgba(80,90,255,0.55)
          )
        "
      />

      <KpiCard
        icon={AlertTriangle}
        label="High Risk"
        value={stats.highRisk}
        subtitle="Requires attention"
        accent="#ffad24"
        glow="bg-amber-400"
        gradient="
          linear-gradient(
            120deg,
            rgba(255,210,40,0.95),
            rgba(255,155,0,0.75),
            rgba(255,75,20,0.55)
          )
        "
      />

      <KpiCard
        icon={Layers3}
        label="Persistent Sources"
        value={stats.persistentSources}
        subtitle="Thermal persistence"
        accent="#b45cff"
        glow="bg-purple-400"
        gradient="
          linear-gradient(
            120deg,
            rgba(190,80,255,0.95),
            rgba(125,65,255,0.70),
            rgba(75,80,255,0.50)
          )
        "
      />

      <KpiCard
        icon={Factory}
        label="Industrial Proximity"
        value={stats.industrialProximity}
        subtitle="Within 50 km"
        accent="#00e6a0"
        glow="bg-emerald-400"
        gradient="
          linear-gradient(
            120deg,
            rgba(0,240,165,0.95),
            rgba(0,205,125,0.65),
            rgba(0,180,235,0.55)
          )
        "
      />

    </div>
  );
}

export function SectionTitle({ children, icon: Icon }) {
  return (
    <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/70">
      {Icon && (
        <Icon
          size={12}
          strokeWidth={2}
          className="text-cyan-400"
        />
      )}

      <span>{children}</span>

      <div className="h-px flex-1 bg-white/[0.06]" />
    </div>
  );
}