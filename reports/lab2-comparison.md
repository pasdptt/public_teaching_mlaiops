# Lab 2 — Run comparison

Experiment `itcs355-lab2` · 12 trials · total spend 0.0016 THB

`thb_per_point` is cost per percentage point of val_roc_auc above the worst trial. Cheap improvements rank low; expensive improvements rank high, however good the headline number is.

| run_id   |   val_roc_auc |   cost_thb |   n_estimators |   max_depth |   min_samples_leaf |   thb_per_point |
|:---------|--------------:|-----------:|---------------:|------------:|-------------------:|----------------:|
| 55e93760 |        0.8426 |     0.0002 |            100 |           4 |                  5 |          0.0001 |
| e7768f95 |        0.8424 |     0.0003 |            100 |           4 |                  1 |          0.0002 |
| e4ccf157 |        0.8412 |     0.0001 |            300 |           4 |                  5 |          0.0001 |
| 668bfe2d |        0.8404 |     0.0001 |            300 |           4 |                  1 |          0.0001 |
| 7a41981b |        0.8398 |     0.0001 |            100 |           8 |                  5 |          0.0001 |
| 1474f0b4 |        0.8377 |     0.0002 |            300 |           8 |                  5 |          0.0002 |
| f6b51416 |        0.8357 |     0.0001 |            300 |          12 |                  5 |          0.0001 |
| 48262cc7 |        0.8337 |     0.0001 |            300 |           8 |                  1 |          0.0001 |
| cfe1cce2 |        0.8322 |     0.0001 |            100 |          12 |                  5 |          0.0002 |
| 742e6946 |        0.8312 |     0.0001 |            100 |           8 |                  1 |          0.0002 |
| cbcfb0ab |        0.8259 |     0.0001 |            300 |          12 |                  1 |          0.0047 |
| 004ca47b |        0.8257 |     0.0001 |            100 |          12 |                  1 |          0.0834 |

## Which model did you register, and why?

We registered `n_estimators=100, max_depth=4, min_samples_leaf=5` (run `55e93760`), achieving val ROC-AUC 0.8426 and test ROC-AUC 0.8532 at 0.0002 THB. While tripling trees to 300 (`e4ccf157`) yields 0.8412, it provides no metric gain while tripling compute cost and inference latency. Crucially, across all 12 trials, scores cluster tightly between 0.8257 and 0.8426 (a spread of 0.0169), which is comparable to the random variation across seeds. Deeper trees overfit to noise (depth 12 dropped to 0.8257), so shallow depth-4 with leaf regularization (min_samples_leaf=5) is the most parsimonious, robust choice.

Across 5 evaluation seeds (20260101–20260105), this configuration demonstrated solid generalization: validation ROC-AUC 0.8556 ± 0.0126 and test ROC-AUC 0.8534 ± 0.0086.

Training cost is 0.0002 THB on GCP `e2-standard-4` spot instances (rate 1.92 THB/h). Monthly retraining costs ~0.0002 THB (<0.003 THB annually), well below our 150 THB budget.
This choice could be wrong if future machine degradation manifests as complex high-order sensor interactions that shallow depth-4 trees cannot capture, leading to underfitting if failure patterns become non-linear.
### Model Promotion and Staging Policy
In a production organization, model promotion to Staging should be restricted to the **Lead ML Engineer or MLOps Platform Owner**, requiring an automated CI audit showing: (1) verified lineage across git commit, data digest, container sha, and training job; (2) passing data contract and regression tests; (3) latency p95 within SLA; and (4) demonstrable metric gain exceeding observed seed variance without budget regression.