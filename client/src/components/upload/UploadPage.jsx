import React, { useRef } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";
import { InfoCard } from "../common/InfoCard";
import { formatFileSize } from "../../utils/utils";

function FactorRow({ title, subtitle, icon }) {
  return (
    <div
      className="flex items-center justify-between rounded-[1rem] px-4 py-4"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <div>
        <div className="text-sm font-bold" style={{ color: COLORS.primary }}>
          {title}
        </div>
        <div className="text-xs" style={{ color: COLORS.onSurfaceVariant }}>
          {subtitle}
        </div>
      </div>
      <MaterialIcon style={{ color: COLORS.primary }}>{icon}</MaterialIcon>
    </div>
  );
}

export function UploadPage({
  selectedFile,
  previewDataUrl,
  isDragActive,
  isAnalyzing,
  onSelectFile,
  onAnalyze,
  setDragActive,
}) {
  const fileInputRef = useRef(null);

  const openFileDialog = () => fileInputRef.current?.click();

  const handleDrop = async (event) => {
    event.preventDefault();
    setDragActive(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      await onSelectFile(file);
    }
  };

  const hasFile = Boolean(selectedFile);

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <section className="text-center mb-16 max-w-3xl mx-auto">
        <div
          className="inline-block px-4 py-1.5 rounded-full font-bold text-xs mb-6 uppercase"
          style={{
            backgroundColor: COLORS.primaryFixed,
            color: COLORS.onPrimaryFixed,
            letterSpacing: "0.15em",
          }}
        >
          AI-POWERED
        </div>
        <h1
          className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight tracking-tight"
          style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
        >
          Authenticity in the Age of Synthesis
        </h1>
        <p
          className="text-lg leading-relaxed"
          style={{ color: COLORS.onSurfaceVariant }}
        >
          Utilizing state-of-the-art neural networks to verify digital
          provenance. Upload any image to receive a comprehensive forensic
          analysis of its origin and integrity.
        </p>
      </section>

      <section className="mb-12">
        <div
          className="p-4 rounded-[1.75rem]"
          style={{
            backgroundColor: COLORS.surfaceContainerLowest,
            boxShadow: "0 40px 60px -10px rgba(14,30,36,0.05)",
          }}
        >
          <div
            className="border-2 border-dashed rounded-[1.5rem] p-12 flex flex-col items-center justify-center text-center cursor-pointer transition-colors"
            style={{
              backgroundColor: isDragActive
                ? COLORS.surfaceContainerHigh
                : COLORS.surfaceContainerLow,
              borderColor: isDragActive
                ? COLORS.primaryContainer
                : "rgba(193,199,203,0.3)",
            }}
            onClick={(event) => {
              if (event.target.closest("button")) return;
              openFileDialog();
            }}
            onDragEnter={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragActive(false);
            }}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
              onChange={async (event) => {
                const file = event.target.files?.[0];
                if (file) {
                  await onSelectFile(file);
                }
              }}
            />

            <div
              className="w-16 h-16 rounded-full flex items-center justify-center mb-6"
              style={{ backgroundColor: COLORS.primaryContainer }}
            >
              <MaterialIcon className="text-white text-3xl">
                cloud_upload
              </MaterialIcon>
            </div>

            <h3
              className="text-2xl font-bold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              Drop image to analyze
            </h3>
            <p className="mb-3" style={{ color: COLORS.onSurfaceVariant }}>
              PNG, JPG, or WEBP up to 25MB
            </p>
            <p
              className="text-sm mb-8 max-w-xl"
              style={{ color: COLORS.outline }}
            >
              The current prototype organizes results into five explainable
              factors: provenance, metadata, external search, visual anomalies,
              and forensic patterns.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <button
                type="button"
                onClick={openFileDialog}
                className="px-8 py-4 font-bold rounded-[1.5rem] transition-all flex items-center gap-2 text-white"
                style={{
                  background: `linear-gradient(135deg, ${COLORS.primary}, ${COLORS.primaryContainer})`,
                }}
              >
                Choose Image
                <MaterialIcon className="text-sm">arrow_forward</MaterialIcon>
              </button>

              <button
                type="button"
                disabled={!hasFile || isAnalyzing}
                onClick={onAnalyze}
                className="px-8 py-4 font-bold rounded-[1.5rem] transition-all flex items-center gap-2 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: COLORS.surfaceContainerLowest,
                  color: COLORS.primary,
                  border: `1px solid rgba(193,199,203,0.3)`,
                  opacity: !hasFile || isAnalyzing ? 0.5 : 1,
                }}
              >
                {isAnalyzing ? "Analyzing..." : "Analyze Image"}
                <MaterialIcon className="text-sm">
                  {isAnalyzing ? "hourglass_top" : "analytics"}
                </MaterialIcon>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-[1.1fr,0.9fr] gap-8">
        <div
          className="p-6 rounded-[1.5rem] border shadow-sm"
          style={{
            backgroundColor: COLORS.surfaceContainerLowest,
            borderColor: "rgba(193,199,203,0.1)",
          }}
        >
          <div className="flex items-start justify-between gap-4 mb-5">
            <div>
              <h3
                className="text-2xl font-bold mb-1"
                style={{
                  color: COLORS.primary,
                  fontFamily: "Manrope, sans-serif",
                }}
              >
                Selected Image
              </h3>
              <p className="text-sm" style={{ color: COLORS.onSurfaceVariant }}>
                Preview the uploaded image before moving to the result
                dashboard.
              </p>
            </div>
            <span
              className="px-3 py-1 rounded-full text-xs font-bold uppercase"
              style={{
                backgroundColor: COLORS.primaryFixed,
                color: COLORS.onPrimaryFixed,
                letterSpacing: "0.15em",
              }}
            >
              {hasFile ? "Ready" : "No File"}
            </span>
          </div>

          <div
            className="rounded-[1.5rem] overflow-hidden min-h-[360px] flex items-center justify-center"
            style={{
              backgroundColor: COLORS.surfaceContainerLow,
              border: `1px solid rgba(193,199,203,0.2)`,
            }}
          >
            {previewDataUrl ? (
              <img
                src={previewDataUrl}
                alt="Selected preview"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8">
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center mb-5"
                  style={{ backgroundColor: COLORS.primaryContainer }}
                >
                  <MaterialIcon className="text-white text-3xl">
                    image
                  </MaterialIcon>
                </div>
                <h4
                  className="text-xl font-bold mb-2"
                  style={{
                    color: COLORS.primary,
                    fontFamily: "Manrope, sans-serif",
                  }}
                >
                  No image selected
                </h4>
                <p
                  className="text-sm max-w-md"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  Choose an image to enable preview and prototype analysis.
                </p>
              </div>
            )}
          </div>

          {hasFile && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
              <InfoCard label="File Name" value={selectedFile.name} breakAll />
              <InfoCard
                label="File Type"
                value={selectedFile.type || "Unknown"}
              />
              <InfoCard
                label="File Size"
                value={formatFileSize(selectedFile.size)}
              />
            </div>
          )}
        </div>

        <div
          className="p-6 rounded-[1.5rem] border shadow-sm"
          style={{
            backgroundColor: COLORS.surfaceContainerLowest,
            borderColor: "rgba(193,199,203,0.1)",
          }}
        >
          <h3
            className="text-2xl font-bold mb-2"
            style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
          >
            Five-Factor Structure
          </h3>
          <p
            className="text-sm mb-6"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            The result page is now organized around your XAI reporting
            structure, so it can later consume backend output without changing
            the layout.
          </p>

          <div className="space-y-3">
            <FactorRow
              title="Provenance Verification"
              subtitle="Origin and creation history"
              icon="shield_lock"
            />
            <FactorRow
              title="Metadata Analysis"
              subtitle="EXIF and header consistency"
              icon="badge"
            />
            <FactorRow
              title="External Search Validation"
              subtitle="Cross-source match review"
              icon="travel_explore"
            />
            <FactorRow
              title="Visual Anomaly Analysis"
              subtitle="Human-interpretable artifact check"
              icon="visibility"
            />
            <FactorRow
              title="Forensic Pattern Analysis"
              subtitle="Noise, compression, and pixel cues"
              icon="biotech"
            />
          </div>
        </div>
      </section>
    </main>
  );
}
