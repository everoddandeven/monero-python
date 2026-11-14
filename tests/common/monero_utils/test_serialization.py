from __future__ import annotations

import logging
from typing import Any

import pytest
from monero import MoneroUtils

from .base_test_monero_utils import BaseTestMoneroUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtilsSerialization")


@pytest.mark.unit
class TestMoneroUtilsSerialization(BaseTestMoneroUtils):
    """Monero utilities serialization unit tests."""

    # Can serialize heights with small numbers
    def test_serialize_heights_small(self) -> None:
        json_map: dict[Any, Any] = {
          "heights": [111, 222, 333]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # Can serialize heights with big numbers
    def test_serialize_heights_big(self) -> None:
        json_map: dict[Any, Any] = {
          "heights": [123456, 1234567, 870987]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # can serialize height with large unsigned values
    def test_serialize_large_unsigned_values(self) -> None:
        big_value: int = 18446744073709551615  # UINT64_MAX
        json_map: dict[Any, Any] = {
          "heights": [big_value]
        }
        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2
        assert json_map2["heights"][0] > 0, "uint64 > INT64_MAX must not serialize as negative"

    # Can serialize jsonMap with text
    def test_serialize_text_short(self, config: BaseTestMoneroUtils.Config) -> None:
        assert config.serialization_msg is not None and config.serialization_msg != ""
        json_map: dict[Any, Any] = {
            "msg": config.serialization_msg
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # Can serialize json with long text
    def test_serialize_text_long(self, config: BaseTestMoneroUtils.Config) -> None:
        msg: str = config.serialization_msg
        json_map: dict[str, str] = {
            "msg": f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n" +
            f"{msg}\n"
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2
