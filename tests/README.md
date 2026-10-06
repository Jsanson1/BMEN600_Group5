# Tests

Unit tests for `src/gaitpdb`, on synthetic signals with known timing (no dataset needed):

```
python -m pip install -r requirements-dev.txt
python -m pytest
```

They pin down what later changes must keep: heel strikes and toe offs at the threshold crossings, the stride rules (absolute limits, swing fraction, the relative rule that drops a doubled stride), the quirks of `demographics.txt`, that the shared evaluation never puts one participant on both sides of a split, and the statistics the model comparison relies on (`test_comparison.py`: the corrected interval and t-test for repeated cross-validation against their formula, the rank AUC against scikit-learn's, the paired bootstrap, and the files each model script writes).
