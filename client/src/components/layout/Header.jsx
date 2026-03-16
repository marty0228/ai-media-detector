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
          AI Authenticator
        </span>
      </div>
      <div className="flex items-center gap-6">
        <nav
          className="hidden md:flex gap-8 text-sm font-semibold uppercase"
          style={{ letterSpacing: "0.18em", color: COLORS.onSurfaceVariant }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            Forensics
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Case Studies
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            API
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
