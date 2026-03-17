// 로컬 스토리지 키 정의
export const STORAGE_KEYS = {
  result: "aiAuthenticatorResult", // 분석 결과 저장 키
  file: "aiAuthenticatorFile",     // 선택된 파일 정보 저장 키
  preview: "aiAuthenticatorPreview", // 이미지 프리뷰 데이터 저장 키
};

// 앱 전역에서 사용하는 색상 팔레트 정의
export const COLORS = {
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

// 기본 분석 결과 목업 데이터 (백엔드 연결 전 프로토타입용)
export const defaultResult = {
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

// 기본 파일 정보 상태
export const defaultFile = {
  name: "No image uploaded",
  type: "Unknown",
  size: "Unknown",
};
