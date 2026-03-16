import React, { useEffect, useState } from "react";
import { COLORS } from "./constants/colors";
import { STORAGE_KEYS } from "./constants/storageKeys";
import { defaultResult, defaultFile } from "./constants/defaultData";
import { safeParse, formatFileSize, createOptimizedPreview } from "./utils/utils";
import { useExternalFonts } from "./hooks/useExternalFonts";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import { UploadPage } from "./components/upload/UploadPage";
import { ResultPage } from "./components/result/ResultPage";

export default function App() {
  useExternalFonts();

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

  useEffect(() => {
    const storedPreview = localStorage.getItem(STORAGE_KEYS.preview);
    if (storedPreview) {
      setPreviewDataUrl(storedPreview);
    }
    if (safeParse(localStorage.getItem(STORAGE_KEYS.result))) {
      setPage("result");
    }
  }, []);

  const handleSelectedFile = async (file) => {
    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      alert("Please choose an image up to 25MB.");
      return;
    }

    const optimizedPreview = await createOptimizedPreview(file);
    setSelectedFile(file);
    setPreviewDataUrl(optimizedPreview);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setIsAnalyzing(true);

      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = "Analysis request failed.";
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // ignore json parse failure
        }
        throw new Error(errorMessage);
      }

      const nextResult = await response.json();
      const nextFileInfo = {
        name: selectedFile.name,
        type: selectedFile.type || "Unknown",
        size: formatFileSize(selectedFile.size),
      };

      localStorage.setItem(STORAGE_KEYS.result, JSON.stringify(nextResult));
      localStorage.setItem(STORAGE_KEYS.file, JSON.stringify(nextFileInfo));
      if (previewDataUrl) {
        localStorage.setItem(STORAGE_KEYS.preview, previewDataUrl);
      } else {
        localStorage.removeItem(STORAGE_KEYS.preview);
      }

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

      <Footer />
    </div>
  );
}