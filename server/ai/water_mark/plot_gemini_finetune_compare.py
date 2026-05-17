from pathlib import Path

import matplotlib.pyplot as plt


BEFORE = {
    "Gemini detection rate (%)": 25.0,
    "Average confidence": 0.0870,
    "Max confidence": 0.2880,
}

AFTER = {
    "Gemini detection rate (%)": 70.0,
    "Average confidence": 0.3613,
    "Max confidence": 0.7823,
}


def main() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # Left panel: detection rate
    rate_ax = axes[0]
    rate_values = [BEFORE["Gemini detection rate (%)"], AFTER["Gemini detection rate (%)"]]
    rate_bars = rate_ax.bar([0, 1], rate_values, width=0.5, color=["#9aa0a6", "#1f77b4"])
    rate_ax.set_title("Detection Rate", fontsize=13, pad=10)
    rate_ax.set_xticks([0, 1])
    rate_ax.set_xticklabels(["Before", "After"])
    rate_ax.set_ylim(0, 100)
    rate_ax.set_ylabel("%")

    for bar in rate_bars:
        height = bar.get_height()
        rate_ax.annotate(
            f"{height:.1f}%",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Right panel: confidence metrics
    conf_ax = axes[1]
    conf_labels = ["Average confidence", "Max confidence"]
    before_conf = [BEFORE[label] for label in conf_labels]
    after_conf = [AFTER[label] for label in conf_labels]
    x = range(len(conf_labels))
    width = 0.34

    before_bars = conf_ax.bar([i - width / 2 for i in x], before_conf, width, label="Before", color="#9aa0a6")
    after_bars = conf_ax.bar([i + width / 2 for i in x], after_conf, width, label="After", color="#1f77b4")
    conf_ax.set_title("Confidence", fontsize=13, pad=10)
    conf_ax.set_ylabel("Score")
    conf_ax.set_xticks(list(x))
    conf_ax.set_xticklabels(conf_labels, rotation=12, ha="right")
    conf_ax.set_ylim(0, 1.0)
    conf_ax.legend(frameon=False)

    for bar in list(before_bars) + list(after_bars):
        height = bar.get_height()
        conf_ax.annotate(
            f"{height:.3f}",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.suptitle("Gemini Watermark Fine-tuning Comparison", fontsize=16, y=1.02)
    fig.tight_layout()

    output_dir = Path(__file__).resolve().parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "gemini_finetune_compare.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
