import { jsPDF } from "jspdf";

const FONT_FAMILY = "NanumGothic";
const REGULAR_FONT_FILE = "NanumGothic.ttf";
const BOLD_FONT_FILE = "NanumGothicBold.ttf";

const COLORS = {
  pageBg: [248, 250, 252],
  white: [255, 255, 255],
  border: [221, 226, 232],
  title: [23, 37, 84],
  text: [31, 41, 55],
  subText: [107, 114, 128],
  mutedBg: [245, 247, 250],
  primary: [37, 99, 235],
  yellowBg: [254, 240, 138],
  yellowText: [120, 53, 15],
  track: [235, 239, 244],
};

const fontCache = {
  regularBase64: null,
  boldBase64: null,
  loaded: false,
};

const toText = (value, fallback = "") =>
  String(value ?? fallback)
    .replace(/\s+/g, " ")
    .trim();

const blobToBase64 = (blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onloadend = () => {
      const result = String(reader.result || "");
      const base64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(base64);
    };

    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });

const fetchFontAsBase64 = async (url) => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`폰트 요청 실패 (${response.status}): ${url}`);
  }

  const blob = await response.blob();

  if (!blob || blob.size === 0) {
    throw new Error(`폰트 파일이 비어 있음: ${url}`);
  }

  return blobToBase64(blob);
};

const registerKoreanFonts = async (doc) => {
  if (!fontCache.loaded) {
    fontCache.regularBase64 = await fetchFontAsBase64(
      `/fonts/${REGULAR_FONT_FILE}`,
    );

    try {
      fontCache.boldBase64 = await fetchFontAsBase64(
        `/fonts/${BOLD_FONT_FILE}`,
      );
    } catch (error) {
      console.warn("Bold 폰트가 없어 Regular 폰트로 대체합니다.", error);
      fontCache.boldBase64 = fontCache.regularBase64;
    }

    fontCache.loaded = true;
  }

  doc.addFileToVFS(REGULAR_FONT_FILE, fontCache.regularBase64);
  doc.addFont(REGULAR_FONT_FILE, FONT_FAMILY, "normal");

  doc.addFileToVFS(BOLD_FONT_FILE, fontCache.boldBase64);
  doc.addFont(BOLD_FONT_FILE, FONT_FAMILY, "bold");
};

const setPdfFont = (doc, style = "normal") => {
  doc.setFont(FONT_FAMILY, style);
};

const loadImageForPdf = (src) =>
  new Promise((resolve) => {
    if (!src) {
      resolve(null);
      return;
    }

    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = () => {
      const maxWidth = 1200;
      const maxHeight = 1200;

      let width = img.naturalWidth || img.width;
      let height = img.naturalHeight || img.height;

      const ratio = Math.min(maxWidth / width, maxHeight / height, 1);
      width = Math.round(width * ratio);
      height = Math.round(height * ratio);

      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = width;
      canvas.height = height;

      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);

      resolve({
        dataUrl: canvas.toDataURL("image/jpeg", 0.95),
        width,
        height,
      });
    };

    img.onerror = () => resolve(null);
    img.src = src;
  });

const addImageContain = (doc, img, boxX, boxY, boxW, boxH, padding = 6) => {
  if (!img?.dataUrl || !img?.width || !img?.height) return;

  const innerW = boxW - padding * 2;
  const innerH = boxH - padding * 2;

  const ratio = Math.min(innerW / img.width, innerH / img.height);
  const drawW = img.width * ratio;
  const drawH = img.height * ratio;

  const drawX = boxX + padding + (innerW - drawW) / 2;
  const drawY = boxY + padding + (innerH - drawH) / 2;

  doc.addImage(img.dataUrl, "JPEG", drawX, drawY, drawW, drawH);
};

