"""Seed control. Log the seed as a parameter, never leave it as a comment."""
from __future__ import annotations

import os
import random

import numpy as np

DEFAULT_SEED = 20260101


def set_all(seed: int = DEFAULT_SEED) -> int:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    # Adding a deep-learning framework? Seed it here too, and say so in your README.
    return seed
