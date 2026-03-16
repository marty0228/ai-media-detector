import React, { useEffect, useMemo, useRef, useState } from "react";

const STORAGE_KEYS = {
  result: "aiAuthenticatorResult",
  file: "aiAuthenticatorFile",
  preview: "aiAuthenticatorPreview",
};

const COLORS = {
  secondaryFixedDim: "#6fd8c8",
  outline: "#72787b",
  surfaceDim: "#ccdde6",
  outlineVariant: "#c1c7cb",
  tertiaryFixed: "#ffdcc4",
  secondary: "#006a60",
  onSurface: "#0e1e24",
  surfaceBright: "#f3faff",
  surfaceContainer: "#dff0fa",
  error: "#ba1a1a",
  surfaceContainerLow: "#e6f6ff",
  tertiaryFixedDim: "#ffb780",
  surfaceContainerLowest: "#ffffff",
  inverseOnSurface: "#e2f3fd",
  inverseSurface: "#23333a",
  onSecondaryContainer: "#007166",
  inversePrimary: "#abcbdb",
  surface: "#f3faff",
  tertiaryContainer: "#683400",
  surfaceTint: "#436370",
  primaryFixedDim: "#abcbdb",
  primaryFixed: "#c6e8f8",
  onTertiaryFixed: "#2f1400",
  onPrimaryFixedVariant: "#2b4b58",
  background: "#f3faff",
  onSecondary: "#ffffff",
  secondaryFixed: "#8cf5e4",
  onTertiaryFixedVariant: "#6f3800",
  onError: "#ffffff",
  surfaceContainerHighest: "#d4e5ee",
  secondaryContainer: "#8cf5e4",
  tertiary: "#472200",
  surfaceVariant: "#d4e5ee",
  onErrorContainer: "#93000a",
  onPrimaryFixed: "#001f29",
  onPrimary: "#ffffff",
  primary: "#0c303c",
  onSecondaryFixed: "#00201c",
  errorContainer: "#ffdad6",
  primaryContainer: "#264653",
  onSurfaceVariant: "#42484b",
  surfaceContainerHigh: "#daebf4",
  onTertiary: "#ffffff",
  onSecondaryFixedVariant: "#005048",
  onTertiaryContainer: "#ed9c5b",
  onPrimaryContainer: "#93b3c3",
  onBackground: "#0e1e24",
};

const defaultResult = {
  summary: {
    finalScore: 71.8,
    verdict: "LIKELY AI-GENERATED",
    confidence: 0.902,
    description:
      "This prototype result combines five explainable factors and displays a weighted score that can later be replaced by backend analysis output.",
  },
  factors: [
    {
      title: "Provenance Verification",
      subtitle: "Origin & History",
      score: 74,
      accent: "#006a60",
      progressLabel: "Trust Index",
      progressValue: "Low Verification",
      metrics: [
        { label: "Credential Status", value: "NOT VERIFIED" },
        { label: "Edit Trail", value: "MISSING" },
      ],
      description:
        "No signed content credentials or verifiable creation path were confirmed in the current prototype workflow.",
    },
    {
      title: "Metadata Analysis",
      subtitle: "EXIF & Headers",
      score: 48,
      accent: "#ffb780",
      progressLabel: "Header Integrity",
      progressValue: "Suspicious",
      metrics: [
        { label: "Camera Make", value: "LIMITED / STRIPPED" },
        { label: "Software Tag", value: "REVIEW NEEDED" },
      ],
      description:
        "Metadata is treated as an independent signal so header consistency and software traces can be reviewed separately.",
    },
    {
      title: "External Search Validation",
      subtitle: "Cross-Source Search",
      score: 69,
      accent: "#006a60",
      progressLabel: "Cross-Web Match",
      progressValue: "Weak Match",
      metrics: [
        { label: "Visual Matches", value: "LOW / UNKNOWN" },
        { label: "Source Trace", value: "UNCONFIRMED" },
      ],
      description:
        "External search helps verify whether trusted prior appearances or reliable source traces can be found.",
    },
    {
      title: "Visual Anomaly Analysis",
      subtitle: "Human-Readable Artifacts",
      score: 81,
      accent: "#ba1a1a",
      progressLabel: "Artifact Density",
      progressValue: "Elevated",
      metrics: [
        { label: "Edge Coherence", value: "INCONSISTENT" },
        { label: "Lighting Pattern", value: "REVIEW FLAGGED" },
      ],
      description:
        "This factor isolates visible cues such as edge distortion, lighting mismatch, or irregular semantic details.",
    },
    {
      title: "Forensic Pattern Analysis",
      subtitle: "Noise & Compression Cues",
      score: 66,
      accent: "#264653",
      progressLabel: "Low-Level Signal",
      progressValue: "Detected",
      metrics: [
        { label: "Noise Signature", value: "IRREGULAR" },
        { label: "Compression Cue", value: "PRESENT" },
      ],
      description:
        "Forensic pattern analysis focuses on low-level evidence such as compression, noise, and pixel-level irregularity.",
    },
  ],
  notes: {
    heroTitle: "Structured Prototype Output",
    heroText:
      "The dashboard now renders from a single result object, so you can later replace this mock payload with a real API response while keeping the same UI.",
    sideTitle: "Pipeline Status",
    sideItems: [
      { label: "Upload State", value: "READY" },
      { label: "Result Source", value: "MOCK DATA" },
      { label: "Factor Layout", value: "5 FACTORS" },
      { label: "API Hook", value: "PENDING" },
    ],
  },
};

