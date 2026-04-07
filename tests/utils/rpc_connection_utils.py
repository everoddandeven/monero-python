from abc import ABC

from monero import MoneroRpcConnection


class RpcConnectionUtils(ABC):
    """Test utils for rpc connections."""

    @classmethod
    def test_connections_and_order(
        cls,
        ordered_connections: list[MoneroRpcConnection],
        connections: list[MoneroRpcConnection],
        check_never_connected: bool
        ) -> None:
        """
        Test rpc connections and order.

        :param list[MoneroRpcConnection] ordered_connections: list of ordered connections to test.
        :param list[MoneroRpcConnection] connections: connections to test with ordered.
        """
        assert ordered_connections[0] == connections[4]
        assert ordered_connections[1] == connections[2]
        assert ordered_connections[2] == connections[3]
        assert ordered_connections[3] == connections[0]
        connection = connections[1]
        assert connection is not None
        assert ordered_connections[4].uri == connection.uri

        if not check_never_connected:
            return

        for connection in ordered_connections:
            assert connection.is_online() is None

    @classmethod
    def test_connections_order(cls, ordered_connections: list[MoneroRpcConnection], connections: list[MoneroRpcConnection]) -> None:
        """
        Test rpc connections order.

        :param list[MoneroRpcConnection] ordered_connections: list of ordered connections to test.
        :param list[MoneroRpcConnection] connections: connections to test with ordered.
        """
        assert ordered_connections[0] == connections[4]
        assert ordered_connections[1] == connections[0]
        connection = connections[1]
        assert connection is not None
        assert ordered_connections[2].uri == connection.uri
        assert ordered_connections[3] == connections[2]
        assert ordered_connections[4] == connections[3]
