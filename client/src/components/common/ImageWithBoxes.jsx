import React, { useRef, useState, useEffect } from "react";

export default function ImageWithBoxes({ src, boxes = [], onBoxClick, highlightIndex = null }) {
  const imgRef = useRef(null);
  const [natural, setNatural] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;
    const handleLoad = () => setNatural({ w: img.naturalWidth, h: img.naturalHeight });
    img.addEventListener("load", handleLoad);
    if (img.complete) handleLoad();
    return () => img.removeEventListener("load", handleLoad);
  }, [src]);

  const toPercent = (val, dim) => (dim > 0 ? (val / dim) * 100 : 0);

  return (
    <div style={{ position: "relative", display: "inline-block", width: "100%" }}>
      <img
        ref={imgRef}
        src={src}
        alt="preview"
        style={{ display: "block", width: "100%", height: "auto" }}
      />

      {natural.w > 0 && boxes.map((b, i) => {
        const [x1, y1, x2, y2] = b.xyxy || b.box || [0,0,0,0];
        const left = toPercent(x1, natural.w);
        const top = toPercent(y1, natural.h);
        const width = toPercent(Math.max(0, x2 - x1), natural.w);
        const height = toPercent(Math.max(0, y2 - y1), natural.h);

        const isHighlight = highlightIndex !== null && highlightIndex === i;

        return (
          <div
            key={i}
            onClick={(e) => { e.stopPropagation(); onBoxClick?.(b, i); }}
            role="button"
            tabIndex={0}
            style={{
              position: "absolute",
              left: `${left}%`,
              top: `${top}%`,
              width: `${width}%`,
              height: `${height}%`,
              border: isHighlight ? "3px solid rgba(255,165,0,0.95)" : "2px solid rgba(0,123,255,0.9)",
              boxSizing: "border-box",
              background: isHighlight ? "rgba(255,165,0,0.08)" : "rgba(0,123,255,0.06)",
              cursor: "pointer",
            }}
            title={`conf: ${b.confidence ?? b.conf ?? ""}`}
          />
        );
      })}
    </div>
  );
}
