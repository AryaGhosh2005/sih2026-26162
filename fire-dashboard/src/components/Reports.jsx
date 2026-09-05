import React from "react";
import { Download } from "lucide-react";
import { SectionTitle } from "./KpiCards";
import { toCsv, toGeoJson, downloadFile } from "../utils";

export default function Reports({ filtered }) {
  const exportCsv = () => {
    downloadFile(toCsv(filtered), "thermoscope_report.csv", "text/csv");
  };

  const exportGeoJson = () => {
    downloadFile(
      JSON.stringify(toGeoJson(filtered), null, 2),
      "thermoscope_report.geojson",
      "application/geo+json"
    );
  };

  return (
    <div>
      <SectionTitle>REPORTS</SectionTitle>
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={exportCsv}
          className="flex items-center justify-center gap-2 bg-[#0d141f] border border-[#283446] text-[#dce4ee] rounded-md text-xs font-semibold py-2.5 hover:border-[#159eea] hover:text-white transition-colors"
        >
          <Download size={13} /> EXPORT CSV
        </button>
        <button
          onClick={exportGeoJson}
          className="flex items-center justify-center gap-2 bg-[#0d141f] border border-[#283446] text-[#dce4ee] rounded-md text-xs font-semibold py-2.5 hover:border-[#159eea] hover:text-white transition-colors"
        >
          <Download size={13} /> EXPORT GEOJSON
        </button>
      </div>
    </div>
  );
}
