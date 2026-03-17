import React from 'react';
import { COLORS } from '../constants';
import MaterialIcon from '../components/MaterialIcon';
import InfoCard from '../components/InfoCard';
import AnimatedFactorCard from '../components/AnimatedFactorCard';

// 분석 결과 페이지 컴포넌트
export default function ResultPage({
  result, // 서버 또는 목업에서 응답받은 결과 객체
  fileInfo, // 저장된 파일 정보
  previewUrl, // 저장된 프리뷰 데이터 URL
  onBack, // '업로드로 돌아가기' 핸들러
}) {
  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      {/* 뒤로 가기 버튼 */}
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-2 text-sm font-semibold mb-8 hover:underline"
        style={{ color: COLORS.primary }}
      >
        <MaterialIcon className="text-base">arrow_back</MaterialIcon>
        업로드 페이지로 돌아가기
      </button>

      {/* 최종 점수 및 종합 요약 */}
      <section className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12">
          <div className="max-w-2xl">
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold uppercase mb-4"
              style={{
                backgroundColor: COLORS.primaryFixed,
                color: COLORS.onPrimaryFixed,
                letterSpacing: "0.15em",
              }}
            >
              <MaterialIcon className="text-sm">science</MaterialIcon>
              Prototype Output {/* 프로토타입 결과 */}
            </div>
            <h2
              className="text-4xl font-extrabold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              종합 분석 결과
            </h2>
            <p style={{ color: COLORS.onSurfaceVariant }}>
              {result.summary.description}
            </p>
          </div>

          <div
            className="text-white p-8 rounded-[1.5rem] flex items-center gap-8 min-w-[320px] shadow-xl"
            style={{ backgroundColor: COLORS.primary }}
          >
            <div>
              <span
                className="text-xs font-bold uppercase opacity-70"
                style={{ letterSpacing: "0.18em" }}
              >
                최종 스코어
              </span>
              <div
                className="text-5xl font-black mt-1"
                style={{ fontFamily: "Manrope, sans-serif" }}
              >
                {result.summary.finalScore}%
              </div>
            </div>
            <div className="h-12 w-px bg-white/20" /> {/* 구분선 */}
            <div className="text-sm font-medium leading-tight">
              <span
                className="block font-bold"
                style={{ color: COLORS.secondaryFixedDim }}
              >
                {result.summary.verdict}
              </span>
              <span>{`신뢰도 (Confidence): ${result.summary.confidence}`}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[340px,1fr] gap-8">
          {/* 업로드되었던 원본 미디어 정보 및 미리보기 */}
          <div
            className="p-6 rounded-[1.5rem] border shadow-sm h-fit"
            style={{
              backgroundColor: COLORS.surfaceContainerLowest,
              borderColor: "rgba(193,199,203,0.1)",
            }}
          >
            <div className="flex items-start justify-between gap-4 mb-5">
              <div>
                <h3
                  className="text-2xl font-bold mb-1"
                  style={{
                    color: COLORS.primary,
                    fontFamily: "Manrope, sans-serif",
                  }}
                >
                  업로드된 미디어
                </h3>
                <p
                  className="text-sm"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  대시보드에 첨부된 현재 입력 (Input) 파일.
                </p>
              </div>
              <span
                className="px-3 py-1 rounded-full text-xs font-bold uppercase"
                style={{
                  backgroundColor: COLORS.primaryFixed,
                  color: COLORS.onPrimaryFixed,
                  letterSpacing: "0.15em",
                }}
              >
                Input
              </span>
            </div>

            <div
              className="rounded-[1.5rem] overflow-hidden min-h-[280px] flex items-center justify-center"
              style={{
                backgroundColor: COLORS.surfaceContainerLow,
                border: `1px solid rgba(193,199,203,0.2)`,
              }}
            >
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Uploaded preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center justify-center text-center p-8">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center mb-5"
                    style={{ backgroundColor: COLORS.primaryContainer }}
                  >
                    <MaterialIcon className="text-white text-3xl">
                      image
                    </MaterialIcon>
                  </div>
                  <h4
                    className="text-xl font-bold mb-2"
                    style={{
                      color: COLORS.primary,
                      fontFamily: "Manrope, sans-serif",
                    }}
                  >
                    미리보기 불가
                  </h4>
                  <p
                    className="text-sm"
                    style={{ color: COLORS.onSurfaceVariant }}
                  >
                    첫 페이지에서 이미지를 업로드해야 미리보기가 나타납니다.
                  </p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 gap-4 mt-5">
              <InfoCard
                label="File Name"
                value={fileInfo.name || "Unknown"}
                breakAll
              />
              <div className="grid grid-cols-2 gap-4">
                <InfoCard label="Type" value={fileInfo.type || "Unknown"} />
                <InfoCard label="Size" value={fileInfo.size || "Unknown"} />
              </div>
            </div>
          </div>

          {/* 각 팩터별 분석 내용 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {result.factors.map((factor, index) => (
              <AnimatedFactorCard
                key={`${factor.title}-${index}`}
                factor={factor}
                index={index}
              />
            ))}
          </div>
        </div>
      </section>

      {/* 하단 요약 및 보조 상태 플로팅 UI */}
      <section className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 히어로 카드 (설명 및 다시하기 버튼) */}
        <div
          className="md:col-span-2 text-white p-10 rounded-[1.5rem] relative overflow-hidden flex flex-col justify-end min-h-[360px]"
          style={{ backgroundColor: COLORS.primaryContainer }}
        >
          <div
            className="absolute top-0 right-0 w-64 h-64 opacity-20 blur-3xl -mr-20 -mt-20"
            style={{ backgroundColor: COLORS.secondary }}
          />

          <div className="relative z-10">
            <h3
              className="text-3xl font-bold mb-4"
              style={{ fontFamily: "Manrope, sans-serif" }}
            >
              {result.notes.heroTitle}
            </h3>
            <p
              className="text-lg mb-8 max-w-2xl"
              style={{ color: COLORS.onPrimaryContainer }}
            >
              {result.notes.heroText}
            </p>

            <div className="flex gap-4 z-10 flex-wrap">
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase"
                style={{
                  backgroundColor: COLORS.surfaceContainerLowest,
                  color: COLORS.primary,
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              >
                요약 보기 (맨 위로)
              </button>
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase border"
                style={{
                  backgroundColor: "rgba(255,255,255,0.10)",
                  color: COLORS.onPrimary,
                  borderColor: "rgba(255,255,255,0.20)",
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={onBack}
              >
                다른 이미지 테스트
              </button>
            </div>
          </div>
        </div>

        {/* 파이프라인 상태 보조 사이드 카드 */}
        <div
          className="p-8 rounded-[1.5rem] flex flex-col justify-between"
          style={{ backgroundColor: COLORS.surfaceContainerHigh }}
        >
          <div>
            <MaterialIcon
              className="text-4xl mb-6"
              style={{ color: COLORS.primary }}
            >
              hub
            </MaterialIcon>
            <h4
              className="text-xl font-bold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              {result.notes.sideTitle}
            </h4>
            <p className="text-sm" style={{ color: COLORS.onSurfaceVariant }}>
              이 블록은 향후 백엔드 파이프라인의 처리 상태를 보여주는 용도로 사용됩니다.
            </p>
          </div>
          <div className="mt-8 flex flex-col gap-3">
            {result.notes.sideItems.map((item, index) => (
              <div
                key={`${item.label}-${index}`}
                className="flex items-center justify-between text-xs py-2"
                style={{
                  borderBottom:
                    index !== result.notes.sideItems.length - 1
                      ? `1px solid rgba(193,199,203,0.2)`
                      : "none",
                }}
              >
                <span style={{ color: COLORS.outline }}>{item.label}</span>
                <span className="font-bold" style={{ color: COLORS.primary }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
