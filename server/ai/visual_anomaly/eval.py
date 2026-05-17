from predict import predict, load_model
import pandas as pd
import os

try:
  load_model()
except Exception as e:
  print(f"Error while loading AI Image Detector model: {e}")
  raise

predictions = []

print(f"starting evaluation")
try:
  train_df = pd.read_csv("./evaldata/train.csv").iloc[:50000]
  x = train_df["file_name"]
  y = train_df["label"].astype(int)

  total = len(x)

  for i in range(total):
    file_name = x.iloc[i]
    label = y.iloc[i]

    img_path = os.path.join("./evaldata/", file_name)
    if not os.path.exists(img_path):
      print(f"File not found: {img_path}")
      continue

    with open(img_path, "rb") as f:
      img_bytes = f.read()

    result = predict(img_bytes)

    predicted_idx = int(result["predicted_idx"])
    predictions.append(predicted_idx)
    
    if (i % 5000 == 0):
      print(f"Processed {i}/{total} files")

except Exception as e:
  print(f"Error while evaluating AI Image Detector model: {e}")

TP = 0
TN = 0
FP = 0
FN = 0

for i in range(len(predictions)):
    if (predictions[i] == 1 and y.iloc[i] == 1):
        TP += 1
    elif (predictions[i] == 0 and y.iloc[i] == 0):
        TN += 1
    elif (predictions[i] == 1 and y.iloc[i] == 0):
        FP += 1
    elif (predictions[i] == 0 and y.iloc[i] == 1):
        FN += 1

accuracy = (TP + TN) / total
precision = (TP / (TP + FP)) if (TP + FP) > 0 else 0
recall = (TP / (TP + FN)) if (TP + FN) > 0 else 0
f1_score = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) > 0
    else 0
)

print(f"Evaluated files: {total}")
print(f"TP: {TP}, TN: {TN}, FP: {FP}, FN: {FN}")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-score: {f1_score:.4f}")


