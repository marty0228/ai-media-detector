import React, { useRef } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import { InfoCard } from "../common/InfoCard";
import { formatFileSize } from "../../utils/utils";

function FactorRow({ title, subtitle, icon }) {
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
}) {
  const fileInputRef = useRef(null);

  const openFileDialog = () => fileInputRef.current?.click();

  const handleClearFile = () => {
    onClearFile?.();

    // 같은 파일 다시 선택 가능하게 input 값도 초기화
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
  const hasFile = Boolean(
    selectedFile || previewDataUrl || savedFileInfo?.name,
  );

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <section className="text-center mb-16 max-w-3xl mx-auto">
        <div
          className="inline-block px-4 py-1.5 rounded-full font-bold text-xs mb-6 uppercase"
          style={{
            backgroundColor: COLORS.primaryFixed,
            color: COLORS.onPrimaryFixed,
            letterSpacing: "0.15em",
          }}
        >
          AI 기반
        </div>

        <h1
          className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight tracking-tight break-keep"
          style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
        >
          합성 시대의 진위 판독기
        </h1>

        <p
          className="text-lg leading-relaxed break-keep"
          style={{ color: COLORS.onSurfaceVariant }}
        >
          최첨단 신경망 모델을 활용하여 디지털 이미지의 진위를 검증합니다. 어떤
          사진이든 업로드하여 기원과 무결성에 대한 종합적인 포렌식 분석 리포트를
          받아보세요.
        </p>
      </section>

      <section className="mb-12">
        <div
          className="p-4 rounded-[1.75rem]"
          style={{
            backgroundColor: COLORS.surfaceContainerLowest,
            boxShadow: "0 40px 60px -10px rgba(14,30,36,0.05)",
          }}
        >
          <div
            className="border-2 border-dashed rounded-[1.5rem] p-12 flex flex-col items-center justify-center text-center cursor-pointer transition-colors"
            style={{
              backgroundColor: isDragActive
                ? COLORS.surfaceContainerHigh
                : COLORS.surfaceContainerLow,
              borderColor: isDragActive
                ? COLORS.primaryContainer
                : "rgba(193,199,203,0.3)",
            }}
            onClick={(event) => {
              if (event.target.closest("button")) return;
              openFileDialog();
            }}
            onDragEnter={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragActive(false);
            }}
            onDrop={handleDrop}
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

            <div
              className="w-16 h-16 rounded-full flex items-center justify-center mb-6"
              style={{ backgroundColor: COLORS.primaryContainer }}
            >
              <MaterialIcon className="text-white text-3xl">
                cloud_upload
              </MaterialIcon>
            </div>

            <h3
              className="text-2xl font-bold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              이미지를 놓아서 분석하기
            </h3>

            <p className="mb-3" style={{ color: COLORS.onSurfaceVariant }}>
              최대 25MB 이하의 PNG, JPG, WEBP 허용
            </p>

            <p
              className="text-sm mb-8 max-w-xl break-keep"
              style={{ color: COLORS.outline }}
            >
              현재 버전은 출처, 메타데이터, 외부 검색, 시각적 오류, 포렌식
              패턴이라는 5가지 설명 가능한 구성 요소로 분석 결과를 정리하여
              보여줍니다.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <button
                type="button"
                onClick={openFileDialog}
                className="px-8 py-4 font-bold rounded-[1.5rem] transition-all flex items-center gap-2 text-white"
                style={{
                  background: `linear-gradient(135deg, ${COLORS.primary}, ${COLORS.primaryContainer})`,
                }}
              >
                이미지 선택
                <MaterialIcon className="text-sm">arrow_forward</MaterialIcon>
              </button>

              <button
                type="button"
                disabled={!hasFile || isAnalyzing}
                onClick={onAnalyze}
                className="px-8 py-4 font-bold rounded-[1.5rem] transition-all flex items-center gap-2 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: COLORS.surfaceContainerLowest,
                  color: COLORS.primary,
                  border: `1px solid rgba(193,199,203,0.3)`,
                  opacity: !hasFile || isAnalyzing ? 0.5 : 1,
                }}
              >
                {isAnalyzing ? "분석 중..." : "AI 이미지 판독"}
                <MaterialIcon className="text-sm">
                  {isAnalyzing ? "hourglass_top" : "analytics"}
                </MaterialIcon>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-[1.1fr,0.9fr] gap-8">
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
                선택된 이미지
              </h3>
              <p className="text-sm" style={{ color: COLORS.onSurfaceVariant }}>
                결과 대시보드로 이동하기 전 업로드된 이미지를 미리 봅니다.
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
              {hasFile ? "준비 완료" : "업로드 대기"}
            </span>
          </div>

          <div
            className="relative rounded-[1.5rem] overflow-hidden min-h-[360px] flex items-center justify-center"
            style={{
              backgroundColor: COLORS.surfaceContainerLow,
              border: `1px solid rgba(193,199,203,0.2)`,
            }}
          >
            {hasPreview && (
              <bu
                tton
                type="button"
                onClick={handleClearFile}
                className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full flex items-center justify-center"
                style={{
                  backgroundColor: "rgba(12, 48, 60, 0.78)",
                  color: "#ffffff",
                  border: "1px solid rgba(255,255,255,0.16)",
                  backdropFilter: "blur(8px)",
                  cursor: "pointer",
                }}
                aria-label="선택한 이미지 제거"
                title="선택한 이미지 제거"
              >
                <MaterialIcon className="text-[20px]">close</MaterialIcon>
              </bu>
            )}

            {hasPreview ? (
              <img
                src={previewDataUrl}
                alt="Selected preview"
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
                  이미지가 없습니다
                </h4>

                <p
                  className="text-sm max-w-md"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  위에서 이미지를 업로드하면 이 영역에 미리보기가 표시됩니다.
                </p>
              </div>
            )}
          </div>

          {hasStoredFileInfo && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
              <InfoCard
                label="파일 이름"
                value={savedFileInfo.name || "알 수 없음"}
                breakAll
              />
              <InfoCard
                label="파일 확장자"
                value={savedFileInfo.type || "알 수 없음"}
              />
              <InfoCard
                label="파일 용량"
                value={savedFileInfo.size || "알 수 없음"}
              />
            </div>
          )}
        </div>

        <div
          className="p-6 rounded-[1.5rem] border shadow-sm"
          style={{
            backgroundColor: COLORS.surfaceContainerLowest,
            borderColor: "rgba(193,199,203,0.1)",
          }}
        >
          <h3
            className="text-2xl font-bold mb-2"
            style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
          >
            5-요소 분석 모델
          </h3>

          <p
            className="text-sm mb-6 break-keep"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            분석 결과 페이지는 설명 가능한 AI(XAI) 구성 요소를 기반으로
            정렬됩니다. 백엔드 알고리즘에서 어떠한 포멧의 데이터가 넘어오더라도
            이 동일한 시각적 구조에서 정보를 깔끔하게 열람할 수 있습니다.
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
        </div>
      </section>
    </main>
  );
}
