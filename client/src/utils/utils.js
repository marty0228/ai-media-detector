export function safeParse(value) {
  try {
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

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

export function getScoreColor(score) {
  if (score >= 70) return "#ba1a1a";
  if (score >= 40) return "#ffb780";
  return "#006a60";
}

export function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}
