//Sidebar.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
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
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

import { RISK_OPTIONS, SOURCE_TYPES } from "../constants";

/* =========================================================
   HELPERS
========================================================= */

function parseDate(value) {
  if (!value) return new Date();

  const [year, month, day] = value.split("-").map(Number);

  return new Date(year, month - 1, day);
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function formatDisplayDate(value) {
  if (!value) return "-- / -- / ----";

  const [year, month, day] = value.split("-");

  return `${day} / ${month} / ${year}`;
}

function isSameDay(a, b) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

/* =========================================================
   SECTION LABEL
========================================================= */

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

/* =========================================================
   CHECKBOX
========================================================= */

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

/* =========================================================
   TOGGLE HELPER
========================================================= */

function toggle(list, value) {
  return list.includes(value)
    ? list.filter((v) => v !== value)
    : [...list, value];
}

/* =========================================================
   CUSTOM CALENDAR
========================================================= */

function CalendarPopup({
  value,
  min,
  max,
  anchorRect,
  onSelect,
  onClose,
}) {
  const initialDate = parseDate(value);

  const [viewDate, setViewDate] = useState(
    new Date(initialDate.getFullYear(), initialDate.getMonth(), 1)
  );

  const popupRef = useRef(null);

  const [position, setPosition] = useState({
    top: 0,
    left: 0,
  });

  /* -------------------------------------------------------
     POSITION POPUP OUTSIDE SIDEBAR
  ------------------------------------------------------- */

  useEffect(() => {
    if (!anchorRect) return;

    const popupWidth = 304;
    const popupHeight = 365;
    const gap = 8;

    let left = anchorRect.left;

    if (left + popupWidth > window.innerWidth - 8) {
      left = window.innerWidth - popupWidth - 8;
    }

    if (left < 8) {
      left = 8;
    }

    let top = anchorRect.bottom + gap;

    if (top + popupHeight > window.innerHeight - 8) {
      top = anchorRect.top - popupHeight - gap;
    }

    if (top < 8) {
      top = 8;
    }

    setPosition({
      top,
      left,
    });
  }, [anchorRect]);

  /* -------------------------------------------------------
     CLOSE ON OUTSIDE CLICK
  ------------------------------------------------------- */

  useEffect(() => {
    function handleOutside(event) {
      if (
        popupRef.current &&
        !popupRef.current.contains(event.target)
      ) {
        onClose();
      }
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("mousedown", handleOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [onClose]);

  /* -------------------------------------------------------
     KEEP POSITION CORRECT ON RESIZE
  ------------------------------------------------------- */

  useEffect(() => {
    const handleResize = () => {
      if (!anchorRect) return;

      const popupWidth = 304;
      const popupHeight = 365;
      const gap = 8;

      let left = anchorRect.left;

      if (left + popupWidth > window.innerWidth - 8) {
        left = window.innerWidth - popupWidth - 8;
      }

      if (left < 8) {
        left = 8;
      }

      let top = anchorRect.bottom + gap;

      if (top + popupHeight > window.innerHeight - 8) {
        top = anchorRect.top - popupHeight - gap;
      }

      if (top < 8) {
        top = 8;
      }

      setPosition({
        top,
        left,
      });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [anchorRect]);

  /* -------------------------------------------------------
     CALENDAR DAYS
  ------------------------------------------------------- */

  const calendarDays = useMemo(() => {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    const startDay = firstDay.getDay();
    const totalDays = lastDay.getDate();

    const days = [];

    for (let i = 0; i < startDay; i++) {
      days.push(null);
    }

    for (let day = 1; day <= totalDays; day++) {
      days.push(new Date(year, month, day));
    }

    while (days.length < 42) {
      days.push(null);
    }

    return days;
  }, [viewDate]);

  const selectedDate = parseDate(value);
  const minDate = min ? parseDate(min) : null;
  const maxDate = max ? parseDate(max) : null;

  function isDisabled(date) {
    if (!date) return true;

    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;

    return false;
  }

  function previousMonth() {
    setViewDate(
      new Date(
        viewDate.getFullYear(),
        viewDate.getMonth() - 1,
        1
      )
    );
  }

  function nextMonth() {
    setViewDate(
      new Date(
        viewDate.getFullYear(),
        viewDate.getMonth() + 1,
        1
      )
    );
  }

  function selectDate(date) {
    if (!date || isDisabled(date)) return;

    onSelect(formatDate(date));
    onClose();
  }

  const monthName = viewDate.toLocaleDateString("en-US", {
    month: "long",
  });

  const year = viewDate.getFullYear();

  return createPortal(
    <div
      ref={popupRef}
      className="
        fixed
        z-[99999]
        w-[304px]
        rounded-2xl
        border
        border-cyan-400/30
        bg-[#06101a]/[0.98]
        backdrop-blur-2xl
        shadow-[0_25px_80px_rgba(0,0,0,0.65),0_0_35px_rgba(0,200,255,0.12)]
        overflow-hidden
      "
      style={{
        top: position.top,
        left: position.left,
      }}
    >
      {/* =================================================
          TOP GLOW
      ================================================= */}

      <div
        className="
          absolute
          left-8
          right-8
          top-0
          h-px
          bg-gradient-to-r
          from-transparent
          via-cyan-400
          to-transparent
          opacity-80
        "
      />

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="relative px-4 pt-4 pb-3 border-b border-white/[0.07]">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <CalendarDays
                size={13}
                className="text-cyan-400"
              />

              <span className="text-[8px] uppercase tracking-[0.22em] text-slate-500">
                SELECT DATE
              </span>
            </div>

            <div className="mt-1.5 text-[15px] font-bold text-white">
              {monthName}
              <span className="ml-1.5 text-cyan-400">
                {year}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="
              flex
              h-7
              w-7
              items-center
              justify-center
              rounded-lg
              border
              border-white/[0.08]
              bg-white/[0.03]
              text-slate-500
              transition
              hover:border-cyan-400/30
              hover:bg-cyan-400/[0.08]
              hover:text-cyan-300
            "
          >
            <X size={12} />
          </button>
        </div>

        {/* Month navigation */}

        <div className="mt-3 flex items-center justify-between">
          <button
            type="button"
            onClick={previousMonth}
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              border
              border-white/[0.08]
              bg-white/[0.025]
              text-slate-400
              transition
              hover:border-cyan-400/30
              hover:bg-cyan-400/[0.08]
              hover:text-cyan-300
            "
          >
            <ChevronLeft size={15} />
          </button>

          <div className="text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {monthName} {year}
          </div>

          <button
            type="button"
            onClick={nextMonth}
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              border
              border-white/[0.08]
              bg-white/[0.025]
              text-slate-400
              transition
              hover:border-cyan-400/30
              hover:bg-cyan-400/[0.08]
              hover:text-cyan-300
            "
          >
            <ChevronRight size={15} />
          </button>
        </div>
      </div>

      {/* =================================================
          CALENDAR BODY
      ================================================= */}

      <div className="px-4 py-3">
        {/* Weekdays */}

        <div className="grid grid-cols-7 mb-2">
          {["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"].map(
            (day, index) => (
              <div
                key={day}
                className={`
                  text-center
                  text-[7px]
                  font-bold
                  tracking-wider
                  ${
                    index === 0
                      ? "text-red-400/80"
                      : "text-slate-500"
                  }
                `}
              >
                {day}
              </div>
            )
          )}
        </div>

        {/* Days */}

        <div className="grid grid-cols-7 gap-y-1">
          {calendarDays.map((date, index) => {
            if (!date) {
              return (
                <div
                  key={`empty-${index}`}
                  className="h-8"
                />
              );
            }

            const selected = isSameDay(date, selectedDate);
            const disabled = isDisabled(date);
            const today = isSameDay(date, new Date());
            const sunday = date.getDay() === 0;

            return (
              <button
                key={formatDate(date)}
                type="button"
                disabled={disabled}
                onClick={() => selectDate(date)}
                className={`
                  relative
                  mx-auto
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-lg
                  text-[9px]
                  font-medium
                  transition-all
                  duration-150

                  ${
                    selected
                      ? "bg-cyan-400 text-[#021017] font-bold shadow-[0_0_16px_rgba(34,211,238,0.45)]"
                      : disabled
                      ? "text-slate-700 cursor-not-allowed"
                      : today
                      ? "border border-cyan-400/35 bg-cyan-400/[0.06] text-cyan-300"
                      : sunday
                      ? "text-red-400/80 hover:bg-white/[0.05] hover:text-red-300"
                      : "text-slate-300 hover:bg-cyan-400/[0.10] hover:text-cyan-200"
                  }
                `}
              >
                {date.getDate()}

                {today && !selected && (
                  <span className="absolute bottom-1 h-0.5 w-0.5 rounded-full bg-cyan-400" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* =================================================
          FOOTER
      ================================================= */}

      <div className="border-t border-white/[0.07] bg-black/[0.14] px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[7px] uppercase tracking-[0.16em] text-slate-600">
              SELECTED DATE
            </div>

            <div className="mt-1 text-[10px] font-semibold text-cyan-300">
              {formatDisplayDate(value)}
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              onSelect("");
              onClose();
            }}
            className="
              rounded-lg
              border
              border-white/[0.10]
              bg-white/[0.025]
              px-3
              py-1.5
              text-[8px]
              font-bold
              uppercase
              tracking-wider
              text-slate-400
              transition
              hover:border-red-400/30
              hover:bg-red-400/[0.06]
              hover:text-red-300
            "
          >
            Clear
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

/* =========================================================
   DATE FIELD
========================================================= */

function DateField({
  value,
  min,
  max,
  onChange,
  label,
}) {
  const buttonRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [anchorRect, setAnchorRect] = useState(null);

  function openCalendar() {
    if (!buttonRef.current) return;

    setAnchorRect(
      buttonRef.current.getBoundingClientRect()
    );

    setOpen(true);
  }

  useEffect(() => {
    if (!open) return;

    function updatePosition() {
      if (!buttonRef.current) return;

      setAnchorRect(
        buttonRef.current.getBoundingClientRect()
      );
    }

    window.addEventListener("scroll", updatePosition, true);

    return () => {
      window.removeEventListener(
        "scroll",
        updatePosition,
        true
      );
    };
  }, [open]);

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        onClick={openCalendar}
        className="
          group
          w-full
          rounded-lg
          border
          border-white/[0.10]
          bg-black/20
          px-2
          py-2
          text-left
          outline-none
          transition-all
          hover:border-cyan-400/35
          hover:bg-cyan-400/[0.04]
          focus:border-cyan-400/50
          focus:ring-1
          focus:ring-cyan-400/20
        "
      >
        <div className="flex items-center justify-between gap-1">
          <span
            className={`text-[9px] ${
              value
                ? "text-slate-200"
                : "text-slate-500"
            }`}
          >
            {formatDisplayDate(value)}
          </span>

          <CalendarDays
            size={11}
            className="shrink-0 text-slate-500 transition group-hover:text-cyan-400"
          />
        </div>
      </button>

      {open && (
        <CalendarPopup
          value={value}
          min={min}
          max={max}
          anchorRect={anchorRect}
          onSelect={onChange}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}

/* =========================================================
   SIDEBAR
========================================================= */

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
        h-full
        w-full
        overflow-y-auto
        px-3.5
        py-4
        text-slate-200
        rounded-2xl
        border
        border-white/[0.10]
        bg-[#07101a]/85
        backdrop-blur-xl
        shadow-[0_20px_60px_rgba(0,0,0,0.45)]
        scrollbar-thin
      "
    >
      {/* =========================================================
          COMMAND CENTER IDENTITY
      ========================================================== */}

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

      {/* =========================================================
          DATE RANGE
      ========================================================== */}

      <SectionLabel icon={CalendarDays}>
        DATE RANGE
      </SectionLabel>

      <div className="grid grid-cols-2 gap-1.5">
        <DateField
          value={f.startDate}
          max={f.endDate}
          onChange={(value) =>
            update({ startDate: value })
          }
          label="START"
        />

        <DateField
          value={f.endDate}
          min={f.startDate}
          onChange={(value) =>
            update({ endDate: value })
          }
          label="END"
        />
      </div>

      {/* =========================================================
          RISK LEVEL
      ========================================================== */}

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

      {/* =========================================================
          SOURCE TYPE
      ========================================================== */}

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

      {/* =========================================================
          CONFIDENCE
      ========================================================== */}

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

      {/* =========================================================
          THERMAL INTENSITY
      ========================================================== */}

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

      {/* =========================================================
          INDUSTRIAL PROXIMITY
      ========================================================== */}

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

      {/* =========================================================
          SATELLITE
      ========================================================== */}

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

      {/* =========================================================
          DATA STATUS
      ========================================================== */}

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

      {/* =========================================================
          REFRESH
      ========================================================== */}

      <button
        onClick={onRefresh}
        className="
          mt-4
          w-full
          flex
          items-center
          justify-center
          gap-2
          rounded-xl
          border
          border-cyan-400/20
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
          transition-all
          duration-200
        "
      >
        <RotateCcw size={12} />
        REFRESH DATA
      </button>

      {/* =========================================================
          BOTTOM STATUS
      ========================================================== */}

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