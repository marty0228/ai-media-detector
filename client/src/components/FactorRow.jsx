import React from 'react';
import { COLORS } from '../constants';
import MaterialIcon from './MaterialIcon';

// XAI 5가지 분석 요소 중 하나를 간략히 보여주는 행 컴포넌트
export default function FactorRow({ title, subtitle, icon }) {
  return (
    <div
      className="flex items-center justify-between rounded-[1rem] px-4 py-4"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <div>
        <div className="text-sm font-bold" style={{ color: COLORS.primary }}>
          {title}
        </div>
        <div className="text-xs" style={{ color: COLORS.onSurfaceVariant }}>
          {subtitle}
        </div>
      </div>
      <MaterialIcon style={{ color: COLORS.primary }}>{icon}</MaterialIcon>
    </div>
  );
}
