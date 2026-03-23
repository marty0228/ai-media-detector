import { jsPDF } from "jspdf";

const loadImageDataUrl = (src) =>
  new Promise((resolve) => {
    if (!src) {
      resolve(null);
      return;
    }

    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = () => {
      const maxWidth = 900;
      const maxHeight = 600;

      let { width, height } = img;
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

      resolve(canvas.toDataURL("image/jpeg", 0.95));
    };

    img.onerror = () => resolve(null);
    img.src = src;
  });

const drawProgressBar = (doc, x, y, w, h, percent, color) => {
  const safePercent = Math.max(0, Math.min(100, Number(percent) || 0));

  doc.setFillColor(235, 239, 244);
  doc.roundedRect(x, y, w, h, h / 2, h / 2, "F");

  doc.setFillColor(...color);
  doc.roundedRect(x, y, (w * safePercent) / 100, h, h / 2, h / 2, "F");
};

const drawFactorCard = (doc, factor, x, y, w, h, toAscii) => {
  const score = Number(factor?.score ?? 0);
  const title = toAscii(factor?.title || "Factor");
  const detail = toAscii(
    factor?.detail ||
      factor?.description ||
      factor?.reason ||
      factor?.summary ||
      "No detail available",
  );

  let accent = [245, 158, 11];
  if (score >= 70) accent = [15, 118, 110];
  else if (score < 40) accent = [239, 68, 68];

  doc.setFillColor(250, 252, 255);
  doc.setDrawColor(219, 226, 234);
  doc.roundedRect(x, y, w, h, 16, 16, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(31, 41, 55);
  doc.text(title, x + 16, y + 22);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(...accent);
  doc.text(`${score}%`, x + w - 16, y + 24, { align: "right" });

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(107, 114, 128);
  doc.text("score", x + w - 16, y + 38, { align: "right" });

  drawProgressBar(doc, x + 16, y + 48, w - 32, 8, score, accent);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(75, 85, 99);

  const lines = doc.splitTextToSize(detail, w - 32);
  doc.text(lines.slice(0, 4), x + 16, y + 74);
};

export async function generateResultPdf({
  result,
  fileInfo,
  previewUrl,
  sanitizeFileName,
  toAscii,
}) {
  const timestamp = new Date();
  const fileBase = sanitizeFileName(fileInfo?.name);
  const dateLabel = timestamp.toISOString().slice(0, 10);
  const filename = `${fileBase || "ai-detection-report"}-${dateLabel}.pdf`;

  const doc = new jsPDF({
    unit: "pt",
    format: "a4",
    orientation: "landscape",
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  const margin = 28;
  const gap = 14;
  const contentWidth = pageWidth - margin * 2;

  const score = Number(result?.summary?.finalScore ?? 0);
  const verdict = toAscii(
    result?.summary?.verdict ||
      (score >= 50 ? "Likely AI-generated" : "Likely Real photo"),
  );
  const confidencePercent = Number(result?.summary?.confidence ?? 0) * 100;
  const summaryDescription = toAscii(
    result?.summary?.description || "AI generated content analysis report.",
  );
  const factors = Array.isArray(result?.factors)
    ? result.factors.slice(0, 5)
    : [];

  const imageDataUrl = await loadImageDataUrl(previewUrl);

  doc.setFillColor(248, 250, 252);
  doc.rect(0, 0, pageWidth, pageHeight, "F");

  doc.setFillColor(255, 255, 255);
  doc.setDrawColor(221, 226, 232);
  doc.roundedRect(margin, margin, contentWidth, 52, 18, 18, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(23, 37, 84);
  doc.text("AI MEDIA DETECTION REPORT", margin + 20, margin + 32);

  doc.setFillColor(254, 240, 138);
  doc.roundedRect(pageWidth - margin - 120, margin + 10, 100, 28, 10, 10, "F");
  doc.setFontSize(10);
  doc.setTextColor(120, 53, 15);
  doc.text("OFFICIAL RESULT", pageWidth - margin - 70, margin + 28, {
    align: "center",
  });

  const heroY = margin + 68;
  const heroH = 170;
  const leftW = 220;
  const rightW = contentWidth - leftW - gap;

  doc.setFillColor(255, 255, 255);
  doc.setDrawColor(221, 226, 232);
  doc.roundedRect(margin, heroY, leftW, heroH, 18, 18, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(31, 41, 55);
  doc.text("Uploaded Media", margin + 16, heroY + 24);

  const imageBoxX = margin + 16;
  const imageBoxY = heroY + 36;
  const imageBoxW = 90;
  const imageBoxH = 110;

  doc.setFillColor(245, 247, 250);
  doc.setDrawColor(223, 228, 234);
  doc.roundedRect(imageBoxX, imageBoxY, imageBoxW, imageBoxH, 12, 12, "FD");

  if (imageDataUrl) {
    doc.addImage(
      imageDataUrl,
      "JPEG",
      imageBoxX + 4,
      imageBoxY + 4,
      imageBoxW - 8,
      imageBoxH - 8,
    );
  } else {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(107, 114, 128);
    doc.text(
      "No Preview",
      imageBoxX + imageBoxW / 2,
      imageBoxY + imageBoxH / 2,
      {
        align: "center",
      },
    );
  }

  let infoY = imageBoxY + 10;
  const infoX = imageBoxX + imageBoxW + 16;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(107, 114, 128);
  doc.text("File Name", infoX, infoY);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(31, 41, 55);
  doc.text(
    doc.splitTextToSize(toAscii(fileInfo?.name || "Unknown"), 88),
    infoX,
    infoY + 14,
  );

  infoY += 42;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(107, 114, 128);
  doc.text("File Type", infoX, infoY);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(31, 41, 55);
  doc.text(toAscii(fileInfo?.type || "Unknown"), infoX, infoY + 14);

  infoY += 34;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(107, 114, 128);
  doc.text("File Size", infoX, infoY);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(31, 41, 55);
  doc.text(toAscii(fileInfo?.size || "Unknown"), infoX, infoY + 14);

  const rightX = margin + leftW + gap;

  doc.setFillColor(255, 255, 255);
  doc.setDrawColor(221, 226, 232);
  doc.roundedRect(rightX, heroY, rightW, heroH, 18, 18, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(15);
  doc.setTextColor(23, 37, 84);
  doc.text("Detection Summary", rightX + 18, heroY + 26);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(75, 85, 99);
  doc.text(
    doc.splitTextToSize(summaryDescription, rightW - 180),
    rightX + 18,
    heroY + 46,
  );

  const circleX = rightX + rightW - 86;
  const circleY = heroY + 62;

  doc.setDrawColor(23, 37, 84);
  doc.setLineWidth(2);
  doc.circle(circleX, circleY, 36, "S");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(24);
  doc.setTextColor(23, 37, 84);
  doc.text(`${score}`, circleX, circleY + 8, { align: "center" });

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(107, 114, 128);
  doc.text("TOTAL SCORE", circleX, circleY - 46, { align: "center" });

  const miniY = heroY + 110;
  const miniGap = 10;
  const miniW = (rightW - 36 - 160) / 3;

  const miniCards = [
    { label: "Verdict", value: verdict },
    { label: "Confidence", value: `${confidencePercent.toFixed(2)}%` },
    {
      label: "Exported",
      value: timestamp.toISOString().slice(0, 19).replace("T", " "),
    },
  ];

  miniCards.forEach((item, index) => {
    const x = rightX + 18 + index * (miniW + miniGap);

    doc.setFillColor(246, 248, 252);
    doc.roundedRect(x, miniY, miniW, 42, 12, 12, "F");

    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(107, 114, 128);
    doc.text(item.label, x + 10, miniY + 14);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.setTextColor(31, 41, 55);
    doc.text(
      doc.splitTextToSize(toAscii(item.value), miniW - 20),
      x + 10,
      miniY + 28,
    );
  });

  const sectionY = heroY + heroH + 18;
  const cardH = 108;
  const cardGap = 14;
  const cardW3 = (contentWidth - cardGap * 2) / 3;
  const cardW2 = (contentWidth - cardGap) / 2;

  const positions = [
    { x: margin, y: sectionY, w: cardW3, h: cardH },
    { x: margin + cardW3 + cardGap, y: sectionY, w: cardW3, h: cardH },
    { x: margin + (cardW3 + cardGap) * 2, y: sectionY, w: cardW3, h: cardH },
    { x: margin, y: sectionY + cardH + cardGap, w: cardW2, h: cardH },
    {
      x: margin + cardW2 + cardGap,
      y: sectionY + cardH + cardGap,
      w: cardW2,
      h: cardH,
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
        toAscii,
      );
    }
  });

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(120, 126, 134);
  doc.text(
    `Generated for ${toAscii(fileInfo?.name || "Unknown")}  |  ${timestamp.toISOString()}`,
    margin,
    pageHeight - 16,
  );

  doc.save(filename);
}
