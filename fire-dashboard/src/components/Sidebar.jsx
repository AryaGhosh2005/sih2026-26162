import React from "react";
import {
  RotateCcw,
  CalendarDays,
  ShieldAlert,
  Radio,
  Target,
  Thermometer,
  Factory,
  Satellite,
  Database,
  Activity,
  Check,
} from "lucide-react";

import { RISK_OPTIONS, SOURCE_TYPES } from "../constants";

function SectionLabel({ icon: Icon, children }) {
  return (
    <div className="flex items-center gap-2 mt-5 mb-2.5">
      <Icon size={12} className="text-cyan-400 shrink-0" />

      <span className="text-[9px] font-bold tracking-[0.18em] uppercase text-slate-400">
        {children}
      </span>

      <span className="flex-1 h-px bg-white/[0.07]" />
    </div>
  );
}

function CheckboxRow({ checked, onChange, label }) {
  return (
    <label className="group flex items-center gap-2.5 px-2 py-1.5 rounded-lg cursor-pointer transition-all duration-200 hover:bg-white/[0.04]">
      <span
        className={`relative flex items-center justify-center w-3.5 h-3.5 rounded border transition-all ${
          checked
            ? "bg-cyan-400/20 border-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.25)]"
            : "bg-black/20 border-white/15 group-hover:border-white/30"
        }`}
      >
        {checked && (
          <Check
            size={10}
            strokeWidth={3}
            className="text-cyan-300"
          />
        )}

        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />
      </span>

      <span
        className={`text-[10px] transition-colors ${
          checked
            ? "text-slate-200"
            : "text-slate-500 group-hover:text-slate-300"
        }`}
      >
        {label}
      </span>
    </label>
  );
}

function toggle(list, value) {
  return list.includes(value)
    ? list.filter((v) => v !== value)
    : [...list, value];
}