const drawProgressBar = (doc, x, y, w, h, percent, color) => {
  const safePercent = Math.max(0, Math.min(100, Number(percent) || 0));

  doc.setFillColor(...COLORS.track);
  doc.roundedRect(x, y, w, h, h / 2, h / 2, "F");

  doc.setFillColor(...color);
  doc.roundedRect(x, y, (w * safePercent) / 100, h, h / 2, h / 2, "F");
};

const getScoreAccent = (score) => {
  if (score >= 70) return [15, 118, 110];
  if (score < 40) return [239, 68, 68];
  return [245, 158, 11];
};

const drawLabelValue = (
  doc,
  { x, y, label, value, valueWidth, labelSize = 7, valueSize = 9 },
) => {
  setPdfFont(doc, "normal");
  doc.setFontSize(labelSize);
  doc.setTextColor(...COLORS.subText);
  doc.text(label, x, y);

  setPdfFont(doc, "bold");
  doc.setFontSize(valueSize);
  doc.setTextColor(...COLORS.text);
  const lines = doc.splitTextToSize(toText(value, "-"), valueWidth);
  doc.text(lines.slice(0, 2), x, y + 12);
};

const drawFactorCard = (doc, factor, x, y, w, h) => {
  const score = Number(factor?.score ?? 0);
  const title = toText(factor?.title, "평가 항목");
  const detail = toText(
    factor?.detail || factor?.description || factor?.reason || factor?.summary,
    "세부 설명이 없습니다.",
  );

  const accent = getScoreAccent(score);

  doc.setFillColor(...COLORS.white);
  doc.setDrawColor(...COLORS.border);
  doc.roundedRect(x, y, w, h, 14, 14, "FD");

  setPdfFont(doc, "bold");
  doc.setFontSize(11);
  doc.setTextColor(...COLORS.text);
  doc.text(title, x + 14, y + 20);

  setPdfFont(doc, "bold");
  doc.setFontSize(17);
  doc.setTextColor(...accent);
  doc.text(`${score}%`, x + w - 14, y + 22, { align: "right" });

  setPdfFont(doc, "normal");
  doc.setFontSize(7);
  doc.setTextColor(...COLORS.subText);
  doc.text("score", x + w - 14, y + 34, { align: "right" });

  drawProgressBar(doc, x + 14, y + 42, w - 28, 7, score, accent);

  setPdfFont(doc, "normal");
  doc.setFontSize(8.2);
  doc.setTextColor(75, 85, 99);

  const detailLines = doc.splitTextToSize(detail, w - 28);
  doc.text(detailLines.slice(0, 3), x + 14, y + 62);
};

