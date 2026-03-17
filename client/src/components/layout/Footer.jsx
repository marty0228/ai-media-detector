import React from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";

export function Footer() {
  return (
    <footer
      className="mt-24 px-8 py-16"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
        <div className="flex flex-col items-center md:items-start gap-4">
          <div className="flex items-center gap-2">
            <MaterialIcon style={{ color: COLORS.primary }}>
              security
            </MaterialIcon>
            <span
              className="font-bold text-lg tracking-tight"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
                letterSpacing: "-0.03em",
              }}
            >
              AI 판독기
            </span>
          </div>
          <p
            className="text-sm text-center md:text-left max-w-sm"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            © 2024 AI 판독기. 본 분석 결과는 확률에 기반하며 참고용으로만 제공됩니다.
          </p>
        </div>
        <nav
          className="flex flex-wrap justify-center gap-8 text-sm font-bold"
          style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.1em" }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            이용 약관
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            개인정보 처리방침
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            고객 지원
          </a>
        </nav>
      </div>
    </footer>
  );
}
