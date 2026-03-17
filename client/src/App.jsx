import React, { useState, useEffect } from "react";
import { STORAGE_KEYS, COLORS, defaultResult, defaultFile } from "./constants";
import { safeParse, createOptimizedPreview, formatFileSize, useExternalFonts } from "./utils";
import Header from "./components/Header";
import Footer from "./components/Footer";
import UploadPage from "./pages/UploadPage";
import ResultPage from "./pages/ResultPage";

// 메인 App 컴포넌트
export default function App() {
  // 전역 뷰용 폰트 동적 로드 (Material Icons 등)
  useExternalFonts();

  // 앱 내 상태 관리
  const [page, setPage] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewDataUrl, setPreviewDataUrl] = useState("");
  const [result, setResult] = useState(
    () => safeParse(localStorage.getItem(STORAGE_KEYS.result)) || defaultResult,
  );
  const [savedFileInfo, setSavedFileInfo] = useState(
    () => safeParse(localStorage.getItem(STORAGE_KEYS.file)) || defaultFile,
  );
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDragActive, setDragActive] = useState(false);

  // 로컬 데이터(이전 분석 내역) 복원 효과
  useEffect(() => {
    const storedPreview = localStorage.getItem(STORAGE_KEYS.preview);
    if (storedPreview) {
      setPreviewDataUrl(storedPreview);
    }
    if (safeParse(localStorage.getItem(STORAGE_KEYS.result))) {
      setPage("result");
    }
  }, []);

  // 파일 선택 핸들러
  const handleSelectedFile = async (file) => {
    if (!file.type.startsWith("image/")) {
      alert("이미지 파일을 업로드해주세요.");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      alert("최대 25MB 이하의 이미지를 선택해주세요.");
      return;
    }

    // 선택된 이미지의 최적화된 프리뷰 생성 및 로컬 상태에 저장
    const optimizedPreview = await createOptimizedPreview(file);
    setSelectedFile(file);
    setPreviewDataUrl(optimizedPreview);
  };

  // 분석 시작 핸들러 (실제 API 호출 혹은 Mock 데이터 활용)
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setIsAnalyzing(true);

      const formData = new FormData();
      formData.append("image", selectedFile);

      // 실제 API 엔드포인트 호출 (/analyze)
      const response = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = "분석 요청에 실패했습니다.";
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // json 변환 불가 시 무시
        }
        throw new Error(errorMessage);
      }

      // API 통신 성공 시 받은 데이터 처리
      const nextResult = await response.json();
      const nextFileInfo = {
        name: selectedFile.name,
        type: selectedFile.type || "Unknown",
        size: formatFileSize(selectedFile.size),
      };

      // 분석 결과, 파일 정보 등을 로컬 스토리지에 캐싱
      localStorage.setItem(STORAGE_KEYS.result, JSON.stringify(nextResult));
      localStorage.setItem(STORAGE_KEYS.file, JSON.stringify(nextFileInfo));
      if (previewDataUrl) {
        localStorage.setItem(STORAGE_KEYS.preview, previewDataUrl);
      } else {
        localStorage.removeItem(STORAGE_KEYS.preview);
      }

      // 화면을 결과 페이지로 전환 및 데이터 적용
      setResult(nextResult);
      setSavedFileInfo(nextFileInfo);
      setPage("result");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error(error);
      alert(`분석 중 오류가 발생했습니다: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 결과 확인 후 다시 분석하기(업로드 창)로 돌아가는 핸들러
  const handleBack = () => {
    setPage("upload");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: COLORS.background,
        color: COLORS.onSurface,
        fontFamily: "Inter, sans-serif",
      }}
    >
      {/* 폰트 및 전역 스타일 */}
      <style>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        body {
          margin: 0;
          background: ${COLORS.background};
        }
        * {
          box-sizing: border-box;
        }
      `}</style>

      {/* 헤더 섹션 */}
      <Header />

      {/* 메인 라우팅 (페이지) 처리부 */}
      {page === "upload" ? (
        <UploadPage
          selectedFile={selectedFile}
          previewDataUrl={previewDataUrl}
          isDragActive={isDragActive}
          isAnalyzing={isAnalyzing}
          onSelectFile={handleSelectedFile}
          onAnalyze={handleAnalyze}
          setDragActive={setDragActive}
        />
      ) : (
        <ResultPage
          result={result}
          fileInfo={savedFileInfo}
          previewUrl={
            previewDataUrl || localStorage.getItem(STORAGE_KEYS.preview) || ""
          }
          onBack={handleBack}
        />
      )}

      {/* 푸터 섹션 */}
      <Footer />
    </div>
  );
}