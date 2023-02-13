import os
import sys
from pathlib import Path

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from utils.redis import backoff


def test_backoff():
    backoffTime = backoff()
    assert isinstance(backoffTime, float)  # nosec


def test_looped_backoff():
    totalTime = 0
    for _ in range(20):
        totalTime += backoff()
    assert totalTime > 60.0  # nosec