const defaultFile = {
  name: "No image uploaded",
  type: "Unknown",
  size: "Unknown",
};

function safeParse(value) {
  try {
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function createOptimizedPreview(file) {
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

function getScoreColor(score) {
  if (score >= 70) return "#006a60";
  if (score >= 40) return "#ffb780";
  return "#ba1a1a";
}

function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

function useExternalFonts() {
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

function MaterialIcon({ children, className = "", style = {} }) {
  return (
    <span
      className={`material-symbols-outlined ${className}`.trim()}
      style={style}
    >
      {children}
    </span>
  );
}

function Header() {
  return (
    <header
      className="sticky top-0 z-50 px-8 py-4 flex items-center justify-between"
      style={{
        background: "rgba(243,250,255,0.8)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div className="flex items-center gap-3">
        <MaterialIcon className="text-[24px]" style={{ color: COLORS.primary }}>
          security
        </MaterialIcon>
        <span
          className="font-extrabold text-xl tracking-tight"
          style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
        >
          AI Authenticator
        </span>
      </div>
      <div className="flex items-center gap-6">
        <nav
          className="hidden md:flex gap-8 text-sm font-semibold uppercase"
          style={{ letterSpacing: "0.18em", color: COLORS.onSurfaceVariant }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            Forensics
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Case Studies
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            API
          </a>
        </nav>
        <MaterialIcon
          className="cursor-pointer"
          style={{ color: COLORS.onSurfaceVariant }}
        >
          menu
        </MaterialIcon>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer
      className="mt-24 px-8 py-16"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
        <div className="flex flex-col items-center md:items-start gap-4">
          <div className="flex items-center gap-2">
            <MaterialIcon style={{ color: COLORS.primary }}>
              security
            </MaterialIcon>
            <span
              className="font-bold text-lg uppercase"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
                letterSpacing: "-0.03em",
              }}
            >
              AI Authenticator
            </span>
          </div>
          <p
            className="text-sm text-center md:text-left max-w-sm"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            © 2024 AI Authenticator. Analysis is probabilistic and for
            informational purposes only.
          </p>
        </div>
        <nav
          className="flex flex-wrap justify-center gap-8 text-sm font-bold uppercase"
          style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.18em" }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            Terms of Service
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Privacy Policy
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Contact Support
          </a>
        </nav>
      </div>
    </footer>
  );
}

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

function UploadPage({
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

function InfoCard({ label, value, breakAll = false }) {
  return (
    <div
      className="p-4 rounded-[1rem]"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <span
        className="text-[10px] font-bold uppercase mb-1 block"
        style={{ color: COLORS.outline }}
      >
        {label}
      </span>
      <span
        className={`text-sm font-bold ${breakAll ? "break-all" : ""}`}
        style={{ color: COLORS.primary }}
      >
        {value}
      </span>
    </div>
  );
}

function AnimatedFactorCard({ factor, index }) {
  const circumference = useMemo(() => 2 * Math.PI * 40, []);
  const [displayScore, setDisplayScore] = useState(0);
  const [displayColor, setDisplayColor] = useState("#ba1a1a");

  useEffect(() => {
    const duration = 1400;
    const delay = index * 120;
    let frameId = 0;
    let timeoutId = 0;

    timeoutId = window.setTimeout(() => {
      const startTime = performance.now();

      const update = (now) => {
        const rawProgress = Math.min((now - startTime) / duration, 1);
        const easedProgress = easeOutCubic(rawProgress);
        const currentScore = Math.round(factor.score * easedProgress);
        const currentColor = getScoreColor(currentScore);

        setDisplayScore(currentScore);
        setDisplayColor(currentColor);

        if (rawProgress < 1) {
          frameId = requestAnimationFrame(update);
        }
      };

      frameId = requestAnimationFrame(update);
    }, delay);

    return () => {
      clearTimeout(timeoutId);
      cancelAnimationFrame(frameId);
    };
  }, [factor.score, index]);

  const dashOffset = circumference * (1 - displayScore / 100);

  return (
    <div
      className="p-8 rounded-[1.5rem] border shadow-sm flex flex-col"
      style={{
        backgroundColor: COLORS.surfaceContainerLowest,
        borderColor: "rgba(193,199,203,0.1)",
      }}
    >
      <div className="flex justify-between items-start mb-10 gap-6">
        <div>
          <h3
            className="text-xl font-bold"
            style={{ color: COLORS.primary, fontFamily: "Manrope, sans-serif" }}
          >
            {factor.title}
          </h3>
          <p
            className="text-xs font-bold uppercase mt-1"
            style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.18em" }}
          >
            {factor.subtitle}
          </p>
        </div>

        <div className="relative w-24 h-24 shrink-0">
          <svg className="w-24 h-24 -rotate-90">
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="transparent"
              stroke={COLORS.surfaceContainer}
              strokeWidth="8"
            />
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="transparent"
              stroke={displayColor}
              strokeDasharray={circumference.toFixed(1)}
              strokeDashoffset={dashOffset.toFixed(1)}
              strokeLinecap="round"
              strokeWidth="8"
              style={{ transition: "stroke 0.12s linear" }}
            />
          </svg>
          <div
            className="absolute inset-0 flex items-center justify-center font-bold text-lg"
            style={{
              color: displayColor,
              fontFamily: "Manrope, sans-serif",
              transition: "color 0.12s linear",
            }}
          >
            {displayScore}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <InfoCard
          label={factor.metrics[0].label}
          value={factor.metrics[0].value}
        />
        <InfoCard
          label={factor.metrics[1].label}
          value={factor.metrics[1].value}
        />
      </div>

      <div className="mb-8">
        <div
          className="flex justify-between text-[10px] font-bold uppercase mb-2"
          style={{ color: COLORS.outline }}
        >
          <span>{factor.progressLabel}</span>
          <span>{factor.progressValue}</span>
        </div>
        <div
          className="w-full h-2 rounded-full overflow-hidden"
          style={{ backgroundColor: COLORS.surfaceContainer }}
        >
          <div
            className="h-full rounded-full"
            style={{
              width: `${displayScore}%`,
              backgroundColor: displayColor,
              transition: "background-color 0.12s linear",
            }}
          />
        </div>
      </div>

      <p
        className="text-sm mt-auto pt-6 leading-relaxed"
        style={{ color: COLORS.onSurfaceVariant }}
      >
        {factor.description}
      </p>
    </div>
  );
}

function ResultPage({ result, fileInfo, previewUrl, onBack }) {
  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-2 text-sm font-semibold mb-8 hover:underline"
        style={{ color: COLORS.primary }}
      >
        <MaterialIcon className="text-base">arrow_back</MaterialIcon>
        Back to Upload
      </button>

      <section className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12">
          <div className="max-w-2xl">
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold uppercase mb-4"
              style={{
                backgroundColor: COLORS.primaryFixed,
                color: COLORS.onPrimaryFixed,
                letterSpacing: "0.15em",
              }}
            >
              <MaterialIcon className="text-sm">science</MaterialIcon>
              Prototype Output
            </div>
            <h2
              className="text-4xl font-extrabold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              Analysis Result
            </h2>
            <p style={{ color: COLORS.onSurfaceVariant }}>
              {result.summary.description}
            </p>
          </div>

          <div
            className="text-white p-8 rounded-[1.5rem] flex items-center gap-8 min-w-[320px] shadow-xl"
            style={{ backgroundColor: COLORS.primary }}
          >
            <div>
              <span
                className="text-xs font-bold uppercase opacity-70"
                style={{ letterSpacing: "0.18em" }}
              >
                Final Score
              </span>
              <div
                className="text-5xl font-black mt-1"
                style={{ fontFamily: "Manrope, sans-serif" }}
              >
                {result.summary.finalScore}%
              </div>
            </div>
            <div className="h-12 w-px bg-white/20" />
            <div className="text-sm font-medium leading-tight">
              <span
                className="block font-bold"
                style={{ color: COLORS.secondaryFixedDim }}
              >
                {result.summary.verdict}
              </span>
              <span>{`Confidence: ${result.summary.confidence}`}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[340px,1fr] gap-8">
          <div
            className="p-6 rounded-[1.5rem] border shadow-sm h-fit"
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
                  Uploaded Media
                </h3>
                <p
                  className="text-sm"
                  style={{ color: COLORS.onSurfaceVariant }}
                >
                  Current input attached to the dashboard.
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
                Input
              </span>
            </div>

            <div
              className="rounded-[1.5rem] overflow-hidden min-h-[280px] flex items-center justify-center"
              style={{
                backgroundColor: COLORS.surfaceContainerLow,
                border: `1px solid rgba(193,199,203,0.2)`,
              }}
            >
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Uploaded preview"
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
                    No preview available
                  </h4>
                  <p
                    className="text-sm"
                    style={{ color: COLORS.onSurfaceVariant }}
                  >
                    Upload an image from the first page to attach it to the
                    dashboard.
                  </p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 gap-4 mt-5">
              <InfoCard
                label="File Name"
                value={fileInfo.name || "Unknown"}
                breakAll
              />
              <div className="grid grid-cols-2 gap-4">
                <InfoCard label="Type" value={fileInfo.type || "Unknown"} />
                <InfoCard label="Size" value={fileInfo.size || "Unknown"} />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {result.factors.map((factor, index) => (
              <AnimatedFactorCard
                key={`${factor.title}-${index}`}
                factor={factor}
                index={index}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          className="md:col-span-2 text-white p-10 rounded-[1.5rem] relative overflow-hidden flex flex-col justify-end min-h-[360px]"
          style={{ backgroundColor: COLORS.primaryContainer }}
        >
          <div
            className="absolute top-0 right-0 w-64 h-64 opacity-20 blur-3xl -mr-20 -mt-20"
            style={{ backgroundColor: COLORS.secondary }}
          />

          <div className="relative z-10">
            <h3
              className="text-3xl font-bold mb-4"
              style={{ fontFamily: "Manrope, sans-serif" }}
            >
              {result.notes.heroTitle}
            </h3>
            <p
              className="text-lg mb-8 max-w-2xl"
              style={{ color: COLORS.onPrimaryContainer }}
            >
              {result.notes.heroText}
            </p>

            <div className="flex gap-4 z-10 flex-wrap">
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase"
                style={{
                  backgroundColor: COLORS.surfaceContainerLowest,
                  color: COLORS.primary,
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              >
                Review Summary
              </button>
              <button
                className="px-6 py-3 font-bold rounded-[1rem] text-sm uppercase border"
                style={{
                  backgroundColor: "rgba(255,255,255,0.10)",
                  color: COLORS.onPrimary,
                  borderColor: "rgba(255,255,255,0.20)",
                  letterSpacing: "0.14em",
                }}
                type="button"
                onClick={onBack}
              >
                Test Another Image
              </button>
            </div>
          </div>
        </div>

        <div
          className="p-8 rounded-[1.5rem] flex flex-col justify-between"
          style={{ backgroundColor: COLORS.surfaceContainerHigh }}
        >
          <div>
            <MaterialIcon
              className="text-4xl mb-6"
              style={{ color: COLORS.primary }}
            >
              hub
            </MaterialIcon>
            <h4
              className="text-xl font-bold mb-2"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
              }}
            >
              {result.notes.sideTitle}
            </h4>
            <p className="text-sm" style={{ color: COLORS.onSurfaceVariant }}>
              This block is ready to display backend-related status later.
            </p>
          </div>
          <div className="mt-8 flex flex-col gap-3">
            {result.notes.sideItems.map((item, index) => (
              <div
                key={`${item.label}-${index}`}
                className="flex items-center justify-between text-xs py-2"
                style={{
                  borderBottom:
                    index !== result.notes.sideItems.length - 1
                      ? `1px solid rgba(193,199,203,0.2)`
                      : "none",
                }}
              >
                <span style={{ color: COLORS.outline }}>{item.label}</span>
                <span className="font-bold" style={{ color: COLORS.primary }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

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