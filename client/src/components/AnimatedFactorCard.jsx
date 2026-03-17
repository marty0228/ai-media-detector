import React, { useMemo, useState, useEffect } from 'react';
import { COLORS } from '../constants';
import { getScoreColor, easeOutCubic } from '../utils';
import InfoCard from './InfoCard';

// 애니메이션 효과가 들어간 상세 분석 요소 카드
export default function AnimatedFactorCard({ factor, index }) {
  const circumference = useMemo(() => 2 * Math.PI * 40, []); // 원형 프로그레스바 둘레 계산
  const [displayScore, setDisplayScore] = useState(0); // 화면에 표시될 점수 상태
  const [displayColor, setDisplayColor] = useState("#ba1a1a"); // 점수에 따른 색상 상태

  // 애니메이션 효과 처리를 위한 Hook
  useEffect(() => {
    const duration = 1400; // 애니메이션 진행 시간(ms)
    const delay = index * 120; // 요소별 딜레이를 주어 순차적으로 나타나게 함
    let frameId = 0;
    let timeoutId = 0;

    timeoutId = window.setTimeout(() => {
      const startTime = performance.now();

      const update = (now) => {
        const rawProgress = Math.min((now - startTime) / duration, 1);
        const easedProgress = easeOutCubic(rawProgress);
        const currentScore = Math.round(factor.score * easedProgress);
        const currentColor = getScoreColor(currentScore);

        setDisplayScore(currentScore);
        setDisplayColor(currentColor);

        if (rawProgress < 1) {
          frameId = requestAnimationFrame(update);
        }
      };

      frameId = requestAnimationFrame(update);
    }, delay);

    return () => {
      clearTimeout(timeoutId);
      cancelAnimationFrame(frameId);
    };
  }, [factor.score, index]);

  const dashOffset = circumference * (1 - displayScore / 100);

  return (
    <div
      className="p-8 rounded-[1.5rem] border shadow-sm flex flex-col"
      style={{
        backgroundColor: COLORS.surfaceContainerLowest,
        borderColor: "rgba(193,199,203,0.1)",
      }}
    >
      {/* 카드 상단 (타이틀 및 원형 프로그레스 바) */}
      <div className="flex justify-between items-start mb-10 gap-6">
        <div>
          <h3
            className="text-xl font-bold"
            style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
          >
            {factor.title}
          </h3>
          <p
            className="text-xs font-bold uppercase mt-1"
            style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.18em" }}
          >
            {factor.subtitle}
          </p>
        </div>

        <div className="relative w-24 h-24 shrink-0">
          <svg className="w-24 h-24 -rotate-90">
            {/* 배경 원 */}
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="transparent"
              stroke={COLORS.surfaceContainer}
              strokeWidth="8"
            />
            {/* 진행율 표시 원 (애니메이션 적용) */}
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="transparent"
              stroke={displayColor}
              strokeDasharray={circumference.toFixed(1)}
              strokeDashoffset={dashOffset.toFixed(1)}
              strokeLinecap="round"
              strokeWidth="8"
              style={{ transition: "stroke 0.12s linear" }}
            />
          </svg>
          {/* 퍼센트 텍스트 */}
          <div
            className="absolute inset-0 flex items-center justify-center font-bold text-lg"
            style={{
              color: displayColor,
              fontFamily: "Manrope, sans-serif",
              transition: "color 0.12s linear",
            }}
          >
            {displayScore}%
          </div>
        </div>
      </div>

      {/* 세부 메트릭 지표 2개 */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <InfoCard
          label={factor.metrics[0].label}
          value={factor.metrics[0].value}
        />
        <InfoCard
          label={factor.metrics[1].label}
          value={factor.metrics[1].value}
        />
      </div>

      {/* 직선형 프로그레스 바 */}
      <div className="mb-8">
        <div
          className="flex justify-between text-[10px] font-bold uppercase mb-2"
          style={{ color: COLORS.outline }}
        >
          <span>{factor.progressLabel}</span>
          <span>{factor.progressValue}</span>
        </div>
        <div
          className="w-full h-2 rounded-full overflow-hidden"
          style={{ backgroundColor: COLORS.surfaceContainer }}
        >
          <div
            className="h-full rounded-full"
            style={{
              width: `${displayScore}%`,
              backgroundColor: displayColor,
              transition: "background-color 0.12s linear",
            }}
          />
        </div>
      </div>

      {/* 요소에 대한 부가 설명 */}
      <p
        className="text-sm mt-auto pt-6 leading-relaxed"
        style={{ color: COLORS.onSurfaceVariant }}
      >
        {factor.description}
      </p>
    </div>
  );
}
