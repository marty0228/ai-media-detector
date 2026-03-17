import { useEffect } from "react";

// 안전한 JSON 파싱 함수
export function safeParse(value) {
  try {
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

// 파일 크기를 읽기 쉬운 형식(KB, MB)으로 변환하는 함수
export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

// 파일을 Data URL 형태로 읽는 함수
export function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// 이미지 최적화 및 크기 조정 함수 (프리뷰용)
export async function createOptimizedPreview(file) {
  const originalDataUrl = await readFileAsDataURL(file);

  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const maxDimension = 1200;
      const ratio = Math.min(1, maxDimension / Math.max(img.width, img.height));
      const width = Math.round(img.width * ratio);
      const height = Math.round(img.height * ratio);

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);

      resolve(canvas.toDataURL("image/jpeg", 0.88));
    };
    img.onerror = () => resolve(originalDataUrl);
    img.src = originalDataUrl;
  });
}

// 점수에 따라 색상을 반환하는 함수 (위험도 표시용)
export function getScoreColor(score) {
  if (score >= 70) return "#006a60"; // 낮음/안전 (초록)
  if (score >= 40) return "#ffb780"; // 중간/주의 (주황)
  return "#ba1a1a"; // 높음/위험 (빨강)
}

// 애니메이션 부드러움을 위한 Cubic Easing 함수
export function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

// 외부 폰트를 동적으로 추가하는 Custom Hook
export function useExternalFonts() {
  useEffect(() => {
    const head = document.head;
    const manropeInter = document.createElement("link");
    manropeInter.rel = "stylesheet";
    manropeInter.href =
      "https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap";

    const materialSymbols = document.createElement("link");
    materialSymbols.rel = "stylesheet";
    materialSymbols.href =
      "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0";

    head.appendChild(manropeInter);
    head.appendChild(materialSymbols);

    return () => {
      head.removeChild(manropeInter);
      head.removeChild(materialSymbols);
    };
  }, []);
}
