import os
import sys
import uuid
from pathlib import Path

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from cache import CommandKeyBuilder


def test_key_builder_defaults():
    assert CommandKeyBuilder() == "cache:akari:None:None"  # nosec


def test_key_builder_params():
    assert CommandKeyBuilder(id=123, command="test") == "cache:akari:123:test"  # nosec


def test_key_builder_id():
    id = str(uuid.uuid4())
    assert CommandKeyBuilder(id=id, command="test") == f"cache:akari:{id}:test"  # nosec
