import os
import sys
import uuid
from pathlib import Path

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from cache import CommandKeyBuilder


def test_key_builder_defaults():
    assert CommandKeyBuilder() == "None:None:None:None"  # nosec


def test_key_builder_params():
    assert (
        CommandKeyBuilder(prefix="cache", namespace="akari", id=123, command="test")
        == "cache:akari:123:test"
    )  # nosec


def test_key_builder_id():
    id = uuid.uuid4()
    assert (
        CommandKeyBuilder(prefix="cache", namespace="akari", id=id, command="test")
        == f"cache:akari:{str(id)}:test"
    )  # nosec
