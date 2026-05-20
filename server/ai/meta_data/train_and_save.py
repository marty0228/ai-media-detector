import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_auc_score,
    log_loss,
    brier_score_loss,
)

from fetch_metadata import collect_images_from_folder


# ============================================================
# 0. 학습 설정
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.2

N_ESTIMATORS = 300
MAX_DEPTH = 10
MIN_SAMPLES_SPLIT = 4
MIN_SAMPLES_LEAF = 2


# ============================================================
# 1. 그래프 저장 함수
# ============================================================

def save_confusion_matrix_image(y_true, y_pred, title, save_path):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Real", "AI"],
    )

    disp.plot(values_format="d")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


def save_bar_chart(df, x_col, y_col, title, ylabel, save_path, rotation=45, ylim=None):
    plot_df = df.copy().sort_values(by=y_col, ascending=True)

    plt.figure(figsize=(14, 6))
    plt.bar(plot_df[x_col], plot_df[y_col])
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right")

    if ylim is not None:
        plt.ylim(*ylim)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


def save_confidence_distribution(detail_df, save_path):
    plt.figure(figsize=(10, 6))
    plt.hist(detail_df["confidence"], bins=20, range=(0.5, 1.0))
    plt.title("Confidence Distribution on Validation Dataset")
    plt.xlabel("Confidence")
    plt.ylabel("Image Count")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


def save_confidence_bin_accuracy(confidence_bin_df, save_path):
    plt.figure(figsize=(10, 6))
    plt.bar(
        confidence_bin_df["confidence_bin"].astype(str),
        confidence_bin_df["accuracy"],
    )
    plt.title("Accuracy by Confidence Range")
    plt.xlabel("Confidence Range")
    plt.ylabel("Accuracy")
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


def save_ai_probability_by_source_type(detail_df, save_path):
    source_types = detail_df["source_type"].unique().tolist()

    data = [
        detail_df[detail_df["source_type"] == source_type]["ai_probability"].values
        for source_type in source_types
    ]

    plt.figure(figsize=(16, 6))
    plt.boxplot(data, tick_labels=source_types, showfliers=False)
    plt.title("AI Probability Distribution by Source Type")
    plt.xlabel("Source Type")
    plt.ylabel("AI Probability")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


# ============================================================
# 2. Feature / Label 전처리 함수
# ============================================================

def prepare_features(df: pd.DataFrame):
    """
    메타데이터 DataFrame을 RandomForest 입력 feature X와 label y로 분리한다.

    처리 내용:
    - raw 문자열 컬럼 제거
    - camera_brand, software_type one-hot encoding
    - bool 컬럼 int 변환
    - 결측치 0 처리
    """

    fill_values = {
        "make_raw": "None",
        "model_raw": "None",
        "camera_brand": "none",
        "software_raw": "None",
        "software_type": "none",
    }

    df = df.fillna(fill_values)

    drop_cols = [
        "label",
        "filename",
        "filepath",
        "path",
        "relative_path",
        "source_type",
        "split",
        "original_id",
        "make_raw",
        "model_raw",
        "software_raw",
        "note",
    ]

    X = df.drop(columns=drop_cols, errors="ignore")
    y = df["label"].astype(int)

    cat_cols = [c for c in ["camera_brand", "software_type"] if c in X.columns]

    if cat_cols:
        X = pd.get_dummies(X, columns=cat_cols)

    bool_cols = [c for c in X.columns if X[c].dtype == "bool"]

    for c in bool_cols:
        X[c] = X[c].astype(int)

    X = X.fillna(0)

    return X, y


# ============================================================
# 3. 메인 학습 함수
# ============================================================

