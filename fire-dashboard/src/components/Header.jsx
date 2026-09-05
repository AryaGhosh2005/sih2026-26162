import React, { useEffect, useState } from "react";
import { Flame } from "lucide-react";

export default function Header() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const time = now.toLocaleTimeString("en-GB", { hour12: false });
  const date = now.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  return (
    <div className="grid grid-cols-[2.6fr_1.6fr_0.3fr_1.1fr_1.1fr] gap-3">
      <div className="bg-gradient-to-br from-[#0d1420] to-[#070b12] border border-[#1d2939] rounded-[10px] px-[18px] py-3 h-[74px] flex flex-col justify-center">
        <div className="flex items-center gap-2 text-white text-[21px] font-extrabold tracking-wide">
          <Flame size={20} className="text-[#ff8a00]" />
          INDUSTRIAL FIRE DETECTION SYSTEM
        </div>
        <div className="text-[#778498] text-[10px] mt-[3px] tracking-wide">
          Satellite Thermal Intelligence &amp; Industrial Safety Command Center
        </div>
      </div>

      <div className="flex items-end justify-center pb-3">
        <div className="text-white font-bold text-xs border-b-2 border-[#24aef5] pb-3">
          Overview
        </div>
      </div>

      <div />

      <div className="bg-[#0b111b] border border-[#263142] rounded-lg text-center h-[74px] flex flex-col justify-center">
        <div className="text-[#738096] text-[9px] tracking-wide">SYSTEM STATUS</div>
        <div className="text-[#38d477] text-[13px] font-bold mt-1">● MONITORING ACTIVE</div>
      </div>

      <div className="bg-[#0b111b] border border-[#263142] rounded-lg text-center h-[74px] flex flex-col justify-center">
        <div className="text-white text-[15px] font-bold tracking-wide">{time}</div>
        <div className="text-[#778498] text-[9px] mt-[2px]">{date} &middot; Last updated</div>
      </div>
    </div>
  );
}
