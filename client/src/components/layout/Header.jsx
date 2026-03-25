import React from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import Logo from "../../assets/logoColored.svg";

export function Header() {
  return (
    <header
      className="sticky top-0 z-50 px-8 py-4 flex items-center justify-between"
      style={{
        background: "rgba(243,250,255,0.8)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div className="flex items-center gap-0.5">
        <img
          src={Logo}
          alt="AI 판독기 로고"
          className="w-8 h-8 block shrink-0"
        />
        <span
          className="font-extrabold text-xl tracking-tight leading-none"
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
