import React, { useEffect, useRef, useState } from 'react';

export default function BoxCropPreview({ src, box, scale = 2, maxWidth = 800 }) {
  const canvasRef = useRef(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!src || !box) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = src;
    const handleLoad = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      const [x1, y1, x2, y2] = box.xyxy || [0,0,0,0];
      const w = Math.max(1, x2 - x1);
      const h = Math.max(1, y2 - y1);

      const targetW = Math.min(maxWidth, Math.round(w * scale));
      const scaleFactor = targetW / w;
      const targetH = Math.round(h * scaleFactor);

      canvas.width = targetW;
      canvas.height = targetH;

      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, x1, y1, w, h, 0, 0, targetW, targetH);

      setLoaded(true);
    };

    img.onload = handleLoad;
    img.onerror = () => setLoaded(false);
    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src, box, scale, maxWidth]);

  if (!src || !box) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ borderRadius: 8, overflow: 'hidden', background: '#111' }}>
        <canvas ref={canvasRef} style={{ display: loaded ? 'block' : 'none', width: '100%', height: 'auto' }} />
        {!loaded && (
          <div style={{ width: 300, height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
            이미지 로딩...
          </div>
        )}
      </div>
      <div style={{ fontSize: 13, color: '#333' }}>
        <div>확대: {scale}x</div>
      </div>
    </div>
  );
}
