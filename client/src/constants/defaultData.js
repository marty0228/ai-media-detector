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

export const defaultFile = {
  name: "No image uploaded",
  type: "Unknown",
  size: "Unknown",
};
