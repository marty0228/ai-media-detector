import React from 'react';
import { COLORS } from '../constants';

// 간단한 키-값 정보를 보여주는 카드 컴포넌트
export default function InfoCard({ label, value, breakAll = false }) {
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
