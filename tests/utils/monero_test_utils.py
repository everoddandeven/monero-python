from typing import Any, Optional
from monero import MoneroNetworkType, MoneroUtils

class MoneroTestUtils:

    @classmethod
    def assert_false(cls, expr: Any):
        assert expr == False

    @classmethod
    def assert_true(cls, expr: Any):
        assert expr == True

    @classmethod
    def assert_not_none(cls, expr: Any):
        assert expr is not None

    @classmethod
    def test_invalid_address(cls, address: Optional[str], networkType: MoneroNetworkType) -> None:
        if address is None:
            return

        cls.assert_false(MoneroUtils.is_valid_address(address, networkType))
        try:
            MoneroUtils.validate_address(address, networkType)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_private_view_key(cls, privateViewKey: Optional[str]):
        if privateViewKey is None:
            return
        
        cls.assert_false(MoneroUtils.is_valid_private_view_key(privateViewKey));
        try:
            MoneroUtils.validate_private_view_key(privateViewKey);
            raise Exception("Should have thrown exception");
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)
  

    @classmethod
    def test_invalid_public_view_key(cls, public_view_key: Optional[str]) -> None:
        if public_view_key is None:
            return

        cls.assert_false(MoneroUtils.is_valid_public_view_key(public_view_key))
        try:
            MoneroUtils.validate_public_view_key(public_view_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_private_spend_key(cls, privateSpendKey: Optional[str]):
        if privateSpendKey is None:
            return

        try:
            cls.assert_false(MoneroUtils.is_valid_private_spend_key(privateSpendKey))
            MoneroUtils.validate_private_spend_key(privateSpendKey)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)


    @classmethod
    def test_invalid_public_spend_key(cls, publicSpendKey: Optional[str]):
        if publicSpendKey is None:
            return
        
        cls.assert_false(MoneroUtils.is_valid_public_spend_key(publicSpendKey))
        try:
            MoneroUtils.validate_public_spend_key(publicSpendKey)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)
  
  