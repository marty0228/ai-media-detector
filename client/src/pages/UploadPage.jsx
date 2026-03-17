import React, { useRef } from 'react';
import { COLORS } from '../constants';
import { formatFileSize } from '../utils';
import MaterialIcon from '../components/MaterialIcon';
import InfoCard from '../components/InfoCard';
import FactorRow from '../components/FactorRow';

// 메인 업로드 페이지 컴포넌트
export default function UploadPage({
  selectedFile, // 선택된 파일 객체
  previewDataUrl, // 생성된 이미지 미리보기 데이터 URL
  isDragActive, // 드래그 앤 드롭 활성화 여부
  isAnalyzing, // 분석 중 상태
  onSelectFile, // 파일 선택 핸들러
  onAnalyze, // 분석 시작 핸들러
  setDragActive, // 드래그 상태 변경 핸들러
}) {
  const fileInputRef = useRef(null);

  const openFileDialog = () => fileInputRef.current?.click();

  const handleDrop = async (event) => {
    event.preventDefault();
    setDragActive(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      await onSelectFile(file);
    }
  };

  const hasFile = Boolean(selectedFile);

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      {/* 헤더 섹션 (앱 설명) */}
      <section className="text-center mb-16 max-w-3xl mx-auto">
        <div
          className="inline-block px-4 py-1.5 rounded-full font-bold text-xs mb-6 uppercase"
          style={{
            backgroundColor: COLORS.primaryFixed,
            color: COLORS.onPrimaryFixed,
            letterSpacing: "0.15em",
          }}
        >
          AI-POWERED {/* AI 기반 */}
        </div>
        <h1
          className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight tracking-tight"
          style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
        >
          Authenticity in the Age of Synthesis {/* 합성의 시대의 진정성 */}
        </h1>
        <p
          className="text-lg leading-relaxed"
          style={{ color: COLORS.onSurfaceVariant }}
        >
          최첨단 신경망 네트워크를 활용하여 디지털 출처를 검증합니다.
          이미지를 업로드하여 포괄적인 포렌식 분석을 받아보세요.
        </p>
      </section>

      {/* 업로드 영역 */}
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
              // 버튼 클릭 시에는 파일 다이얼로그가 열리지 않게 처리
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
            {/* 실제 숨겨진 파일 입력 필드 */}
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
              분석할 이미지 드래그 앤 드롭
            </h3>
            <p className="mb-3" style={{ color: COLORS.onSurfaceVariant }}>
              PNG, JPG, 또는 WEBP (최대 25MB)
            </p>
            <p
              className="text-sm mb-8 max-w-xl"
              style={{ color: COLORS.outline }}
            >
              현재 프로토타입은 출처 파악, 메타데이터, 상호 교차 웹 검색, 시각적 오류, 포렌식 패턴이라는
              5가지 설명 가능한 요소를 바탕으로 결과를 도출합니다.
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
                {isAnalyzing ? "분석 중..." : "이미지 분석"}
                <MaterialIcon className="text-sm">
                  {isAnalyzing ? "hourglass_top" : "analytics"}
                </MaterialIcon>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 미리보기 및 구조 안내 섹션 */}
      <section className="grid grid-cols-1 lg:grid-cols-[1.1fr,0.9fr] gap-8">
        {/* 선택한 이미지 미리보기 */}
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
                결과창으로 이동하기 전에 업로드된 이미지를 미리 확인하세요.
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
              {hasFile ? "Ready" : "No File"}
            </span>
          </div>

          <div
            className="rounded-[1.5rem] overflow-hidden min-h-[360px] flex items-center justify-center"
            style={{
              backgroundColor: COLORS.surfaceContainerLow,
              border: `1px solid rgba(193,199,203,0.2)`,
            }}
          >
            {previewDataUrl ? (
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
                  선택된 이미지 없음
                </h4>
                <p
                  className="text-sm max-w-md"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  이미지를 선택하여 미리보기를 활성화하고 프로토타입 분석을 진행하세요.
                </p>
              </div>
            )}
          </div>

          {hasFile && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
              <InfoCard label="File Name" value={selectedFile.name} breakAll />
              <InfoCard
                label="File Type"
                value={selectedFile.type || "Unknown"}
              />
              <InfoCard
                label="File Size"
                value={formatFileSize(selectedFile.size)}
              />
            </div>
          )}
        </div>

        {/* 5가지 요소 구성 설명 */}
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
            5가지 핵심 분석 요소
          </h3>
          <p
            className="text-sm mb-6"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            결과 페이지는 설명 가능한 AI(XAI) 분석 구조로 설계되어, 이후 백엔드의
            실제 분석 결과를 손쉽게 반영할 수 있습니다.
          </p>

          <div className="space-y-3">
            <FactorRow
              title="출처 검증 과정 (Provenance Verification)"
              subtitle="원본 및 이전 생성 기록 검증"
              icon="shield_lock"
            />
            <FactorRow
              title="메타데이터 (Metadata Analysis)"
              subtitle="EXIF 및 헤더의 무결성 검증"
              icon="badge"
            />
            <FactorRow
              title="교차 검색 (External Search Validation)"
              subtitle="교차 소스를 바탕으로 웹 탐색 및 검증"
              icon="travel_explore"
            />
            <FactorRow
              title="시각적 이상 (Visual Anomaly Analysis)"
              subtitle="인식 가능한 아티팩트 및 이상점 탐지"
              icon="visibility"
            />
            <FactorRow
              title="포렌식 패턴 (Forensic Pattern Analysis)"
              subtitle="노이즈, 압축, 픽셀 단위 분석"
              icon="biotech"
            />
          </div>
        </div>
      </section>
    </main>
  );
}
