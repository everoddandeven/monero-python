import pytest
import logging

from monero import (
    MoneroAccount, MoneroBlock, MoneroOutput, MoneroOutputWallet, MoneroRpcConnection, MoneroSubaddress, MoneroTx, MoneroTxWallet,
    MoneroWalletConfig
)

from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestSerializableStruct")


@pytest.mark.unit
class TestSerializableStruct(BaseTestClass):
    """Equality and representation of the serializable structs unit tests."""

    # Can compare structs of the same type by value
    def test_equals(self) -> None:
        subaddress1: MoneroSubaddress = self._get_subaddress()
        subaddress2: MoneroSubaddress = self._get_subaddress()
        assert subaddress1 is not subaddress2
        assert subaddress1 == subaddress2
        assert not subaddress1 != subaddress2

        subaddress2.label = "other label"
        assert subaddress1 != subaddress2

        # a struct does not equal another type
        assert MoneroOutput() != MoneroOutputWallet()
        assert MoneroTx() != MoneroTxWallet()
        assert MoneroSubaddress() != MoneroSubaddress().serialize()
        assert MoneroSubaddress() != None # noqa: E711

    # Can compare the children of the structs but not their back references
    def test_equals_children(self) -> None:
        tx1: MoneroTx = self._get_tx()
        tx2: MoneroTx = self._get_tx()
        assert tx1 == tx2

        # the outputs are compared
        tx2.outputs[0].amount = 2
        assert tx1 != tx2
        tx2.outputs[0].amount = 1
        assert tx1 == tx2

        # the block of a tx and the tx of an output are back references, like with monero-java
        block: MoneroBlock = MoneroBlock()
        block.height = 10
        block.txs = [tx1]
        tx1.block = block
        assert tx1.block is not None
        assert tx2.block is None
        assert tx1 == tx2
        assert tx1.outputs[0] == tx2.outputs[0]

        # the txs of a block are its children
        other_block: MoneroBlock = MoneroBlock()
        other_block.height = 10
        assert block != other_block
        other_block.txs = [tx2]
        assert block == other_block

    # Can compare the structs of a vector by value, like a list and like contains() and equals() of monero-java
    def test_vector_equals(self) -> None:
        tx: MoneroTx = self._get_tx()
        output: MoneroOutput = tx.outputs[0]
        copy: MoneroOutput = output.copy()
        other: MoneroOutput = output.copy()
        other.amount = 2

        # an equal struct is in the vector, which keeps the same objects
        assert output in tx.outputs
        assert copy in tx.outputs
        assert other not in tx.outputs
        assert "my tx hash" not in tx.outputs
        assert tx.outputs[0] is output
        assert tx.outputs.count(copy) == 1
        assert tx.outputs.count(other) == 0
        assert tx.outputs.index(copy) == 0
        with pytest.raises(ValueError):
            tx.outputs.index(other)

        # a vector equals a vector or a list with equal structs in the same order
        assert tx.outputs == self._get_tx().outputs
        assert tx.outputs == [copy]
        assert tx.outputs != [other]
        assert tx.outputs != [copy, copy]
        assert tx.outputs != (copy,)

        # the vectors of structs without a shared_ptr too
        account: MoneroAccount = MoneroAccount()
        account.subaddresses = [self._get_subaddress()]
        assert self._get_subaddress() in account.subaddresses
        assert account.subaddresses == [self._get_subaddress()]

        # an equal struct is removed
        with pytest.raises(ValueError):
            tx.outputs.remove(other)
        tx.outputs.remove(copy)
        assert len(tx.outputs) == 0

    # Cannot hash the structs, which are mutable
    @pytest.mark.parametrize("struct", [MoneroSubaddress(), MoneroTxWallet(), MoneroRpcConnection(), MoneroWalletConfig()])
    def test_not_hashable(self, struct: object) -> None:
        with pytest.raises(TypeError, match="unhashable type"):
            hash(struct)

    # Can represent a struct as its type with its json
    def test_repr(self) -> None:
        subaddress: MoneroSubaddress = self._get_subaddress()
        assert repr(subaddress) == f"MoneroSubaddress({subaddress.serialize()})"

        # the type is the one of the struct, not the one of the binding that returns it
        tx: MoneroTx = self._get_tx()
        assert repr(tx.outputs[0]).startswith("MoneroOutputWallet(")

    # Can compare the config of the connections and not their state
    def test_connection_equals(self) -> None:
        connection1: MoneroRpcConnection = MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123", "socks5://127.0.0.1:9050")
        connection2: MoneroRpcConnection = MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123", "socks5://127.0.0.1:9050")
        assert connection1 == connection2

        # the priority and the timeout are not compared, like with monero-java
        connection2.priority = 1
        connection2.timeout_ms = 1000
        assert connection1 == connection2

        # the uri, the credentials, the proxy, the zmq uri and the ssl verify are
        for connection in (
            MoneroRpcConnection("http://localhost:28082", "rpc_user", "abc123", "socks5://127.0.0.1:9050"),
            MoneroRpcConnection("http://localhost:28081", "other_user", "abc123", "socks5://127.0.0.1:9050"),
            MoneroRpcConnection("http://localhost:28081", "rpc_user", "other_password", "socks5://127.0.0.1:9050"),
            MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123"),
            MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123", "socks5://127.0.0.1:9050", "tcp://127.0.0.1:18083"),
        ):
            assert connection1 != connection
        connection2.ssl_verify = not connection1.ssl_verify
        assert connection1 != connection2

        # a copy equals the connection
        assert MoneroRpcConnection(connection1) == connection1
        assert connection1 != connection1.uri

    # Cannot see the password of a connection in its representation
    def test_connection_repr(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123")
        representation: str = repr(connection)
        assert representation.startswith("MoneroRpcConnection(")
        assert "http://localhost:28081" in representation
        assert "rpc_user" in representation
        assert "abc123" not in representation
        assert '"password":"***"' in representation
        assert "abc123" in connection.serialize()

        # a connection without password has none to hide
        assert "***" not in repr(MoneroRpcConnection("http://localhost:28081"))

    # Cannot see the secrets of a wallet config in its representation
    def test_wallet_config_repr(self) -> None:
        secrets: list[str] = ["supersecretpassword123", "my seed words", "my seed offset", "my private view key", "my private spend key"]
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = "wallets/main"
        config.primary_address = "my primary address"
        config.password, config.seed, config.seed_offset, config.private_view_key, config.private_spend_key = secrets
        representation: str = repr(config)
        assert representation.startswith("MoneroWalletConfig(")
        assert "wallets/main" in representation
        assert "my primary address" in representation
        for secret in secrets:
            assert secret not in representation
            assert secret in config.serialize()
        assert representation.count('"***"') == len(secrets)

        # the password of its server too
        config.server = MoneroRpcConnection("http://localhost:28081", "rpc_user", "abc123")
        representation = repr(config)
        assert "rpc_user" in representation
        assert "abc123" not in representation
        assert representation.count('"***"') == len(secrets) + 1

        # the config is compared with its secrets
        other: MoneroWalletConfig = config.copy()
        assert other == config
        other.seed = "other seed words"
        assert other != config

    #region Utils

    @classmethod
    def _get_subaddress(cls) -> MoneroSubaddress:
        subaddress: MoneroSubaddress = MoneroSubaddress()
        subaddress.account_index = 0
        subaddress.index = 1
        subaddress.address = "my address"
        subaddress.label = "my label"
        subaddress.balance = 100
        subaddress.is_used = True
        return subaddress

    @classmethod
    def _get_tx(cls) -> MoneroTx:
        tx: MoneroTx = MoneroTxWallet()
        tx.hash = "my tx hash"
        tx.fee = 10
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        output.account_index = 0
        output.tx = tx
        tx.outputs = [output]
        return tx

    #endregion
