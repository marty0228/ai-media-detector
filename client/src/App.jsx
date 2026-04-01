import React from "react";
import { COLORS } from "./constants/colors";
import { STORAGE_KEYS } from "./constants/storageKeys";
import { useExternalFonts } from "./hooks/useExternalFonts";
import { useAnalysisState } from "./hooks/useAnalysisState";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import { UploadPage } from "./components/upload/UploadPage";
import { ResultPage } from "./components/result/ResultPage";

export default function App() {
  useExternalFonts();

  const {
    page,
    selectedFile,
    previewDataUrl,
    result,
    savedFileInfo,
    isAnalyzing,
    isDragActive,
    setDragActive,
    handleSelectedFile,
    handleClearSelectedFile,
    handleAnalyze,
    handleBack,
  } = useAnalysisState();

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: COLORS.background,
        color: COLORS.onSurface,
        fontFamily: "Inter, sans-serif",
      }}
    >
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

      <Header />

      {page === "upload" ? (
        <UploadPage
          selectedFile={selectedFile}
          savedFileInfo={savedFileInfo}
          previewDataUrl={previewDataUrl}
          isDragActive={isDragActive}
          isAnalyzing={isAnalyzing}
          onSelectFile={handleSelectedFile}
          onClearFile={handleClearSelectedFile}
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

      <Footer />
    </div>
  );
}
