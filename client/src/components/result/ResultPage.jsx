import React, { useRef } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import { InfoCard } from "../common/InfoCard";
import { AnimatedFactorCard } from "./AnimatedFactorCard";
import { generateResultPdf } from "../../utils/generateResultPdf";

export function ResultPage({ result, fileInfo, previewUrl, isDarkMode }) {
  const reportRef = useRef(null);

  const sanitizeFileName = (name) => {
    return (name || "ai-detection-report")
      .replace(/\.[^/.]+$/, "")
      .replace(/[^\p{L}\p{N}_ -]/gu, "")
      .trim()
      .replace(/\s+/g, "-")
      .slice(0, 60);
  };


  const handlePreviewReport = async () => {
    // 팝업 차단을 방지하기 위해 동기 타이밍에 새 창 오픈
    const newWindow = window.open("", "_blank");
    if (newWindow) {
      newWindow.document.write("<html><body style='display:flex;justify-content:center;align-items:center;height:100vh;background:#f8fafc;font-family:sans-serif;'><h2>Loading PDF Preview...</h2></body></html>");
    }
    
    try {
      const pdfUrl = await generateResultPdf({
        result,
        fileInfo,
        previewUrl,
        sanitizeFileName,
        previewMode: true,
      });
      
      if (newWindow) {
        newWindow.location.href = pdfUrl;
      } else {
        window.open(pdfUrl, "_blank");
      }
    } catch (error) {
      if (newWindow) newWindow.close();
      console.error("PDF 미리보기 실패:", error);
      alert(`PDF 미리보기 실패: ${error?.message || error}`);
    }
  };

  return (
    <main
      ref={reportRef}
      data-report-export="true"
      className="max-w-7xl mx-auto px-6 pt-24 pb-12"
    >
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
              AI 검증 리포트
            </div>

            <h2
              className="text-4xl font-extrabold mb-2"
              style={{
                color: isDarkMode ? "#ffffff" : COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              종합 분석 결과
            </h2>

            <p
              className="mb-8"
              style={{
                color: isDarkMode
                  ? "rgba(255,255,255,0.82)"
                  : COLORS.onSurfaceVariant,
              }}
            >
              {result.summary.description}
            </p>
            <div>
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase inline-flex items-center gap-2 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 ease-out"
                style={{
                  backgroundColor: isDarkMode ? "rgba(255,255,255,0.08)" : COLORS.surfaceContainerLowest,
                  color: isDarkMode ? "#ffffff" : COLORS.primary,
                  border: isDarkMode ? "1px solid rgba(255,255,255,0.16)" : "1px solid rgba(193,199,203,0.3)",
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={handlePreviewReport}
              >
                <MaterialIcon className="text-base">picture_as_pdf</MaterialIcon>
                개요 보기
              </button>
            </div>
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
                예측 신뢰도
              </span>
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
              <span>{`신뢰도 세부수치: ${result.summary.confidence}`}</span>
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
                  업로드된 용의선상 미디어
                </h3>
                <p
                  className="text-sm break-keep"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  현재 백엔드 서버로 전송되어 분석된 원본 이미지입니다.
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
                고객 입력
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
                    미리보기 없음
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

    </main>
  );
}
