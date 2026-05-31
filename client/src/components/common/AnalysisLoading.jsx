import React from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "./MaterialIcon";

const loadingSteps = [
  { icon: "image_search", label: "이미지 구조 분석" },
  { icon: "fingerprint", label: "메타데이터 확인" },
  { icon: "biotech", label: "위변조 패턴 탐지" },
];

export function AnalysisLoading() {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-5"
      style={{
        background:
          "linear-gradient(135deg, rgba(12,48,60,0.96) 0%, rgba(15,93,115,0.94) 48%, rgba(47,141,246,0.92) 100%)",
      }}
      role="status"
      aria-live="polite"
    >
      <style>{`
        @keyframes analysis-spin {
          to { transform: rotate(360deg); }
        }

        @keyframes analysis-pulse {
          0%, 100% { opacity: 0.48; transform: scale(0.96); }
          50% { opacity: 1; transform: scale(1); }
        }

        @keyframes analysis-bar {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(260%); }
        }
      `}</style>

      <div className="w-full max-w-xl text-center">
        <div className="relative mx-auto mb-8 flex h-28 w-28 items-center justify-center">
          <div
            className="absolute inset-0 rounded-full"
            style={{
              border: "1px solid rgba(255,255,255,0.18)",
              animation: "analysis-pulse 1.8s ease-in-out infinite",
            }}
          />
          <div
            className="absolute inset-3 rounded-full"
            style={{
              border: "3px solid rgba(255,255,255,0.20)",
              borderTopColor: "#ffffff",
              animation: "analysis-spin 1.1s linear infinite",
            }}
          />
          <div
            className="relative flex h-16 w-16 items-center justify-center rounded-full"
            style={{
              backgroundColor: "rgba(255,255,255,0.14)",
              border: "1px solid rgba(255,255,255,0.20)",
              backdropFilter: "blur(14px)",
            }}
          >
            <MaterialIcon className="text-[34px] text-white">
              analytics
            </MaterialIcon>
          </div>
        </div>

        <p
          className="mb-3 text-xs font-extrabold uppercase"
          style={{ color: "rgba(255,255,255,0.74)", letterSpacing: "0.16em" }}
        >
          AI Analysis
        </p>

        <h2
          className="mb-4 text-3xl font-extrabold leading-tight md:text-5xl"
          style={{
            color: "#ffffff",
            fontFamily: "Manrope, sans-serif",
          }}
        >
          이미지를 분석하고 있어요
        </h2>

        <p
          className="mx-auto mb-8 max-w-md text-sm leading-7 md:text-base"
          style={{ color: "rgba(240,248,252,0.84)" }}
        >
          워터마크, 메타데이터, 시각적 패턴을 종합해 결과를 준비하는 중입니다.
        </p>

        <div
          className="relative mx-auto mb-8 h-2 max-w-sm overflow-hidden rounded-full"
          style={{ backgroundColor: "rgba(255,255,255,0.18)" }}
        >
          <div
            className="absolute inset-y-0 left-0 w-1/2 rounded-full"
            style={{
              backgroundColor: COLORS.secondaryFixedDim,
              animation: "analysis-bar 1.35s ease-in-out infinite",
            }}
          />
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {loadingSteps.map((step, index) => (
            <div
              key={step.label}
              className="flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-bold sm:flex-col sm:gap-3"
              style={{
                color: "#ffffff",
                backgroundColor: "rgba(255,255,255,0.12)",
                border: "1px solid rgba(255,255,255,0.16)",
                animation: `analysis-pulse 1.8s ease-in-out ${index * 0.2}s infinite`,
              }}
            >
              <MaterialIcon className="text-[22px]">{step.icon}</MaterialIcon>
              <span>{step.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