def main():
    print("Starting final metadata model training...")

    # ------------------------------------------------------------
    # 3.1 경로 설정
    # ------------------------------------------------------------

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "model")
    output_dir = os.path.join(model_dir, "final_train_results")

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    dataset_dir = os.path.join(base_dir, "train_datasets")
    real_dir = os.path.join(dataset_dir, "real")
    ai_dir = os.path.join(dataset_dir, "ai")

    if not os.path.exists(real_dir):
        raise FileNotFoundError(f"real 폴더를 찾을 수 없습니다: {real_dir}")

    if not os.path.exists(ai_dir):
        raise FileNotFoundError(f"ai 폴더를 찾을 수 없습니다: {ai_dir}")

    # ------------------------------------------------------------
    # 3.2 이미지 메타데이터 수집
    # ------------------------------------------------------------

    rows = []
    rows += collect_images_from_folder(real_dir, 0)
    rows += collect_images_from_folder(ai_dir, 1)

    if not rows:
        raise ValueError("수집된 이미지가 없습니다.")

    df = pd.DataFrame(rows)
    df["label"] = df["label"].astype(int)

    print("\n[Dataset Summary]")
    print(f"Total images: {len(df)}")
    print(df["label"].value_counts().rename({0: "Real", 1: "AI"}))

    print("\n[Source Type Count]")
    print(df["source_type"].value_counts().sort_index())

    # 전체 메타데이터 CSV 저장
    dataset_csv = os.path.join(model_dir, "metadata_dataset_expanded.csv")
    df.to_csv(dataset_csv, index=False, encoding="utf-8-sig")
    print(f"\nMetadata CSV saved: {dataset_csv}")

    # ------------------------------------------------------------
    # 3.3 Feature / Label 생성
    # ------------------------------------------------------------

    X, y = prepare_features(df)
    final_columns = X.columns.tolist()

    print(f"\nFinal feature count: {len(final_columns)}")
    print(final_columns)

    # ------------------------------------------------------------
    # 3.4 Train / Valid 8:2 분리
    # ------------------------------------------------------------
    # source_type 기준으로 stratify하여 각 세부 유형이 train/valid에 같은 비율로 들어가게 한다.
    # 예: ai_jpg_converted 100장 -> train 80장, valid 20장

    train_idx, valid_idx = train_test_split(
        df.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["source_type"],
    )

    X_train = X.loc[train_idx, final_columns]
    X_valid = X.loc[valid_idx, final_columns]

    y_train = y.loc[train_idx]
    y_valid = y.loc[valid_idx]

    df_train = df.loc[train_idx].copy()
    df_valid = df.loc[valid_idx].copy()

    df_train["split"] = "train"
    df_valid["split"] = "valid"

    split_df = pd.concat([df_train, df_valid], axis=0).sort_index()

    split_csv = os.path.join(output_dir, "train_valid_split.csv")
    split_df[["filename", "filepath", "label", "source_type", "split"]].to_csv(
        split_csv,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n[Train / Valid Split]")
    print(f"Train size: {len(y_train)}")
    print(f"Valid size: {len(y_valid)}")

    print("\n[Train Source Type Count]")
    print(df_train["source_type"].value_counts().sort_index())

    print("\n[Valid Source Type Count]")
    print(df_valid["source_type"].value_counts().sort_index())

    # ------------------------------------------------------------
    # 3.5 RandomForest 모델 학습
    # ------------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_split=MIN_SAMPLES_SPLIT,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )

    print("\nTraining RandomForest...")
    model.fit(X_train, y_train)

    # ------------------------------------------------------------
    # 3.6 Train / Valid 예측
    # ------------------------------------------------------------

    train_pred = model.predict(X_train)
    train_proba = model.predict_proba(X_train)[:, 1]
    train_confidence = np.maximum(train_proba, 1 - train_proba)

    valid_pred = model.predict(X_valid)
    valid_proba = model.predict_proba(X_valid)[:, 1]
    valid_confidence = np.maximum(valid_proba, 1 - valid_proba)

    valid_correct_class_probability = np.where(
        y_valid.values == 1,
        valid_proba,
        1 - valid_proba,
    )

    valid_correct = y_valid.values == valid_pred

    # ------------------------------------------------------------
    # 3.7 Train 성능 지표 계산
    # ------------------------------------------------------------

    train_acc = accuracy_score(y_train, train_pred)
    train_precision = precision_score(y_train, train_pred, zero_division=0)
    train_recall = recall_score(y_train, train_pred, zero_division=0)
    train_f1 = f1_score(y_train, train_pred, zero_division=0)
    train_auc = roc_auc_score(y_train, train_proba)
    train_logloss = log_loss(y_train, train_proba, labels=[0, 1])
    train_brier = brier_score_loss(y_train, train_proba)

    # ------------------------------------------------------------
    # 3.8 Valid 성능 지표 계산
    # ------------------------------------------------------------

    valid_acc = accuracy_score(y_valid, valid_pred)
    valid_precision = precision_score(y_valid, valid_pred, zero_division=0)
    valid_recall = recall_score(y_valid, valid_pred, zero_division=0)
    valid_f1 = f1_score(y_valid, valid_pred, zero_division=0)
    valid_auc = roc_auc_score(y_valid, valid_proba)
    valid_logloss = log_loss(y_valid, valid_proba, labels=[0, 1])
    valid_brier = brier_score_loss(y_valid, valid_proba)

    valid_cm = confusion_matrix(y_valid, valid_pred, labels=[0, 1])

    # ------------------------------------------------------------
    # 3.9 콘솔 결과 출력
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("Train Result")
    print("=" * 70)
    print(f"Train Images      : {len(y_train)}")
    print(f"Accuracy          : {train_acc:.4f}")
    print(f"Precision         : {train_precision:.4f}")
    print(f"Recall            : {train_recall:.4f}")
    print(f"F1-score          : {train_f1:.4f}")
    print(f"ROC-AUC           : {train_auc:.4f}")
    print(f"Log Loss          : {train_logloss:.4f}")
    print(f"Brier Score       : {train_brier:.4f}")
    print(f"Avg Confidence    : {train_confidence.mean():.4f}")

    print("\n" + "=" * 70)
    print("Validation Result")
    print("=" * 70)
    print(f"Valid Images       : {len(y_valid)}")
    print(f"Accuracy           : {valid_acc:.4f}")
    print(f"Precision          : {valid_precision:.4f}")
    print(f"Recall             : {valid_recall:.4f}")
    print(f"F1-score           : {valid_f1:.4f}")
    print(f"ROC-AUC            : {valid_auc:.4f}")
    print(f"Log Loss           : {valid_logloss:.4f}")
    print(f"Brier Score        : {valid_brier:.4f}")
    print(f"Avg Confidence     : {valid_confidence.mean():.4f}")
    print(f"Avg Correct Prob   : {valid_correct_class_probability.mean():.4f}")
    print(f"Min Confidence     : {valid_confidence.min():.4f}")
    print(f"Low Conf < 0.60    : {(valid_confidence < 0.60).sum()}")
    print(f"Low Conf < 0.70    : {(valid_confidence < 0.70).sum()}")
    print(f"Low Conf < 0.80    : {(valid_confidence < 0.80).sum()}")

    print("\nConfusion Matrix:")
    print(valid_cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_valid,
            valid_pred,
            target_names=["Real", "AI"],
            digits=4,
            zero_division=0,
        )
    )

    # ------------------------------------------------------------
    # 3.10 Valid 상세 결과 테이블 생성
    # ------------------------------------------------------------

    valid_detail_df = pd.DataFrame(
        {
            "filename": df_valid["filename"].values,
            "filepath": df_valid["filepath"].values,
            "source_type": df_valid["source_type"].values,
            "true_label": y_valid.values,
            "pred_label": valid_pred,
            "ai_probability": valid_proba,
            "confidence": valid_confidence,
            "correct_class_probability": valid_correct_class_probability,
            "correct": valid_correct,
        }
    )

    valid_detail_df["true_name"] = valid_detail_df["true_label"].map({0: "Real", 1: "AI"})
    valid_detail_df["pred_name"] = valid_detail_df["pred_label"].map({0: "Real", 1: "AI"})

    # ------------------------------------------------------------
    # 3.11 Confidence 구간별 분석
    # ------------------------------------------------------------

    bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0001]
    labels = ["50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]

    valid_detail_df["confidence_bin"] = pd.cut(
        valid_detail_df["confidence"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=False,
    )

    confidence_bin_df = (
        valid_detail_df.groupby("confidence_bin", observed=False)
        .agg(
            image_count=("filename", "count"),
            accuracy=("correct", "mean"),
            avg_confidence=("confidence", "mean"),
            avg_ai_probability=("ai_probability", "mean"),
            wrong_count=("correct", lambda x: (~x).sum()),
        )
        .reset_index()
    )

    # ------------------------------------------------------------
    # 3.12 Source Type별 분석
    # ------------------------------------------------------------

    source_type_df = (
        valid_detail_df.groupby("source_type")
        .agg(
            image_count=("filename", "count"),
            accuracy=("correct", "mean"),
            avg_confidence=("confidence", "mean"),
            avg_ai_probability=("ai_probability", "mean"),
            avg_correct_class_probability=("correct_class_probability", "mean"),
            low_conf_under_60=("confidence", lambda x: (x < 0.60).sum()),
            low_conf_under_70=("confidence", lambda x: (x < 0.70).sum()),
            low_conf_under_80=("confidence", lambda x: (x < 0.80).sum()),
            wrong_count=("correct", lambda x: (~x).sum()),
        )
        .reset_index()
    )

    source_type_df = source_type_df.sort_values(
        ["accuracy", "avg_confidence"],
        ascending=[True, True],
    )

    wrong_df = valid_detail_df[valid_detail_df["correct"] == False].copy()
    low_conf_df = valid_detail_df[valid_detail_df["confidence"] < 0.70].copy()

    # ------------------------------------------------------------
    # 3.13 CSV 저장
    # ------------------------------------------------------------

    summary_df = pd.DataFrame(
        [
            {
                "dataset": "final_metadata_dataset",
                "train_images": len(y_train),
                "valid_images": len(y_valid),
                "train_real_images": int((y_train == 0).sum()),
                "train_ai_images": int((y_train == 1).sum()),
                "valid_real_images": int((y_valid == 0).sum()),
                "valid_ai_images": int((y_valid == 1).sum()),

                "train_accuracy": train_acc,
                "train_precision_ai": train_precision,
                "train_recall_ai": train_recall,
                "train_f1_ai": train_f1,
                "train_roc_auc": train_auc,
                "train_log_loss": train_logloss,
                "train_brier_score": train_brier,
                "train_avg_confidence": train_confidence.mean(),

                "valid_accuracy": valid_acc,
                "valid_precision_ai": valid_precision,
                "valid_recall_ai": valid_recall,
                "valid_f1_ai": valid_f1,
                "valid_roc_auc": valid_auc,
                "valid_log_loss": valid_logloss,
                "valid_brier_score": valid_brier,
                "valid_avg_confidence": valid_confidence.mean(),
                "valid_avg_correct_class_probability": valid_correct_class_probability.mean(),
                "valid_min_confidence": valid_confidence.min(),
                "valid_low_conf_under_60_count": int((valid_confidence < 0.60).sum()),
                "valid_low_conf_under_70_count": int((valid_confidence < 0.70).sum()),
                "valid_low_conf_under_80_count": int((valid_confidence < 0.80).sum()),

                "false_positive_real_to_ai": int(valid_cm[0, 1]),
                "false_negative_ai_to_real": int(valid_cm[1, 0]),

                "n_estimators": N_ESTIMATORS,
                "max_depth": MAX_DEPTH,
                "min_samples_split": MIN_SAMPLES_SPLIT,
                "min_samples_leaf": MIN_SAMPLES_LEAF,
                "feature_count": len(final_columns),
            }
        ]
    )

    summary_csv = os.path.join(output_dir, "metadata_model_summary.csv")
    predictions_csv = os.path.join(output_dir, "metadata_valid_predictions.csv")
    source_type_csv = os.path.join(output_dir, "metadata_valid_by_source_type.csv")
    confidence_bin_csv = os.path.join(output_dir, "metadata_valid_confidence_bins.csv")
    wrong_csv = os.path.join(output_dir, "metadata_valid_wrong_samples.csv")
    low_conf_csv = os.path.join(output_dir, "metadata_valid_low_confidence_samples.csv")
    cm_csv = os.path.join(output_dir, "metadata_valid_confusion_matrix.csv")

    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    valid_detail_df.to_csv(predictions_csv, index=False, encoding="utf-8-sig")
    source_type_df.to_csv(source_type_csv, index=False, encoding="utf-8-sig")
    confidence_bin_df.to_csv(confidence_bin_csv, index=False, encoding="utf-8-sig")
    wrong_df.to_csv(wrong_csv, index=False, encoding="utf-8-sig")
    low_conf_df.to_csv(low_conf_csv, index=False, encoding="utf-8-sig")

    pd.DataFrame(
        valid_cm,
        index=["true_real", "true_ai"],
        columns=["pred_real", "pred_ai"],
    ).to_csv(cm_csv, encoding="utf-8-sig")

    # ------------------------------------------------------------
    # 3.14 PNG 그래프 저장
    # ------------------------------------------------------------

    cm_png = os.path.join(output_dir, "metadata_valid_confusion_matrix.png")
    source_acc_png = os.path.join(output_dir, "metadata_source_type_accuracy.png")
    source_conf_png = os.path.join(output_dir, "metadata_source_type_confidence.png")
    source_wrong_png = os.path.join(output_dir, "metadata_wrong_count_by_source_type.png")
    confidence_dist_png = os.path.join(output_dir, "metadata_confidence_distribution.png")
    confidence_bin_png = os.path.join(output_dir, "metadata_confidence_bin_accuracy.png")
    ai_prob_box_png = os.path.join(output_dir, "metadata_ai_probability_by_source_type.png")

    save_confusion_matrix_image(
        y_valid,
        valid_pred,
        "Final Metadata Model Validation Confusion Matrix",
        cm_png,
    )

    save_bar_chart(
        source_type_df,
        x_col="source_type",
        y_col="accuracy",
        title="Accuracy by Source Type",
        ylabel="Accuracy",
        save_path=source_acc_png,
        ylim=(0, 1.05),
    )

    save_bar_chart(
        source_type_df,
        x_col="source_type",
        y_col="avg_confidence",
        title="Average Confidence by Source Type",
        ylabel="Average Confidence",
        save_path=source_conf_png,
        ylim=(0.5, 1.05),
    )

    save_bar_chart(
        source_type_df,
        x_col="source_type",
        y_col="wrong_count",
        title="Wrong Prediction Count by Source Type",
        ylabel="Wrong Count",
        save_path=source_wrong_png,
    )

    save_confidence_distribution(valid_detail_df, confidence_dist_png)
    save_confidence_bin_accuracy(confidence_bin_df, confidence_bin_png)
    save_ai_probability_by_source_type(valid_detail_df, ai_prob_box_png)

    # ------------------------------------------------------------
    # 3.15 Feature Importance 저장
    # ------------------------------------------------------------

    feature_importance_df = pd.DataFrame(
        {
            "feature": final_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    feature_importance_csv = os.path.join(model_dir, "feature_importance.csv")
    feature_importance_df.to_csv(feature_importance_csv, index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------
    # 3.16 최종 모델 및 컬럼 저장
    # ------------------------------------------------------------

    model_path = os.path.join(model_dir, "rf_metadata_model.pkl")
    cols_path = os.path.join(model_dir, "model_columns.pkl")

    joblib.dump(model, model_path)
    joblib.dump(final_columns, cols_path)

    # ------------------------------------------------------------
    # 3.17 저장 결과 출력
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("Saved Files")
    print("=" * 70)
    print(f"- dataset csv: {dataset_csv}")
    print(f"- model: {model_path}")
    print(f"- columns: {cols_path}")
    print(f"- feature importance: {feature_importance_csv}")
    print(f"- summary: {summary_csv}")
    print(f"- predictions: {predictions_csv}")
    print(f"- source type result: {source_type_csv}")
    print(f"- confidence bins: {confidence_bin_csv}")
    print(f"- confusion matrix image: {cm_png}")

    print("\nTraining complete.")


# ============================================================
# 4. 실행 진입점
# ============================================================

if __name__ == "__main__":
    main()