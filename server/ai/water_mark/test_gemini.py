import os
import sys
import argparse

# Ensure server folder is on path so package `ai` can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai.water_mark.predict import load_model, predict


def run(folder: str, thresholds=None):
    if thresholds is None:
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    img_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp'))]
    if not img_files:
        print('No images found in', folder)
        return

    print(f'Loading model and evaluating {len(img_files)} images...')
    load_model()

    results = []
    for fn in sorted(img_files):
        path = os.path.join(folder, fn)
        try:
            with open(path, 'rb') as f:
                b = f.read()
            r = predict(b)
            conf = float(r.get('confidence') or 0.0)
            idx = int(r.get('predicted_idx') or 0)
        except Exception as e:
            conf = 0.0
            idx = 0
            print(f'Error for {fn}:', e)
        results.append((fn, conf, idx))

    # Print per-image results
    print('\nPer-image results:')
    print('filename\tconfidence\tpredicted_idx')
    for fn, conf, idx in results:
        print(f'{fn}\t{conf:.4f}\t{idx}')

    # Summary per threshold
    print('\nThreshold summary:')
    for t in thresholds:
        tp = fp = tn = fn_count = 0
        for _, conf, idx in results:
            pred = 1 if conf >= t else 0
            # We don't have ground truth labels here; show counts of predicted positives/negatives
            if pred == 1:
                tp += 1
            else:
                tn += 1
        print(f'threshold {t:.2f}: predicted positives={tp}, negatives={tn}')


def main():
    p = argparse.ArgumentParser(description='Run watermark predictions on a folder of images')
    p.add_argument('folder', help='Folder containing images to test')
    p.add_argument('--thresholds', help='Comma-separated thresholds, e.g. 0.3,0.5,0.7', default='0.3,0.4,0.5,0.6,0.7')
    args = p.parse_args()
    thr = [float(x) for x in args.thresholds.split(',') if x.strip()]
    run(args.folder, thr)


if __name__ == '__main__':
    main()
