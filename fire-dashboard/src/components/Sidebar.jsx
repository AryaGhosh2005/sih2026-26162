import React from "react";
import { RotateCcw } from "lucide-react";
import { RISK_OPTIONS, SOURCE_TYPES } from "../constants";

function SectionLabel({ children }) {
  return (
    <div className="flex items-center gap-1.5 text-[#6d7c93] text-[10px] font-bold tracking-wider mt-4 mb-2">
      {children}
      <span className="flex-1 h-px bg-[#161f2c]" />
    </div>
  );
}

function CheckboxRow({ checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 text-[11px] text-[#9aa6ba] py-0.5 cursor-pointer hover:text-[#dce4ee]">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="accent-[#24aef5] w-3.5 h-3.5"
      />
      {label}
    </label>
  );
}

function toggle(list, value) {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}

export default function Sidebar({ filters, setFilters, dataStatus, onRefresh, satellites }) {
  const f = filters;

  const update = (patch) => setFilters((prev) => ({ ...prev, ...patch }));

  return (
    <aside className="bg-[#070b13] border-r border-[#18202d] h-full px-4 py-5 overflow-y-auto text-[#dce3ed]">
      <div className="pb-2 mb-2 border-b border-[#18212f]">
        <div className="text-white text-[21px] font-extrabold tracking-wide">CONTROL PANEL</div>
        <div className="text-[#62708a] text-[12px] tracking-wide">SIH 26162 &middot; Fire Detection</div>
      </div>

      <SectionLabel>📅 DATE RANGE</SectionLabel>
      <div className="flex gap-2">
        <input
          type="date"
          value={f.startDate}
          max={f.endDate}
          onChange={(e) => update({ startDate: e.target.value })}
          className="w-1/2 bg-[#080d15] border border-[#273445] rounded-md text-[11px] text-white px-2 py-1.5"
        />
        <input
          type="date"
          value={f.endDate}
          min={f.startDate}
          onChange={(e) => update({ endDate: e.target.value })}
          className="w-1/2 bg-[#080d15] border border-[#273445] rounded-md text-[11px] text-white px-2 py-1.5"
        />
      </div>

      <SectionLabel>⚠ RISK LEVEL</SectionLabel>
      {RISK_OPTIONS.map((opt) => (
        <CheckboxRow
          key={opt.key}
          label={opt.label}
          checked={f.selectedRiskKeys.includes(opt.key)}
          onChange={() => update({ selectedRiskKeys: toggle(f.selectedRiskKeys, opt.key) })}
        />
      ))}

      <SectionLabel>📡 SOURCE TYPE</SectionLabel>
      {SOURCE_TYPES.map((type) => (
        <CheckboxRow
          key={type}
          label={type}
          checked={f.selectedSources.includes(type)}
          onChange={() => update({ selectedSources: toggle(f.selectedSources, type) })}
        />
      ))}

      <SectionLabel>🎯 CONFIDENCE</SectionLabel>
      <input
        type="range"
        min={0}
        max={100}
        step={5}
        value={f.minConfidence}
        onChange={(e) => update({ minConfidence: Number(e.target.value) })}
        className="w-full"
      />
      <div className="text-[10px] text-[#9aa6ba] mt-1">Min {f.minConfidence}%</div>

      <SectionLabel>🌡 THERMAL INTENSITY</SectionLabel>
      <input
        type="range"
        min={280}
        max={380}
        step={5}
        value={f.minBrightness}
        onChange={(e) => update({ minBrightness: Number(e.target.value) })}
        className="w-full"
      />
      <div className="text-[10px] text-[#9aa6ba] mt-1">Min {f.minBrightness} K</div>

      <SectionLabel>🏭 INDUSTRIAL PROXIMITY</SectionLabel>
      <input
        type="range"
        min={1}
        max={f.dataMaxDistance}
        step={1}
        value={f.maxDistance}
        onChange={(e) => update({ maxDistance: Number(e.target.value) })}
        className="w-full"
      />
      <div className="text-[10px] text-[#9aa6ba] mt-1">Max {f.maxDistance} km</div>

      <SectionLabel>🛰 SATELLITE</SectionLabel>
      {satellites.map((sat) => (
        <CheckboxRow
          key={sat}
          label={sat}
          checked={f.selectedSatellites.includes(sat)}
          onChange={() => update({ selectedSatellites: toggle(f.selectedSatellites, sat) })}
        />
      ))}

      <SectionLabel>📊 DATA STATUS</SectionLabel>
      <div className="flex justify-between text-[10px] py-1.5 border-b border-[#131b28]">
        <span className="text-[#6d7c93]">Records Loaded</span>
        <span className="text-[#dfe6f0] font-semibold">{dataStatus.total.toLocaleString()}</span>
      </div>
      <div className="flex justify-between text-[10px] py-1.5 border-b border-[#131b28]">
        <span className="text-[#6d7c93]">Auto-refresh</span>
        <span className="text-[#dfe6f0] font-semibold">Every 5 min</span>
      </div>
      <div className="flex justify-between text-[10px] py-1.5 border-b border-[#131b28]">
        <span className="text-[#6d7c93]">Cache Status</span>
        <span className="text-[#35cf66] font-bold">● Active</span>
      </div>

      <button
        onClick={onRefresh}
        className="mt-4 w-full flex items-center justify-center gap-2 bg-[#0d141f] border border-[#283446] text-[#dce4ee] rounded-md text-xs font-semibold py-2 hover:border-[#159eea] hover:text-white transition-colors"
      >
        <RotateCcw size={13} /> REFRESH DATA
      </button>
    </aside>
  );
}
