import React from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";

export function Header() {
  return (
    <header
      className="sticky top-0 z-50 px-8 py-4 flex items-center justify-between"
      style={{
        background: "rgba(243,250,255,0.8)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div className="flex items-center gap-3">
        <MaterialIcon className="text-[24px]" style={{ color: COLORS.primary }}>
          security
        </MaterialIcon>
        <span
          className="font-extrabold text-xl tracking-tight"
          style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
        >
          AI 판독기
        </span>
      </div>
      <div className="flex items-center gap-6">
        <nav
          className="hidden md:flex gap-8 text-sm font-semibold"
          style={{ letterSpacing: "0.1em", color: COLORS.onSurfaceVariant }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            포렌식 분석
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            적용 사례
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            API 연동
          </a>
        </nav>
        <MaterialIcon
          className="cursor-pointer"
          style={{ color: COLORS.onSurfaceVariant }}
        >
          menu
        </MaterialIcon>
      </div>
    </header>
  );
}
