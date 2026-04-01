import React, { useState } from "react";
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

  const [isDarkMode, setIsDarkMode] = useState(false);

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

  const handleLogoClick = () => {
    if (page === "result") {
      handleBack();
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <div
      className="min-h-screen transition-colors duration-300"
      style={{
        backgroundColor: isDarkMode ? "#000000" : "#ffffff",
        color: isDarkMode ? "#ffffff" : COLORS.onSurface,
        fontFamily: "Inter, sans-serif",
      }}
    >
      <style>{`
        html {
          scroll-behavior: smooth;
        }
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        body {
          margin: 0;
          background: ${isDarkMode ? "#000000" : "#ffffff"};
        }
        * {
          box-sizing: border-box;
        }
      `}</style>

      <Header
        isDarkMode={isDarkMode}
        onToggleDarkMode={() => setIsDarkMode((prev) => !prev)}
        onLogoClick={handleLogoClick}
        showNav={page === "upload"}
        forceSolid={page === "result"}
      />

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
          isDarkMode={isDarkMode}
        />
      ) : (
        <ResultPage
          result={result}
          fileInfo={savedFileInfo}
          previewUrl={
            previewDataUrl || localStorage.getItem(STORAGE_KEYS.preview) || ""
          }
          isDarkMode={isDarkMode}
        />
      )}

      <Footer />
    </div>
  );
}
