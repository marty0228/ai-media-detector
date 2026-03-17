import React from 'react';
import { COLORS } from '../constants';
import MaterialIcon from './MaterialIcon';

// 앱 상단 네비게이션 헤더 컴포넌트
export default function Header() {
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
            Forensics {/* 법의학/증거 분석 */}
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Case Studies {/* 사례 연구 */}
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            API {/* API 정보 */}
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