export default function Sidebar({
  filters,
  setFilters,
  dataStatus,
  onRefresh,
  satellites,
}) {
  const f = filters;

  const update = (patch) =>
    setFilters((prev) => ({
      ...prev,
      ...patch,
    }));

  return (
    <aside
      className="
        h-full w-full overflow-y-auto
        px-3.5 py-4
        text-slate-200
        rounded-2xl
        border border-white/[0.10]
        bg-[#07101a]/85
        backdrop-blur-xl
        shadow-[0_20px_60px_rgba(0,0,0,0.45)]
        scrollbar-thin
      "
    >
      {/* =========================================
          COMMAND CENTER IDENTITY
      ========================================== */}
      <div className="relative pb-4 mb-2 border-b border-white/[0.08]">
        <div className="absolute left-0 top-0 w-1 h-10 rounded-full bg-cyan-400 shadow-[0_0_14px_rgba(34,211,238,0.7)]" />

        <div className="pl-3">
          <div className="text-[15px] font-black tracking-[0.08em] text-white">
            CONTROL
          </div>

          <div className="text-[15px] font-black tracking-[0.08em] text-white">
            PANEL
          </div>

          <div className="mt-1 text-[8px] tracking-[0.14em] uppercase text-slate-500">
            SIH 26162 · Fire Detection
          </div>
        </div>

        <div className="absolute right-0 top-0 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />

          <span className="text-[7px] tracking-wider text-emerald-400">
            ONLINE
          </span>
        </div>
      </div>

      {/* =========================================
          DATE RANGE
      ========================================== */}
      <SectionLabel icon={CalendarDays}>
        DATE RANGE
      </SectionLabel>

      <div className="grid grid-cols-2 gap-1.5">
        <div className="relative">
          <input
            type="date"
            value={f.startDate}
            max={f.endDate}
            onChange={(e) =>
              update({ startDate: e.target.value })
            }
            className="
              w-full
              bg-black/20
              border border-white/[0.10]
              rounded-lg
              text-[9px]
              text-slate-200
              px-2 py-2
              outline-none
              focus:border-cyan-400/50
              focus:ring-1
              focus:ring-cyan-400/20
              transition
            "
          />
        </div>

        <div className="relative">
          <input
            type="date"
            value={f.endDate}
            min={f.startDate}
            onChange={(e) =>
              update({ endDate: e.target.value })
            }
            className="
              w-full
              bg-black/20
              border border-white/[0.10]
              rounded-lg
              text-[9px]
              text-slate-200
              px-2 py-2
              outline-none
              focus:border-cyan-400/50
              focus:ring-1
              focus:ring-cyan-400/20
              transition
            "
          />
        </div>
      </div>

      {/* =========================================
          RISK LEVEL
      ========================================== */}
      <SectionLabel icon={ShieldAlert}>
        RISK LEVEL
      </SectionLabel>

      <div className="space-y-0.5">
        {RISK_OPTIONS.map((opt) => (
          <CheckboxRow
            key={opt.key}
            label={opt.label}
            checked={f.selectedRiskKeys.includes(opt.key)}
            onChange={() =>
              update({
                selectedRiskKeys: toggle(
                  f.selectedRiskKeys,
                  opt.key
                ),
              })
            }
          />
        ))}
      </div>

      {/* =========================================
          SOURCE TYPE
      ========================================== */}
      <SectionLabel icon={Radio}>
        SOURCE TYPE
      </SectionLabel>

      <div className="space-y-0.5">
        {SOURCE_TYPES.map((type) => (
          <CheckboxRow
            key={type}
            label={type}
            checked={f.selectedSources.includes(type)}
            onChange={() =>
              update({
                selectedSources: toggle(
                  f.selectedSources,
                  type
                ),
              })
            }
          />
        ))}
      </div>

      {/* =========================================
          CONFIDENCE
      ========================================== */}
      <SectionLabel icon={Target}>
        CONFIDENCE
      </SectionLabel>

      <div className="px-1">
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={f.minConfidence}
          onChange={(e) =>
            update({
              minConfidence: Number(e.target.value),
            })
          }
          className="w-full accent-cyan-400 cursor-pointer"
        />

        <div className="flex justify-between mt-1">
          <span className="text-[8px] text-slate-500">
            MINIMUM
          </span>

          <span className="text-[9px] font-semibold text-cyan-300">
            {f.minConfidence}%
          </span>
        </div>
      </div>

      {/* =========================================
          THERMAL INTENSITY
      ========================================== */}
      <SectionLabel icon={Thermometer}>
        THERMAL INTENSITY
      </SectionLabel>

      <div className="px-1">
        <input
          type="range"
          min={280}
          max={380}
          step={5}
          value={f.minBrightness}
          onChange={(e) =>
            update({
              minBrightness: Number(e.target.value),
            })
          }
          className="w-full accent-orange-400 cursor-pointer"
        />

        <div className="flex justify-between mt-1">
          <span className="text-[8px] text-slate-500">
            MINIMUM
          </span>

          <span className="text-[9px] font-semibold text-orange-300">
            {f.minBrightness} K
          </span>
        </div>
      </div>

      {/* =========================================
          INDUSTRIAL PROXIMITY
      ========================================== */}
      <SectionLabel icon={Factory}>
        INDUSTRIAL PROXIMITY
      </SectionLabel>

      <div className="px-1">
        <input
          type="range"
          min={1}
          max={f.dataMaxDistance}
          step={1}
          value={f.maxDistance}
          onChange={(e) =>
            update({
              maxDistance: Number(e.target.value),
            })
          }
          className="w-full accent-emerald-400 cursor-pointer"
        />

        <div className="flex justify-between mt-1">
          <span className="text-[8px] text-slate-500">
            MAX RANGE
          </span>

          <span className="text-[9px] font-semibold text-emerald-300">
            {f.maxDistance} km
          </span>
        </div>
      </div>

      {/* =========================================
          SATELLITE
      ========================================== */}
      <SectionLabel icon={Satellite}>
        SATELLITE
      </SectionLabel>

      <div className="space-y-0.5">
        {satellites.map((sat) => (
          <CheckboxRow
            key={sat}
            label={sat}
            checked={f.selectedSatellites.includes(sat)}
            onChange={() =>
              update({
                selectedSatellites: toggle(
                  f.selectedSatellites,
                  sat
                ),
              })
            }
          />
        ))}
      </div>

      {/* =========================================
          DATA STATUS
      ========================================== */}
      <SectionLabel icon={Database}>
        DATA STATUS
      </SectionLabel>

      <div className="rounded-xl border border-white/[0.07] bg-black/20 overflow-hidden">
        <div className="flex justify-between items-center px-3 py-2 border-b border-white/[0.06]">
          <span className="text-[8px] text-slate-500">
            RECORDS LOADED
          </span>

          <span className="text-[10px] font-bold text-white">
            {dataStatus.total.toLocaleString()}
          </span>
        </div>

        <div className="flex justify-between items-center px-3 py-2 border-b border-white/[0.06]">
          <span className="text-[8px] text-slate-500">
            AUTO-REFRESH
          </span>

          <span className="text-[9px] font-semibold text-slate-300">
            5 MIN
          </span>
        </div>

        <div className="flex justify-between items-center px-3 py-2">
          <span className="flex items-center gap-1.5 text-[8px] text-slate-500">
            <Activity size={9} />
            CACHE STATUS
          </span>

          <span className="flex items-center gap-1 text-[8px] font-bold text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
            ACTIVE
          </span>
        </div>
      </div>

      {/* =========================================
          REFRESH
      ========================================== */}
      <button
        onClick={onRefresh}
        className="
          mt-4
          w-full
          flex items-center justify-center gap-2
          rounded-xl
          border border-cyan-400/20
          bg-cyan-400/[0.06]
          text-cyan-300
          text-[9px]
          font-bold
          tracking-[0.12em]
          py-2.5
          hover:bg-cyan-400/[0.12]
          hover:border-cyan-400/40
          hover:text-cyan-200
          hover:shadow-[0_0_18px_rgba(34,211,238,0.12)]
          transition-all duration-200
        "
      >
        <RotateCcw size={12} />
        REFRESH DATA
      </button>

      {/* =========================================
          BOTTOM STATUS
      ========================================== */}
      <div className="mt-3 flex items-center justify-center gap-1.5">
        <span className="w-1 h-1 rounded-full bg-cyan-400" />

        <span className="text-[7px] tracking-[0.18em] text-slate-600">
          SYSTEM FILTERS ACTIVE
        </span>

        <span className="w-1 h-1 rounded-full bg-cyan-400" />
      </div>
    </aside>
  );
}