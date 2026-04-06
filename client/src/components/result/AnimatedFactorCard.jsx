import React, { useEffect, useMemo, useState } from "react";
import { COLORS } from "../../constants/colors";
import { InfoCard } from "../common/InfoCard";
import { getScoreColor, easeOutCubic } from "../../utils/utils";

export function AnimatedFactorCard({ factor, index }) {
  const circumference = useMemo(() => 2 * Math.PI * 40, []);
  const [displayScore, setDisplayScore] = useState(0);
  const [displayColor, setDisplayColor] = useState("#ba1a1a");

  useEffect(() => {
    const duration = 1400;
    const delay = index * 120;
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
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="transparent"
              stroke={COLORS.surfaceContainer}
              strokeWidth="8"
            />
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

      <p
        className="text-sm mt-auto pt-6 leading-relaxed"
        style={{ color: COLORS.onSurfaceVariant }}
      >
        {factor.description}
      </p>
    </div>
  );
}
