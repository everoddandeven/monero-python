import logging

from abc import ABC

from monero import SerializableStruct, MoneroRpcConnection, MoneroConnectionType

logger: logging.Logger = logging.getLogger("RpcConnectionUtils")


class RpcConnectionUtils(ABC):
    """Test utils for rpc connections."""

    @classmethod
    def setup_rpc_connection(cls, connection: MoneroRpcConnection) -> None:
        """Setup and check rpc connection.

        :param MoneroRpcConnection connection: rpc connection to setup.
        """
        if connection.is_connected() is not None:
            return
        cls.test_check_rpc_connection(connection, True)

    @classmethod
    def test_check_rpc_connection(cls, connection: MoneroRpcConnection, connected: bool) -> None:
        """Test rpc connection check.

        :param MoneroRpcConnection connection: rpc connection to check.
        :param bool connected: expected rpc connection to be connected after check.
        """
        # check connection
        assert connection.check_connection()
        assert not connection.check_connection()
        assert connection.is_connected() == connected
        assert connection.is_online() == connected

        if connected:
            assert connection.response_time is not None
            assert connection.response_time > 0
            logger.debug(f"Rpc connection response time: {connection.response_time} ms")
        else:
            assert connection.response_time is None

    @classmethod
    def test_rpc_connection(
        cls,
        connection: MoneroRpcConnection | None,
        uri: str | None,
        connected: bool,
        connection_type: MoneroConnectionType | None
    ) -> None:
        """Test a monero rpc connection.

        :param MoneroRpcConnection | None connection: rpc connection to test.
        :param str | None uri: rpc uri of the connection to test.
        :param bool connected: checks if rpc is connected or not.
        :param MoneroConnectionType | None connection_type: type of rpc connection to test.
        :raises AssertionError: raises an error if rpc connection is not as expected.
        """
        # check expected values from rpc connection
        assert connection is not None
        assert isinstance(connection, SerializableStruct)
        assert isinstance(connection, MoneroRpcConnection)
        assert uri is not None
        assert len(uri) > 0
        assert connection.uri == uri

        # test check connection
        cls.test_check_rpc_connection(connection, connected)

        # test setting to readonly property
        try:
            connection.response_time = 0 # type: ignore
            raise Exception("Should have failed")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg != "Should have failed", e_msg

        # test connection type
        if connection_type == MoneroConnectionType.I2P:
            assert connection.is_i2p()
        elif connection_type == MoneroConnectionType.TOR:
            assert connection.is_onion()
        elif connection_type is not None:
            assert not connection.is_i2p()
            assert not connection.is_onion()
