import React, { useRef } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import { InfoCard } from "../common/InfoCard";
import { AnimatedFactorCard } from "./AnimatedFactorCard";
import { generateResultPdf } from "../../utils/generateResultPdf";

export function ResultPage({ result, fileInfo, previewUrl, onBack }) {
  const reportRef = useRef(null);

  const sanitizeFileName = (name) => {
    return (name || "ai-detection-report")
      .replace(/\.[^/.]+$/, "")
      .replace(/[^\p{L}\p{N}_ -]/gu, "")
      .trim()
      .replace(/\s+/g, "-")
      .slice(0, 60);
  };

  const handleSaveReport = async () => {
  try {
    await generateResultPdf({
      result,
      fileInfo,
      previewUrl,
      sanitizeFileName,
    });
  } catch (error) {
    console.error("PDF ?앹꽦 ?ㅽ뙣:", error);
    alert(`PDF ?앹꽦 ?ㅽ뙣: ${error?.message || error}`);
  }
};

  return (
    <main
      ref={reportRef}
      data-report-export="true"
      className="max-w-7xl mx-auto px-6 py-12"
    >
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-2 text-sm font-semibold mb-8 hover:underline"
        style={{ color: COLORS.primary }}
      >
        <MaterialIcon className="text-base">arrow_back</MaterialIcon>
        ?낅줈???섏씠吏濡??뚯븘媛湲?      </button>

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
              AI 寃利?由ы룷??            </div>
            <h2
              className="text-4xl font-extrabold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              醫낇빀 遺꾩꽍 寃곌낵
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
                style={{ letterSpacing: "0.15em" }}
              >
                ?덉륫 ?좊ː??              </span>
              <div
                className="text-5xl font-black mt-1"
                style={{ fontFamily: "Manrope, sans-serif" }}
              >
                {result.summary.finalScore}%
              </div>
            </div>
            <div className="h-12 w-px bg-white/20" />
            <div className="text-sm font-medium leading-tight">
              <span
                className="block font-bold"
                style={{ color: COLORS.secondaryFixedDim }}
              >
                {result.summary.verdict}
              </span>
              <span>{`?좊ː???몃??섏튂: ${result.summary.confidence}`}</span>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {result.factors.map((factor, index) => (
              <AnimatedFactorCard
                key={`${factor.title}-${index}`}
                factor={factor}
                index={index}
              />
            ))}
          </div>

          <div
            className="p-6 rounded-[1.5rem] border shadow-sm"
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
                  ?낅줈?쒕맂 ?⑹쓽?좎긽 誘몃뵒??                </h3>
                <p
                  className="text-sm break-keep"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  ?꾩옱 諛깆뿏???쒕쾭濡??꾩넚?섏뼱 遺꾩꽍???먮낯 ?대?吏?낅땲??
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
                怨좉컼 ?낅젰
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
                  className="w-full max-h-[500px] object-contain"
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
                    誘몃━蹂닿린 ?놁쓬
                  </h4>
                  <p
                    className="text-sm break-keep"
                    style={{ color: COLORS.onSurfaceVariant }}
                  >
                    첫 페이지에서 이미지를 업로드해야 이곳에서 미리보기가
                    제공됩니다.
                  </p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 gap-4 mt-5">
              <InfoCard
                label="파일 이름"
                value={fileInfo.name || "Unknown"}
                breakAll
              />
              <div className="grid grid-cols-2 gap-4">
                <InfoCard label="확장자" value={fileInfo.type || "Unknown"} />
                <InfoCard
                  label="파일 용량"
                  value={fileInfo.size || "Unknown"}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
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
                寃곌낵 媛쒖슂 蹂닿린
              </button>
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase border inline-flex items-center gap-2"
                style={{
                  backgroundColor: "rgba(255,255,255,0.16)",
                  color: COLORS.onPrimary,
                  borderColor: "rgba(255,255,255,0.25)",
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={handleSaveReport}
              >
                <MaterialIcon className="text-base">download</MaterialIcon>
                寃곌낵 ??ν븯湲?              </button>
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
                ?ㅻⅨ ?대?吏 寃?ы븯湲?              </button>
            </div>
          </div>
        </div>

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
            <p
              className="text-sm break-keep"
              style={{ color: COLORS.onSurfaceVariant }}
            >
              ?ν썑 諛깆뿏?쒕줈遺???꾨떖諛쏅뒗 ?쒖뒪??硫뷀??곗씠??諛??곌껐 ?곹깭瑜?              ?쒓린?섎뒗 怨듦컙?낅땲??
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
