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

TODO(Lab 2): 200 words maximum. Must address all four:

1. Why this model rather than the highest-scoring one, if they differ
2. The variance across seeds for your chosen configuration
3. What it costs to train, and to retrain monthly
4. One way this choice could be wrong

An answer that only says "highest validation score" scores zero on this task.