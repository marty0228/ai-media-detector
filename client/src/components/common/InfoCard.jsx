import React from "react";
import { COLORS } from "../../constants/colors";

export function InfoCard({ label, value, breakAll = false }) {
  return (
    <div
      className="p-4 rounded-[1rem]"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <span
        className="text-[10px] font-bold uppercase mb-1 block"
        style={{ color: COLORS.outline }}
      >
        {label}
      </span>
      <span
        className={`text-sm font-bold ${breakAll ? "break-all" : ""}`}
        style={{ color: COLORS.primary }}
      >
        {value}
      </span>
    </div>
  );
}