export async function generateResultPdf({
  result,
  fileInfo,
  previewUrl,
  sanitizeFileName,
}) {
  const timestamp = new Date();
  const fileBase = sanitizeFileName(fileInfo?.name);
  const dateLabel = timestamp.toISOString().slice(0, 10);
  const filename = `${fileBase || "ai-detection-report"}-${dateLabel}.pdf`;

  const doc = new jsPDF({
    unit: "pt",
    format: "a4",
    orientation: "portrait",
  });

  await registerKoreanFonts(doc);

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  const margin = 28;
  const contentWidth = pageWidth - margin * 2;
  const gap = 14;

  const score = Number(result?.summary?.finalScore ?? 0);
  const verdict = toText(
    result?.summary?.verdict,
    score >= 50 ? "AI 생성 가능성이 높음" : "실제 사진일 가능성이 높음",
  );
  const confidencePercent = Number(result?.summary?.confidence ?? 0) * 100;
  const summaryDescription = toText(
    result?.summary?.description,
    "AI 생성 콘텐츠 분석 결과 리포트입니다.",
  );
  const factors = Array.isArray(result?.factors)
    ? result.factors.slice(0, 5)
    : [];

  const previewImage = await loadImageForPdf(previewUrl);

  doc.setFillColor(...COLORS.pageBg);
  doc.rect(0, 0, pageWidth, pageHeight, "F");

  // ===== Header =====
  const headerY = margin;
  const headerH = 56;

  doc.setFillColor(...COLORS.white);
  doc.setDrawColor(...COLORS.border);
  doc.roundedRect(margin, headerY, contentWidth, headerH, 18, 18, "FD");

  setPdfFont(doc, "bold");
  doc.setFontSize(18);
  doc.setTextColor(...COLORS.title);
  doc.text("AI MEDIA DETECTION REPORT", margin + 18, headerY + 33);

  doc.setFillColor(...COLORS.yellowBg);
  doc.roundedRect(pageWidth - margin - 114, headerY + 13, 96, 26, 10, 10, "F");

  setPdfFont(doc, "bold");
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.yellowText);
  doc.text("OFFICIAL RESULT", pageWidth - margin - 66, headerY + 30, {
    align: "center",
  });

  // ===== Hero Section =====
  const heroY = headerY + headerH + 45;
  const heroH = 226; // 190 -> 226로 증가

  const mediaW = 180;
  const summaryW = contentWidth - mediaW - gap;

  // 왼쪽 업로드 이미지 카드
  doc.setFillColor(...COLORS.white);
  doc.setDrawColor(...COLORS.border);
  doc.roundedRect(margin, heroY, mediaW, heroH, 18, 18, "FD");

  setPdfFont(doc, "bold");
  doc.setFontSize(12);
  doc.setTextColor(...COLORS.text);
  doc.text("업로드 이미지", margin + 16, heroY + 22);

  const imageBoxX = margin + 16;
  const imageBoxY = heroY + 34;
  const imageBoxW = mediaW - 32;
  const imageBoxH = 122; // 104 -> 122로 증가

  doc.setFillColor(...COLORS.mutedBg);
  doc.setDrawColor(223, 228, 234);
  doc.roundedRect(imageBoxX, imageBoxY, imageBoxW, imageBoxH, 12, 12, "FD");

  if (previewImage) {
    addImageContain(
      doc,
      previewImage,
      imageBoxX,
      imageBoxY,
      imageBoxW,
      imageBoxH,
      6,
    );
  } else {
    setPdfFont(doc, "normal");
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.subText);
    doc.text(
      "미리보기 없음",
      imageBoxX + imageBoxW / 2,
      imageBoxY + imageBoxH / 2,
      {
        align: "center",
      },
    );
  }

  // 텍스트 위치를 고정값 대신 이미지 박스 기준으로 계산
  const fileNameY = imageBoxY + imageBoxH + 18;
  const fileMetaY = fileNameY + 34;

  drawLabelValue(doc, {
    x: imageBoxX,
    y: fileNameY,
    label: "파일 이름",
    value: fileInfo?.name || "Unknown",
    valueWidth: imageBoxW,
    valueSize: 8.2,
  });

  drawLabelValue(doc, {
    x: imageBoxX,
    y: fileMetaY,
    label: "형식 / 용량",
    value: `${toText(fileInfo?.type, "Unknown")} / ${toText(fileInfo?.size, "Unknown")}`,
    valueWidth: imageBoxW,
    valueSize: 8.2,
  });

  // 오른쪽 종합 분석 결과 카드
  const summaryX = margin + mediaW + gap;
  doc.setFillColor(...COLORS.white);
  doc.setDrawColor(...COLORS.border);
  doc.roundedRect(summaryX, heroY, summaryW, heroH, 18, 18, "FD");

  setPdfFont(doc, "bold");
  doc.setFontSize(14);
  doc.setTextColor(...COLORS.title);
  doc.text("종합 분석 결과", summaryX + 18, heroY + 24);

  // 오른쪽 점수 원이 차지하는 공간을 확실히 비워 둠
  const circleRadius = 34;
  const circleX = summaryX + summaryW - 76;
  const circleY = heroY + 68; // 62 -> 68로 약간 아래
  const circleReserveW = 120;

  const summaryTextX = summaryX + 18;
  const summaryTextY = heroY + 46;
  const summaryTextW = summaryW - 36 - circleReserveW;

  setPdfFont(doc, "normal");
  doc.setFontSize(9.2);
  doc.setTextColor(75, 85, 99);
  const summaryLines = doc.splitTextToSize(summaryDescription, summaryTextW);
  doc.text(summaryLines.slice(0, 3), summaryTextX, summaryTextY);

  doc.setDrawColor(...COLORS.primary);
  doc.setLineWidth(2);
  doc.circle(circleX, circleY, circleRadius, "S");

  setPdfFont(doc, "bold");
  doc.setFontSize(22);
  doc.setTextColor(...COLORS.primary);
  doc.text(`${score}`, circleX, circleY + 7, { align: "center" });

  setPdfFont(doc, "normal");
  doc.setFontSize(8);
  doc.setTextColor(...COLORS.subText);
  doc.text("TOTAL SCORE", circleX, circleY - 42, { align: "center" });

  // 하단 미니 카드
  const miniY = heroY + 130; // 112 -> 130으로 아래
  const miniGap = 10;
  const miniW = (summaryW - 36 - miniGap * 2) / 3;
  const miniH = 50;

  const miniCards = [
    {
      label: "판정",
      value: verdict,
    },
    {
      label: "신뢰도",
      value: `${confidencePercent.toFixed(2)}%`,
    },
    {
      label: "생성 시각",
      value: timestamp.toISOString().slice(0, 16).replace("T", " "),
    },
  ];

  miniCards.forEach((item, index) => {
    const x = summaryX + 18 + index * (miniW + miniGap);

    doc.setFillColor(246, 248, 252);
    doc.roundedRect(x, miniY, miniW, miniH, 12, 12, "F");

    setPdfFont(doc, "normal");
    doc.setFontSize(7.5);
    doc.setTextColor(...COLORS.subText);
    doc.text(item.label, x + 10, miniY + 14);

    setPdfFont(doc, "bold");
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.text);
    const lines = doc.splitTextToSize(toText(item.value), miniW - 20);
    doc.text(lines.slice(0, 2), x + 10, miniY + 30);
  });

  // ===== 세부 평가 항목 섹션: 전체를 조금 더 아래로 =====
  const factorsTitleY = heroY + heroH + 46; // 기존 34 -> 46

  setPdfFont(doc, "bold");
  doc.setFontSize(13);
  doc.setTextColor(...COLORS.title);
  doc.text("세부 평가 항목", margin + 2, factorsTitleY);

  const factorsY = factorsTitleY + 14;
  const cardGap = 14;
  const halfW = (contentWidth - cardGap) / 2;
  const cardH = 104;
  const rowGap = 12;

  const positions = [
    { x: margin, y: factorsY, w: halfW, h: cardH },
    { x: margin + halfW + cardGap, y: factorsY, w: halfW, h: cardH },

    { x: margin, y: factorsY + cardH + rowGap, w: halfW, h: cardH },
    {
      x: margin + halfW + cardGap,
      y: factorsY + cardH + rowGap,
      w: halfW,
      h: cardH,
    },

    {
      x: margin,
      y: factorsY + (cardH + rowGap) * 2,
      w: contentWidth,
      h: 92,
    },
  ];

  factors.forEach((factor, index) => {
    if (positions[index]) {
      drawFactorCard(
        doc,
        factor,
        positions[index].x,
        positions[index].y,
        positions[index].w,
        positions[index].h,
      );
    }
  });

  // Footer
  const footerY = pageHeight - 18;
  doc.setDrawColor(230, 233, 238);
  doc.line(margin, footerY - 10, pageWidth - margin, footerY - 10);

  setPdfFont(doc, "normal");
  doc.setFontSize(7.5);
  doc.setTextColor(120, 126, 134);
  doc.text(
    `Generated for ${toText(fileInfo?.name, "Unknown")}  |  ${timestamp.toISOString()}`,
    margin,
    footerY,
  );

  doc.save(filename);
}
