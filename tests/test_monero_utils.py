import pytest
from typing import Any
from monero import (
    MoneroNetworkType, MoneroIntegratedAddress, MoneroUtils, MoneroTxConfig
)
from utils import MoneroTestUtils


@pytest.mark.monero_utils
class TestMoneroUtils:

    # Can get integrated addresses
    def test_get_integrated_address(self):
        primary_address: str = "58qRVVjZ4KxMX57TH6yWqGcH5AswvZZS494hWHcHPt6cDkP7V8AqxFhi3RKXZueVRgUnk8niQGHSpY5Bm9DjuWn16GDKXpF"
        subaddress: str = "7B9w2xieXjhDumgPX39h1CAYELpsZ7Pe8Wqtr3pVL9jJ5gGDqgxjWt55gTYUCAuhahhM85ajEp6VbQfLDPETt4oT2ZRXa6n"
        payment_id: str = "03284e41c342f036"
        network_type: MoneroNetworkType = MoneroNetworkType.STAGENET

        # get integrated address with randomly generated payment id
        integrated_address: MoneroIntegratedAddress = MoneroUtils.get_integrated_address(network_type, primary_address, "")
        assert primary_address == integrated_address.standard_address
        assert 16 == len(integrated_address.payment_id)
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with specific payment id
        integrated_address = MoneroUtils.get_integrated_address(network_type, primary_address, payment_id)
        assert primary_address == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with subaddress
        integrated_address = MoneroUtils.get_integrated_address(network_type, subaddress, payment_id)
        assert subaddress == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with invalid payment id
        try:
          MoneroUtils.get_integrated_address(network_type, primary_address, "123")
          raise Exception("Getting integrated address with invalid payment id should have failed")
        except Exception as err:
          assert "Invalid payment id" == str(err)

    # Can serialize heights with small numbers
    def test_serialize_heights_small(self):
        jsonMap: dict[Any, Any] = {
          "heights": [111, 222, 333]
        }

        binary: bytes = MoneroUtils.dict_to_binary(jsonMap)

        MoneroTestUtils.assert_true(len(binary) > 0)

        jsonMap2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        
        assert jsonMap == jsonMap2

    # Can serialize heights with big numbers
    def test_serialize_heights_big(self):
        jsonMap: dict[Any, Any] = {
          "heights": [123456, 1234567, 870987]
        }

        binary: bytes = MoneroUtils.dict_to_binary(jsonMap)
        MoneroTestUtils.assert_true(len(binary) > 0)
        jsonMap2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert jsonMap == jsonMap2

    # Can serialize jsonMap with text
    def test_serialize_text_short(self):
        jsonMap: dict[Any, Any] = {
            "msg": "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        }

        binary: bytes = MoneroUtils.dict_to_binary(jsonMap)
        MoneroTestUtils.assert_true(len(binary) > 0)
        jsonMap2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        
        assert jsonMap == jsonMap2

    # Can serialize json with long text
    def test_serialize_text_long(self):
        jsonMap: dict[str, str] = {
            "msg": "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" +
                "Hello there my good man lets make a nice long text to test with lots of exclamation marks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
        }

        binary: bytes = MoneroUtils.dict_to_binary(jsonMap)
        MoneroTestUtils.assert_true(len(binary) > 0)
        jsonMap2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert jsonMap == jsonMap2

    # Can validate addresses
    def test_address_validation(self):

        # test mainnet primary address validation
        assert (MoneroUtils.is_valid_address("42U9v3qs5CjZEePHBZHwuSckQXebuZu299NSmVEmQ41YJZQhKcPyujyMSzpDH4VMMVSBo3U3b54JaNvQLwAjqDhKS3rvM3L", MoneroNetworkType.MAINNET)) is True
        assert (MoneroUtils.is_valid_address("48ZxX3Y2y5s4nJ8fdz2w65TrTEp9PRsv5J8iHSShkHQcE2V31FhnWptioNst1K9oeDY4KpWZ7v8V2BZNVa4Wdky89iqmPz2", MoneroNetworkType.MAINNET)) is True
        assert (MoneroUtils.is_valid_address("48W972Fx1SQMCHVKENnPpM7tRcL5oWMgpMCqQDbhH8UrjDFg2H9i5AQWXuU1qacJgUUCVLTsgDmZKXGz1vPLXY8QB5ypYqG", MoneroNetworkType.MAINNET)) is True

        # test mainnet integrated address validation
        MoneroUtils.validate_address("4CApvrfMgUFZEePHBZHwuSckQXebuZu299NSmVEmQ41YJZQhKcPyujyMSzpDH4VMMVSBo3U3b54JaNvQLwAjqDhKeGLQ9vfRBRKFKnBtVH", MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address("4JGdXrMXaMP4nJ8fdz2w65TrTEp9PRsv5J8iHSShkHQcE2V31FhnWptioNst1K9oeDY4KpWZ7v8V2BZNVa4Wdky8DvDyXvDZXvE9jTQwom", MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address("4JCp7q5SchvMCHVKENnPpM7tRcL5oWMgpMCqQDbhH8UrjDFg2H9i5AQWXuU1qacJgUUCVLTsgDmZKXGz1vPLXY8QFySJXARQWju8AuRN2z", MoneroNetworkType.MAINNET)

        # test mainnet subaddress validation
        MoneroUtils.validate_address("891TQPrWshJVpnBR4ZMhHiHpLx1PUnMqa3ccV5TJFBbqcJa3DWhjBh2QByCv3Su7WDPTGMHmCKkiVFN2fyGJKwbM1t6G7Ea", MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address("88fyq3t8Gxn1QWMG189EufHtMHXZXkfJtJKFJXqeA4GpSiuyfjVwVyp47PeQJnD7Tc8iK8TDvvhcmEmfh8nx7Va2ToP8wAo", MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address("88hnoBiX3TPjbFaQE8RxgyBcf3DtMKZWWQMoArBjQfn37JJwtm568mPX6ipcCuGKDnLCzgjmpLSqce4aBDyapJJAFtNxUMb", MoneroNetworkType.MAINNET)

        # test testnet primary address validation
        MoneroUtils.validate_address("9tUBnNCkC3UKGygHCwYvAB1FscpjUuq5e9MYJd2rXuiiTjjfVeSVjnbSG5VTnJgBgy9Y7GTLfxpZNMUwNZjGfdFr1z79eV1", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("9xZmQa1kYakGoHcfXeBgcsLf622NCpChcACwXxfdgY9uAa9hXSPCV9cLvUsAShfDcFKDdPzCNJ1n5cFGKw5GVM722pjuGPd", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("A2TXS6QFQ4wEsp8U7C2Y4B7wBtiML8aDG7mdCbRvDQmRaRNj1YSSgJE46fSzUkwgpMUCXFqscvrQuN7oKpP6eDyQ7XuYsuf", MoneroNetworkType.TESTNET)

        # test testnet integrated address validation
        MoneroUtils.validate_address("A4AroB2EoJzKGygHCwYvAB1FscpjUuq5e9MYJd2rXuiiTjjfVeSVjnbSG5VTnJgBgy9Y7GTLfxpZNMUwNZjGfdFr2QY5Ba2aHhTEdQa2ra", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("A8GSRNqF9rGGoHcfXeBgcsLf622NCpChcACwXxfdgY9uAa9hXSPCV9cLvUsAShfDcFKDdPzCNJ1n5cFGKw5GVM723iPoCEF1Fs9BcPYxTW", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("ACACSuDk1LTEsp8U7C2Y4B7wBtiML8aDG7mdCbRvDQmRaRNj1YSSgJE46fSzUkwgpMUCXFqscvrQuN7oKpP6eDyQAdgDoT3UnMYKQz7SHC", MoneroNetworkType.TESTNET)

        # test testnet subaddress validation
        MoneroUtils.validate_address("BgnKzHPJQDcg7xiP7bMN9MfPv9Z8ciT71iEMYnCdgBRBFETWgu9nKTr8fnzyGfU9h9gyNA8SFzYYzHfTS9KhqytSU943Nu1", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("BZwiuKkoNP59zgPHTxpNw3PM4DW2xiAVQJWqfFRrGyeZ7afVdQqoiJg3E2dDL3Ja8BV4ov2LEoHx9UjzF3W4ihPBSZvWwTx", MoneroNetworkType.TESTNET)
        MoneroUtils.validate_address("Bhf1DEYrentcehUvNreLK5gxosnC2VStMXNCCs163RTxQq4jxFYvpw7LrQFmrMwWW2KsXLhMRtyho6Lq11ci3Fb246bxYmi", MoneroNetworkType.TESTNET)

        # test stagenet primary address validation
        MoneroUtils.validate_address("5B8s3obCY2ETeQB3GNAGPK2zRGen5UeW1WzegSizVsmf6z5NvM2GLoN6zzk1vHyzGAAfA8pGhuYAeCFZjHAp59jRVQkunGS", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("57VfotUbSZLG82UkKhWXDjS5ZEK9ZCDcmjdk4gpVq2fbKdEgwRCFrGTLZ2MMdSHphRWJDWVBi5qS8T7dz13JTCWtC228zyn", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("52FysgWJYmAG73QUQZRULJj2Dv2C2mceUMB5zHqNzMn8WBtfPWQrSUFSQUKTX9r7bUMmVSGbrau976xYLynR8jTWLdA7rfp", MoneroNetworkType.STAGENET)

        # test stagenet integrated address validation
        MoneroUtils.validate_address("5LqY4cQh9HkTeQB3GNAGPK2zRGen5UeW1WzegSizVsmf6z5NvM2GLoN6zzk1vHyzGAAfA8pGhuYAeCFZjHAp59jRj6LZRFrjuGK8Whthg2", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("5HCLphJ63prG82UkKhWXDjS5ZEK9ZCDcmjdk4gpVq2fbKdEgwRCFrGTLZ2MMdSHphRWJDWVBi5qS8T7dz13JTCWtHETX8zcUhDjVKcynf6", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("5BxetVKoA2gG73QUQZRULJj2Dv2C2mceUMB5zHqNzMn8WBtfPWQrSUFSQUKTX9r7bUMmVSGbrau976xYLynR8jTWVwQwpHNg5fCLgtA2Dv", MoneroNetworkType.STAGENET)

        # test stagenet subaddress validation
        MoneroUtils.validate_address("778B5D2JmMh5TJVWFbygJR15dvio5Z5B24hfSrWDzeroM8j8Lqc9sMoFE6324xg2ReaAZqHJkgfGFRugRmYHugHZ4f17Gxo", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("73U97wGEH9RCVUf6bopo45jSgoqjMzz4mTUsvWs5EusmYAmFcBYFm7wKMVmgtVKCBhMQqXrcMbHvwck2md63jMZSFJxUhQ2", MoneroNetworkType.STAGENET)
        MoneroUtils.validate_address("747wPpaPKrjDPZrF48jAfz9pRRUHLMCWfYu2UanP4ZfTG8NrmYrSEWNW8gYoadU8hTiwBjV14e6DLaC5xfhyEpX5154aMm6", MoneroNetworkType.STAGENET)

        # test invalid addresses on mainnet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address("42ZxX3Y2y5s4nJ8fdz2w65TrTEp9PRsv5J8iHSShkHQcE2V31FhnWptioNst1K9oeDY4KpWZ7v8V2BZNVa4Wdky89iqmPz2", MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address("41ApvrfMgUFZEePHBZHwuSckQXebuZu299NSmVEmQ41YJZQhKcPyujyMSzpDH4VMMVSBo3U3b54JaNvQLwAjqDhKeGLQ9vfRBRKFKnBtVH", MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address("81fyq3t8Gxn1QWMG189EufHtMHXZXkfJtJKFJXqeA4GpSiuyfjVwVyp47PeQJnD7Tc8iK8TDvvhcmEmfh8nx7Va2ToP8wAo", MoneroNetworkType.MAINNET)

        # test invalid addresses on testnet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address("91UBnNCkC3UKGygHCwYvAB1FscpjUuq5e9MYJd2rXuiiTjjfVeSVjnbSG5VTnJgBgy9Y7GTLfxpZNMUwNZjGfdFr1z79eV1", MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address("A1AroB2EoJzKGygHCwYvAB1FscpjUuq5e9MYJd2rXuiiTjjfVeSVjnbSG5VTnJgBgy9Y7GTLfxpZNMUwNZjGfdFr2QY5Ba2aHhTEdQa2ra", MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address("B1nKzHPJQDcg7xiP7bMN9MfPv9Z8ciT71iEMYnCdgBRBFETWgu9nKTr8fnzyGfU9h9gyNA8SFzYYzHfTS9KhqytSU943Nu1", MoneroNetworkType.TESTNET)

        # test invalid addresses on stagenet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address("518s3obCY2ETeQB3GNAGPK2zRGen5UeW1WzegSizVsmf6z5NvM2GLoN6zzk1vHyzGAAfA8pGhuYAeCFZjHAp59jRVQkunGS", MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address("51qY4cQh9HkTeQB3GNAGPK2zRGen5UeW1WzegSizVsmf6z5NvM2GLoN6zzk1vHyzGAAfA8pGhuYAeCFZjHAp59jRj6LZRFrjuGK8Whthg2", MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address("718B5D2JmMh5TJVWFbygJR15dvio5Z5B24hfSrWDzeroM8j8Lqc9sMoFE6324xg2ReaAZqHJkgfGFRugRmYHugHZ4f17Gxo", MoneroNetworkType.STAGENET)

    # Can validate keys
    def test_key_validation(self):

        # test private view key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_private_view_key("86cf351d10894769feba29b9e201e12fb100b85bb52fc5825c864eef55c5840d"))
        MoneroTestUtils.test_invalid_public_view_key("")
        MoneroTestUtils.test_invalid_private_view_key(None)
        MoneroTestUtils.test_invalid_private_view_key("5B8s3obCY2ETeQB3GNAGPK2zRGen5UeW1WzegSizVsmf6z5NvM2GLoN6zzk1vHyzGAAfA8pGhuYAeCFZjHAp59jRVQkunGS")

        # test public view key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_public_view_key("99873d76ca874ff1aad676b835dd303abcb21c9911ca8a3d9130abc4544d8a0a"))
        MoneroTestUtils.test_invalid_public_view_key("")
        MoneroTestUtils.test_invalid_public_view_key(None)
        MoneroTestUtils.test_invalid_public_view_key("z86cf351d10894769feba29b9e201e12fb100b85bb52fc5825c864eef55c5840d")

        # test private spend key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_private_spend_key("e9ba887e93620ef9fafdfe0c6d3022949f1c5713cbd9ef631f18a0fb00421dee"))
        MoneroTestUtils.test_invalid_private_spend_key("")
        MoneroTestUtils.test_invalid_private_spend_key(None)
        MoneroTestUtils.test_invalid_private_spend_key("z86cf351d10894769feba29b9e201e12fb100b85bb52fc5825c864eef55c5840d")

        # test public spend key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_public_spend_key("3e48df9e9d8038dbf6f5382fac2becd8686273cda5bd87187e45dca7ec5af37b"))
        MoneroTestUtils.test_invalid_public_spend_key("")
        MoneroTestUtils.test_invalid_public_spend_key(None)
        MoneroTestUtils.test_invalid_public_spend_key("z86cf351d10894769feba29b9e201e12fb100b85bb52fc5825c864eef55c5840d")

    # Can convert between XMR and atomic units
    def test_atomic_unit_conversion(self):
        assert 1000000000000 == MoneroUtils.xmr_to_atomic_units(1)
        assert 1 == MoneroUtils.atomic_units_to_xmr(1000000000000)
        assert 1000000000 == MoneroUtils.xmr_to_atomic_units(0.001)
        assert 0.001 == MoneroUtils.atomic_units_to_xmr(1000000000)
        assert 250000000000 == MoneroUtils.xmr_to_atomic_units(0.25)
        assert 0.25 == MoneroUtils.atomic_units_to_xmr(250000000000)
        assert 1250000000000 == MoneroUtils.xmr_to_atomic_units(1.25)
        assert 1.25 == MoneroUtils.atomic_units_to_xmr(1250000000000)
        assert 2796726190000 == MoneroUtils.xmr_to_atomic_units(2.79672619)
        assert 2.79672619 == MoneroUtils.atomic_units_to_xmr(2796726190000)
        assert 2796726190001 == MoneroUtils.xmr_to_atomic_units(2.796726190001)
        assert 2.796726190001 == MoneroUtils.atomic_units_to_xmr(2796726190001)
        assert 2796726189999 == MoneroUtils.xmr_to_atomic_units(2.796726189999)
        assert 2.796726189999 == MoneroUtils.atomic_units_to_xmr(2796726189999)
        assert 2796726180000 == MoneroUtils.xmr_to_atomic_units(2.79672618)
        assert 2.79672618 == MoneroUtils.atomic_units_to_xmr(2796726180000)

    # Can get payment uri
    def test_get_payment_uri(self):
        config = MoneroTxConfig()
        config.address = "42U9v3qs5CjZEePHBZHwuSckQXebuZu299NSmVEmQ41YJZQhKcPyujyMSzpDH4VMMVSBo3U3b54JaNvQLwAjqDhKS3rvM3L"
        config.amount = 250000000000
        config.recipient_name = "John Doe"
        config.note = "My transfer to wallet"

        payment_uri = MoneroUtils.get_payment_uri(config)

        assert payment_uri == "monero:42U9v3qs5CjZEePHBZHwuSckQXebuZu299NSmVEmQ41YJZQhKcPyujyMSzpDH4VMMVSBo3U3b54JaNvQLwAjqDhKS3rvM3L?tx_amount=0.250000000000&recipient_name=John%20Doe&tx_description=My%20transfer%20to%20wallet"
