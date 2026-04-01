import { useEffect, useState } from "react";
import { STORAGE_KEYS } from "../constants/storageKeys";
import { defaultResult, defaultFile } from "../constants/defaultData";
import {
  safeParse,
  formatFileSize,
  createOptimizedPreview,
} from "../utils/utils";

export function useAnalysisState() {
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

  const resetAnalysisState = () => {
    localStorage.removeItem(STORAGE_KEYS.result);
    localStorage.removeItem(STORAGE_KEYS.file);
    localStorage.removeItem(STORAGE_KEYS.preview);

    setResult(defaultResult);
    setSavedFileInfo(defaultFile);
    setSelectedFile(null);
    setPreviewDataUrl("");
    setIsAnalyzing(false);
    setDragActive(false);
  };

  const restoreAnalysisState = () => {
    const storedPreview = localStorage.getItem(STORAGE_KEYS.preview);
    const storedResult = safeParse(localStorage.getItem(STORAGE_KEYS.result));
    const storedFile = safeParse(localStorage.getItem(STORAGE_KEYS.file));

    if (storedPreview) {
      setPreviewDataUrl(storedPreview);
    }

    if (storedResult) {
      setResult(storedResult);
      setPage("result");
    }

    if (storedFile) {
      setSavedFileInfo(storedFile);
    }
  };

  useEffect(() => {
    restoreAnalysisState();
  }, []);

  const handleSelectedFile = async (file) => {
    if (!file.type.startsWith("image/")) {
      alert("이미지 파일을 업로드해주세요.");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      alert("최대 25MB 이하의 이미지를 선택해주세요.");
      return;
    }

    const optimizedPreview = await createOptimizedPreview(file);

    const nextFileInfo = {
      name: file.name || "Unknown",
      type: file.type || "Unknown",
      size: formatFileSize(file.size),
    };

    setSelectedFile(file);
    setPreviewDataUrl(optimizedPreview);
    setSavedFileInfo(nextFileInfo);

    localStorage.setItem(STORAGE_KEYS.preview, optimizedPreview);
    localStorage.setItem(STORAGE_KEYS.file, JSON.stringify(nextFileInfo));
  };

  const handleClearSelectedFile = () => {
    setSelectedFile(null);
    setPreviewDataUrl("");
    setSavedFileInfo(defaultFile);

    localStorage.removeItem(STORAGE_KEYS.preview);
    localStorage.removeItem(STORAGE_KEYS.file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert(
        "새로고침 후에는 보안상 원본 파일이 유지되지 않습니다. 다시 선택 후 분석해주세요.",
      );
      return;
    }

    try {
      setIsAnalyzing(true);

      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/api/detect", {
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

      const apiData = await response.json();
      const predictionObj = apiData.prediction;
      const finalPred = predictionObj.final_prediction || predictionObj;

      const fileSize = formatFileSize(selectedFile.size);
      const nextFileInfo = {
        name: selectedFile.name || apiData.filename || "Unknown",
        type: selectedFile.type || "Unknown",
        size: fileSize,
      };

      const parsedConfidence = parseFloat(finalPred.confidence);

      const modelMapping = {
        "출처 검증": "Water Mark",
        "메타데이터 분석": "Meta Data",
        "외부 검색 검증": "Model 4",
        "시각적 이상 분석": "Model 3",
        "포렌식 패턴 분석": "Model 5",
      };

      const updatedFactors = defaultResult.factors.map((factor) => {
        const targetModelName = modelMapping[factor.title];
        const indPred = predictionObj.individual_predictions?.find(
          (p) => p.model_name === targetModelName,
        );

        if (!indPred) return factor;

        const score = Math.round(parseFloat(indPred.confidence) * 100);

        return {
          ...factor,
          score: Math.min(Math.max(score, 0), 100),
          progressValue:
            indPred.predicted_idx === 1 ? "AI 의심 (높음)" : "정상 (낮음)",
        };
      });

      const nextResult = {
        ...defaultResult,
        factors: updatedFactors,
        summary: {
          ...defaultResult.summary,
          finalScore: parsedConfidence,
          verdict: finalPred.predicted_idx === 1 ? "AI 생성 의심" : "실제 사진",
          confidence: parsedConfidence / 100,
          description:
            "본 분석 결과는 AI 예측 모델 백엔드로부터 응답받은 실제 추론 데이터입니다.",
        },
        notes: {
          ...defaultResult.notes,
          sideItems: [
            { label: "업로드 상태", value: "성공" },
            { label: "분석 출처", value: "AI 모델 API" },
            { label: "제공 요소", value: "5 가지 구조" },
            { label: "API 연결", value: "연결 성공" },
          ],
        },
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
    resetAnalysisState();
    setPage("upload");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return {
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
    resetAnalysisState,
    restoreAnalysisState,
  };
}
