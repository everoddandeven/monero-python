from abc import ABC


class WalletErrorUtils(ABC):

    CREATED_WALLET_KEYS_ERROR: str = "Wallet created from keys is not connected to authenticated daemon"
    """Create wallet error message."""

    WALLET_IS_CLOSED_ERROR: str = "Wallet is closed"
    """Wallet is closed error message."""

    @classmethod
    def test_invalid_address_error(cls, ex: Exception, address: str | None = None) -> None:
        """Test exception is invalid address.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        err_msg: str = "Invalid address"
        if address is not None:
            err_msg = f"{err_msg}: {address}"
        assert msg == err_msg, msg

    @classmethod
    def test_invalid_tx_hash_error(cls, ex: Exception) -> None:
        """Test exception is invalid hash format.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        assert msg == "TX hash has invalid format", msg

    @classmethod
    def test_invalid_tx_key_error(cls, ex: Exception) -> None:
        """Test exception is invalid key error.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        assert msg == "Tx key has invalid format", msg

    @classmethod
    def test_invalid_signature_error(cls, ex: Exception) -> None:
        """Test exception is invalid signature error.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        assert msg == "Signature size mismatch with additional tx pubkeys", msg

    @classmethod
    def test_no_subaddress_error(cls, ex: Exception) -> None:
        """Test exception is no subaddress error.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        assert msg == "Address must not be a subaddress", msg

    @classmethod
    def test_signature_header_error(cls, ex: Exception) -> None:
        """Test exception is signature header error.

        :param Exception ex: exception to test.
        """
        msg: str = str(ex)
        assert msg == "Signature header check error", msg

    @classmethod
    def test_no_wallet_file_error(cls, error: Exception) -> None:
        """Test for `No wallet file` monero error.

        :param Exception | None error: error to test.
        """
        err_msg: str = str(error)
        assert err_msg == "No wallet file", err_msg

    @classmethod
    def test_wallet_is_closed_error(cls, error: Exception) -> None:
        """Test for `Wallet is closed` monero error.

        :param Exception | None error: error to test.
        """
        err_msg: str = str(error)
        assert err_msg == cls.WALLET_IS_CLOSED_ERROR, err_msg

    @classmethod
    def test_wallet_is_not_connected_error(cls, error: Exception) -> None:
        err_msg: str = str(error)
        # TODO normalize Network error message?
        assert err_msg == "Wallet is not connected to daemon" or err_msg == "Network error", err_msg

    @classmethod
    def test_deprecated_payment_id_error(cls, error: Exception) -> None:
        err_msg: str = str(error)
        assert err_msg == "Standalone payment id deprecated, use integrated address instead", err_msg
