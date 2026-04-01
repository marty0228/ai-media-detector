import React, { useRef } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";

function FactorRow({ title, subtitle, icon }) {
  return (
    <div
      className="flex items-center justify-between rounded-[1rem] px-4 py-4"
      style={{
        backgroundColor: COLORS.surfaceContainerLow,
      }}
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

export function UploadPage({
  selectedFile,
  savedFileInfo,
  previewDataUrl,
  isDragActive,
  isAnalyzing,
  onSelectFile,
  onClearFile,
  onAnalyze,
  setDragActive,
  isDarkMode,
}) {
  const fileInputRef = useRef(null);

  const openFileDialog = () => fileInputRef.current?.click();

  const handleClearFile = () => {
    onClearFile?.();

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    setDragActive(false);

    const file = event.dataTransfer?.files?.[0];
    if (file) {
      await onSelectFile(file);
    }
  };

  const hasPreview = Boolean(previewDataUrl);
  const hasStoredFileInfo = Boolean(savedFileInfo?.name);
  const hasRealSelectedFile = Boolean(selectedFile);

  return (
    <main
      className="transition-colors duration-300"
      style={{ backgroundColor: isDarkMode ? "#000000" : "#ffffff" }}
    >
      <section
        className="relative overflow-hidden w-full"
        style={{
          background: `
            radial-gradient(circle at 50% 78%, rgba(255,255,255,0.12), transparent 28%),
            linear-gradient(135deg, #0c303c 0%, #0f5d73 42%, #2f8df6 100%)
          `,
        }}
      >
        <div className="px-6 pt-20 pb-16 md:pt-24 md:pb-24">
          <div className="max-w-5xl mx-auto text-center">
            <div
              className="inline-block px-4 py-1.5 rounded-full font-bold text-xs mb-6 uppercase"
              style={{
                backgroundColor: "rgba(255,255,255,0.14)",
                color: "#ffffff",
                letterSpacing: "0.15em",
                border: "1px solid rgba(255,255,255,0.18)",
                backdropFilter: "blur(8px)",
              }}
            >
              AI 기반
            </div>

            <h1
              className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight tracking-tight break-keep"
              style={{
                color: "#ffffff",
                fontFamily: "Manrope, sans-serif",
              }}
            >
              합성 시대의 진위 판독기
            </h1>

            <p
              className="text-lg md:text-2xl leading-relaxed break-keep max-w-4xl mx-auto"
              style={{
                color: "rgba(255,255,255,0.88)",
              }}
            >
              최첨단 신경망 모델을 활용하여 디지털 이미지의 진위를 검증합니다.
              어떤 사진이든 업로드하여 기원과 무결성에 대한 종합적인 포렌식 분석
              리포트를 받아보세요.
            </p>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <section className="grid grid-cols-1 lg:grid-cols-[1.25fr,0.75fr] gap-8">
          <section id="image-analysis" className="scroll-mt-24">
            <div
              className="relative rounded-[2rem] overflow-hidden"
              style={{
                minHeight: "620px",
                background:
                  "linear-gradient(135deg, #0c303c 0%, #0f5d73 42%, #2f8df6 100%)",
              }}
              onDragEnter={(event) => {
                event.preventDefault();
                if (!hasPreview) setDragActive(true);
              }}
              onDragOver={(event) => {
                event.preventDefault();
                if (!hasPreview) setDragActive(true);
              }}
              onDragLeave={(event) => {
                event.preventDefault();
                if (!hasPreview) setDragActive(false);
              }}
              onDrop={hasPreview ? undefined : handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={async (event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    await onSelectFile(file);
                  }
                }}
              />

              {!hasPreview ? (
                <>
                  <div
                    className="absolute inset-0"
                    style={{
                      background:
                        "radial-gradient(circle at 50% 40%, rgba(255,255,255,0.10), transparent 28%)",
                    }}
                  />

                  <div className="relative h-full min-h-[620px]">
                    <div
                      className="absolute inset-0 rounded-[2rem] border flex flex-col items-center justify-center text-center px-8 md:px-12"
                      style={{
                        background: isDragActive
                          ? "linear-gradient(135deg, rgba(255,255,255,0.18) 0%, rgba(193,228,242,0.14) 100%)"
                          : "linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(193,228,242,0.08) 100%)",
                        borderColor: isDragActive
                          ? "rgba(255,255,255,0.26)"
                          : "rgba(255,255,255,0.16)",
                        backdropFilter: "blur(18px)",
                        boxShadow:
                          "inset 0 1px 0 rgba(255,255,255,0.08), 0 12px 30px rgba(4,20,28,0.10)",
                        minHeight: "580px",
                        cursor: "pointer",
                      }}
                      onClick={(event) => {
                        if (event.target.closest("button")) return;
                        openFileDialog();
                      }}
                    >
                      <div
                        className="rounded-full flex items-center justify-center mb-6"
                        style={{
                          width: "72px",
                          height: "72px",
                          background:
                            "linear-gradient(135deg, rgba(255,255,255,0.18) 0%, rgba(193,228,242,0.12) 100%)",
                          border: "1px solid rgba(255,255,255,0.16)",
                          backdropFilter: "blur(14px)",
                        }}
                      >
                        <MaterialIcon className="text-white text-3xl">
                          cloud_upload
                        </MaterialIcon>
                      </div>

                      <h3
                        className="text-3xl md:text-4xl font-extrabold mb-3 break-keep"
                        style={{
                          color: "#ffffff",
                          fontFamily: "Manrope, sans-serif",
                          textShadow: "0 6px 20px rgba(3,18,24,0.18)",
                        }}
                      >
                        이미지를 놓아서 분석하기
                      </h3>

                      <p
                        className="mb-4 text-base md:text-xl"
                        style={{
                          color: "rgba(240,248,252,0.92)",
                        }}
                      >
                        최대 25MB 이하의 PNG, JPG, WEBP 허용
                      </p>

                      <p
                        className="text-sm md:text-base mb-10 max-w-2xl break-keep"
                        style={{
                          color: "rgba(231,244,250,0.78)",
                          lineHeight: 1.7,
                        }}
                      >
                        현재 버전은 출처, 메타데이터, 외부 검색, 시각적 오류,
                        포렌식 패턴이라는 5가지 설명 가능한 구성 요소로 분석
                        결과를 정리하여 보여줍니다.
                      </p>

                      <button
                        type="button"
                        onClick={openFileDialog}
                        className="px-8 py-4 font-bold rounded-[1.5rem] inline-flex items-center gap-2 text-white"
                        style={{
                          background:
                            "linear-gradient(135deg, rgba(255,255,255,0.18) 0%, rgba(193,228,242,0.14) 100%)",
                          border: "1px solid rgba(255,255,255,0.16)",
                          backdropFilter: "blur(14px)",
                          boxShadow: "0 10px 24px rgba(6, 24, 32, 0.12)",
                        }}
                      >
                        이미지 선택
                        <MaterialIcon className="text-sm">
                          arrow_forward
                        </MaterialIcon>
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <img
                    src={previewDataUrl}
                    alt="Selected preview"
                    className="absolute inset-0 w-full h-full object-cover"
                  />

                  <div
                    className="absolute inset-0"
                    style={{
                      background: `
                        linear-gradient(
                          to top,
                          rgba(12, 48, 60, 0.88) 0%,
                          rgba(15, 93, 115, 0.58) 28%,
                          rgba(47, 141, 246, 0.18) 70%,
                          rgba(12, 48, 60, 0.08) 100%
                        )
                      `,
                    }}
                  />

                  <div className="relative h-full min-h-[620px] p-6 flex flex-col justify-between">
                    <div className="flex items-start justify-between gap-4">
                      <div
                        className="px-4 py-2 rounded-full text-xs font-bold uppercase inline-flex items-center gap-2"
                        style={{
                          backgroundColor: "rgba(255,255,255,0.16)",
                          color: "#ffffff",
                          border: "1px solid rgba(255,255,255,0.18)",
                          backdropFilter: "blur(12px)",
                          letterSpacing: "0.14em",
                        }}
                      >
                        <MaterialIcon className="text-sm">image</MaterialIcon>
                        업로드 완료
                      </div>

                      <button
                        type="button"
                        onClick={handleClearFile}
                        className="w-11 h-11 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor: "rgba(12,48,60,0.38)",
                          color: "#ffffff",
                          border: "1px solid rgba(255,255,255,0.18)",
                          backdropFilter: "blur(12px)",
                        }}
                        aria-label="선택한 이미지 제거"
                        title="선택한 이미지 제거"
                      >
                        <MaterialIcon className="text-[20px]">
                          close
                        </MaterialIcon>
                      </button>
                    </div>

                    <div
                      className="rounded-[1.6rem] p-5 md:p-6"
                      style={{
                        background:
                          "linear-gradient(135deg, rgba(12,48,60,0.34) 0%, rgba(15,93,115,0.28) 52%, rgba(47,141,246,0.18) 100%)",
                        border: "1px solid rgba(255,255,255,0.16)",
                        backdropFilter: "blur(18px)",
                        boxShadow:
                          "0 16px 36px rgba(4, 20, 28, 0.16), inset 0 1px 0 rgba(255,255,255,0.06)",
                      }}
                    >
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
                        <div
                          className="rounded-[1rem] px-4 py-4"
                          style={{
                            backgroundColor: "rgba(255,255,255,0.10)",
                            border: "1px solid rgba(255,255,255,0.10)",
                          }}
                        >
                          <div
                            className="text-xs mb-2"
                            style={{ color: "rgba(233,245,251,0.72)" }}
                          >
                            파일 이름
                          </div>
                          <div
                            className="text-sm font-bold break-all"
                            style={{ color: "#ffffff" }}
                          >
                            {savedFileInfo?.name || "알 수 없음"}
                          </div>
                        </div>

                        <div
                          className="rounded-[1rem] px-4 py-4"
                          style={{
                            backgroundColor: "rgba(255,255,255,0.10)",
                            border: "1px solid rgba(255,255,255,0.10)",
                          }}
                        >
                          <div
                            className="text-xs mb-2"
                            style={{ color: "rgba(233,245,251,0.72)" }}
                          >
                            파일 확장자
                          </div>
                          <div
                            className="text-sm font-bold"
                            style={{ color: "#ffffff" }}
                          >
                            {savedFileInfo?.type || "알 수 없음"}
                          </div>
                        </div>

                        <div
                          className="rounded-[1rem] px-4 py-4"
                          style={{
                            backgroundColor: "rgba(255,255,255,0.10)",
                            border: "1px solid rgba(255,255,255,0.10)",
                          }}
                        >
                          <div
                            className="text-xs mb-2"
                            style={{ color: "rgba(233,245,251,0.72)" }}
                          >
                            파일 용량
                          </div>
                          <div
                            className="text-sm font-bold"
                            style={{ color: "#ffffff" }}
                          >
                            {savedFileInfo?.size || "알 수 없음"}
                          </div>
                        </div>
                      </div>

                      {!hasRealSelectedFile && hasStoredFileInfo && (
                        <p
                          className="text-sm mb-5"
                          style={{ color: "rgba(236,247,252,0.82)" }}
                        >
                          새로고침 후에는 보안상 원본 파일이 유지되지 않습니다.
                          분석하려면 이미지를 다시 선택해주세요.
                        </p>
                      )}

                      <div className="flex flex-wrap gap-3">
                        <button
                          type="button"
                          onClick={openFileDialog}
                          className="px-6 py-3 rounded-[1rem] font-bold inline-flex items-center gap-2"
                          style={{
                            backgroundColor: "rgba(255,255,255,0.12)",
                            color: "#ffffff",
                            border: "1px solid rgba(255,255,255,0.16)",
                          }}
                        >
                          <MaterialIcon className="text-sm">
                            refresh
                          </MaterialIcon>
                          다시 선택
                        </button>

                        <button
                          type="button"
                          disabled={!hasRealSelectedFile || isAnalyzing}
                          onClick={onAnalyze}
                          className="px-6 py-3 rounded-[1rem] font-bold inline-flex items-center gap-2 disabled:cursor-not-allowed"
                          style={{
                            backgroundColor: "rgba(242, 250, 255, 0.96)",
                            color: COLORS.primary,
                            boxShadow: "0 8px 20px rgba(9, 34, 46, 0.12)",
                            opacity:
                              !hasRealSelectedFile || isAnalyzing ? 0.6 : 1,
                          }}
                        >
                          <MaterialIcon className="text-sm">
                            {isAnalyzing ? "hourglass_top" : "analytics"}
                          </MaterialIcon>
                          {isAnalyzing ? "분석 중..." : "AI 이미지 판독"}
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>

          <section
            id="analysis-elements"
            className="p-6 rounded-[1.5rem] border shadow-sm scroll-mt-24 transition-colors duration-300 self-start"
            style={{
              backgroundColor: COLORS.surfaceContainerLowest,
              borderColor: "rgba(193,199,203,0.1)",
            }}
          >
            <h3
              className="text-2xl font-bold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              5-요소 분석 모델
            </h3>

            <p
              className="text-sm mb-6 break-keep"
              style={{
                color: COLORS.onSurfaceVariant,
              }}
            >
              분석 결과 페이지는 설명 가능한 AI(XAI) 구성 요소를 기반으로
              정렬됩니다. 백엔드 알고리즘에서 어떠한 포맷의 데이터가
              넘어오더라도 이 동일한 시각적 구조에서 정보를 깔끔하게 열람할 수
              있습니다.
            </p>

            <div className="space-y-3">
              <FactorRow
                title="출처 검증"
                subtitle="사진의 원본 출처 및 생성 이력 파악"
                icon="shield_lock"
              />
              <FactorRow
                title="메타데이터 분석"
                subtitle="EXIF 정보 및 카메라 헤더 일관성 검사"
                icon="badge"
              />
              <FactorRow
                title="외부 검색 검증"
                subtitle="웹 크롤링을 통한 원본 사진 대조"
                icon="travel_explore"
              />
              <FactorRow
                title="시각적 이상 분석"
                subtitle="사물 왜곡 현상 및 인간 식별 가능 단계 오류 확인"
                icon="visibility"
              />
              <FactorRow
                title="포렌식 패턴 분석"
                subtitle="압축 알고리즘, 노이즈, 픽셀 징후 정밀 판독"
                icon="biotech"
              />
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
