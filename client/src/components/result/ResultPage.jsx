import React, { useRef, useState } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import { InfoCard } from "../common/InfoCard";
import { AnimatedFactorCard } from "./AnimatedFactorCard";
import { generateResultPdf } from "../../utils/generateResultPdf";
import ImageWithBoxes from "../common/ImageWithBoxes";
import BoxCropPreview from "../common/BoxCropPreview";

export function ResultPage({ result, fileInfo, previewUrl, isDarkMode }) {
  const reportRef = useRef(null);
  const [selectedBox, setSelectedBox] = useState(null);
  const [showBoxes, setShowBoxes] = useState(false);
  const individualPredictions = result.individualPredictions || [];
  const watermarkPrediction = individualPredictions.find(
    (item) => item.model_name === "Water Mark",
  );
  const finalPrediction =
    result.rawPrediction?.final_prediction || result.rawPrediction || {};
  const isAiResult =
    Number(finalPrediction.predicted_idx) === 1 ||
    result.summary.verdict?.toLowerCase().includes("ai");
  const summaryCardColor = isAiResult ? COLORS.error : "#16a34a";
  const summaryAccentColor = isAiResult
    ? COLORS.errorContainer
    : COLORS.secondaryFixedDim;

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
            style={{ backgroundColor: summaryCardColor }}
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
                style={{ color: summaryAccentColor }}
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
                <div style={{ width: '100%' }}>
                  {!showBoxes ? (
                    <img
                      src={previewUrl}
                      alt="Uploaded preview"
                      className="w-full max-h-[500px] object-contain"
                      style={{ cursor: 'pointer' }}
                      onClick={() => setShowBoxes(true)}
                    />
                  ) : (
                    <div style={{ position: 'relative' }}>
                      <ImageWithBoxes
                        src={previewUrl}
                        boxes={watermarkPrediction?.details?.boxes || []}
                        onBoxClick={(box, idx) => setSelectedBox({ box, idx })}
                        highlightIndex={selectedBox?.idx ?? null}
                      />
                      <button
                        onClick={() => setShowBoxes(false)}
                        style={{ position: 'absolute', top: 10, right: 10, zIndex: 40 }}
                        className="px-3 py-1 rounded bg-white/90"
                      >
                        박스 숨기기
                      </button>
                    </div>
                  )}

                  {selectedBox ? (
                    <div
                      onClick={() => setSelectedBox(null)}
                      style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(0,0,0,0.6)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 60,
                        padding: 20,
                      }}
                    >
                      <div
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          width: 'min(95vw, 1100px)',
                          maxHeight: '92vh',
                          background: '#fff',
                          padding: 18,
                          borderRadius: 12,
                          overflow: 'auto',
                          display: 'flex',
                          gap: 12,
                        }}
                      >
                        <div style={{ flex: '1 1 60%', minWidth: 320 }}>
                          <h3 style={{ marginBottom: 8 }}>검출 영역 미리보기</h3>
                          <BoxCropPreview src={previewUrl} box={selectedBox.box} scale={3} maxWidth={720} />
                        </div>

                        <div style={{ flex: '1 1 40%', minWidth: 220, display: 'flex', flexDirection: 'column', gap: 8 }}>
                          <h3 style={{ marginBottom: 6 }}>상세 정보</h3>
                          <div style={{ fontSize: 14 }}>
                            <div><b>신뢰도:</b> {Math.round((selectedBox.box.confidence ?? selectedBox.box.conf ?? 0) * 10000) / 100}%</div>
                            <div><b>인덱스:</b> {selectedBox.idx}</div>
                            <div><b>패스:</b> {selectedBox.box.pass ?? '-'}</div>
                            <div style={{ marginTop: 6 }}><b>좌표 (x1,y1,x2,y2):</b></div>
                            <div style={{ fontFamily: 'monospace', fontSize: 13 }}>{(selectedBox.box.xyxy || []).map(v => Math.round(v)).join(', ')}</div>
                            <div style={{ marginTop: 8 }}>
                              <button onClick={() => setSelectedBox(null)} className="px-4 py-2 rounded bg-gray-200 mr-2">닫기</button>
                              <button
                                onClick={() => {
                                  const boxes = watermarkPrediction?.details?.boxes || [];
                                  const nextIdx = (selectedBox.idx + 1) % boxes.length;
                                  setSelectedBox({ box: boxes[nextIdx], idx: nextIdx });
                                }}
                                className="px-4 py-2 rounded bg-blue-500 text-white mr-2"
                              >다음</button>
                              <button
                                onClick={() => {
                                  const boxes = watermarkPrediction?.details?.boxes || [];
                                  const prevIdx = (selectedBox.idx - 1 + boxes.length) % boxes.length;
                                  setSelectedBox({ box: boxes[prevIdx], idx: prevIdx });
                                }}
                                className="px-4 py-2 rounded bg-blue-200"
                              >이전</button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
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

          {watermarkPrediction ? (
            <div
              className="p-6 rounded-[1.5rem] border shadow-sm"
              style={{
                backgroundColor: COLORS.surfaceContainerLowest,
                borderColor: "rgba(193,199,203,0.1)",
              }}
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <h3
                    className="text-2xl font-bold mb-1"
                    style={{
                      color: COLORS.primary,
                      fontFamily: "Manrope, sans-serif",
                    }}
                  >
                    워터마크 원본 결과
                  </h3>
                  <p
                    className="text-sm break-keep"
                    style={{ color: COLORS.onSurfaceVariant }}
                  >
                    백엔드가 실제로 돌린 워터마크 모델 출력입니다.
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
                  debug
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <InfoCard label="predicted_idx" value={String(watermarkPrediction.predicted_idx)} />
                <InfoCard label="confidence" value={String(watermarkPrediction.confidence)} />
                <InfoCard label="threshold" value={String(watermarkPrediction.threshold ?? watermarkPrediction.model_threshold ?? "-")} />
                <InfoCard label="weights" value={watermarkPrediction.weights_path ? "loaded" : "unknown"} />
              </div>

              {watermarkPrediction.details?.boxes?.length ? (
                <div className="mt-5 text-sm" style={{ color: COLORS.onSurfaceVariant }}>
                  탐지 박스 수: <b>{watermarkPrediction.details.boxes.length}</b>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </section>

    </main>
  );
}
