import { jsPDF } from "jspdf";
import { toCanvas } from "html-to-image";

export async function generateResultPdf({
  fileInfo,
  sanitizeFileName,
  reportElement,
}) {
  const timestamp = new Date();
  const fileBase = sanitizeFileName(fileInfo?.name);
  const dateLabel = timestamp.toISOString().slice(0, 10);
  const filename = `${fileBase || "ai-detection-report"}-${dateLabel}.pdf`;

  const pageRoot = document.documentElement;
  const body = document.body;

  const fullWidth = Math.max(
    pageRoot.scrollWidth,
    pageRoot.clientWidth,
    pageRoot.offsetWidth,
    body?.scrollWidth || 0,
    body?.clientWidth || 0,
    body?.offsetWidth || 0,
  );
  const fullHeight = Math.max(
    pageRoot.scrollHeight,
    pageRoot.clientHeight,
    pageRoot.offsetHeight,
    body?.scrollHeight || 0,
    body?.clientHeight || 0,
    body?.offsetHeight || 0,
  );

  const targetNode = reportElement || pageRoot;

  if (document.fonts?.ready) {
    await document.fonts.ready;
  }

  await new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve)),
  );

  // Google Fonts stylesheet의 cssRules 접근(CORS) 오류를 피하기 위해
  // 폰트 임베딩을 비활성화하고 DOM 캡처만 수행합니다.
  const canvas = await toCanvas(targetNode, {
    cacheBust: true,
    pixelRatio: 1,
    backgroundColor: "#f3faff",
    fontEmbedCSS: "",
    width: fullWidth,
    height: fullHeight,
    canvasWidth: fullWidth,
    canvasHeight: fullHeight,
    style: {
      transform: "none",
      transformOrigin: "top left",
    },
  });

  const imageData = canvas.toDataURL("image/jpeg", 0.96);
  const imageWidth = canvas.width;
  const imageHeight = canvas.height;

  if (!imageWidth || !imageHeight) {
    throw new Error("PDF 생성용 캡처 이미지가 비어 있습니다.");
  }

  const portrait = { width: 595.28, height: 841.89 };
  const landscape = { width: 841.89, height: 595.28 };
  const margin = 16;

  const portraitScale = Math.min(
    (portrait.width - margin * 2) / imageWidth,
    (portrait.height - margin * 2) / imageHeight,
  );
  const landscapeScale = Math.min(
    (landscape.width - margin * 2) / imageWidth,
    (landscape.height - margin * 2) / imageHeight,
  );

  const orientation = landscapeScale > portraitScale ? "landscape" : "portrait";
  const doc = new jsPDF({ unit: "pt", format: "a4", orientation });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const availableWidth = pageWidth - margin * 2;
  const availableHeight = pageHeight - margin * 2;
  const fitRatio = Math.min(availableWidth / imageWidth, availableHeight / imageHeight);

  const renderWidth = imageWidth * fitRatio;
  const renderHeight = imageHeight * fitRatio;
  const offsetX = (pageWidth - renderWidth) / 2;
  const offsetY = (pageHeight - renderHeight) / 2;

  doc.addImage(
    imageData,
    "JPEG",
    offsetX,
    offsetY,
    renderWidth,
    renderHeight,
    undefined,
    "FAST",
  );

  doc.save(filename);
}
