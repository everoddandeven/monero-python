from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonRpc, MoneroDestination, MoneroMultisigInitResult, MoneroMultisigSignResult,
    MoneroOutputQuery, MoneroOutputWallet, MoneroTxConfig, MoneroTxQuery, MoneroTxSet, MoneroTxWallet,
    MoneroUtils, MoneroWallet, MoneroWalletConfig
)
from typing_extensions import override

from utils import GenUtils, MiningUtils, TestUtils, TestUtils as Utils, TxWalletUtils, WalletUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletMultisig")


class BaseTestMoneroWalletMultisig(BaseTestMoneroWallet):
    """Common wallet multisig tests."""

    MULTISIG_CONFIGS: list[tuple[int, int]] = [
        (2, 2),  # n/n
        (2, 3),  # (n-1)/n
        (2, 4),  # m/n
    ]
    """The multisig wallets that `test_multisig` makes, as (threshold, number of participants)."""

    # Can indicate if multisig import is needed for correct balance information
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        # TODO test with multisig wallet
        multisig_import_needed: bool = wallet.is_multisig_import_needed()
        assert multisig_import_needed is False, "Expected non-multisig wallet"

    # Supports multisig wallets
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_multisig(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        for m, n in self.MULTISIG_CONFIGS:
            self._test_multisig(daemon, wallet, m, n)

    #region Multisig

    def _test_multisig(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet, m: int, n: int) -> None:
        """Make a m/n multisig wallet, fund it from the test wallet and spend its funds.

        :param MoneroDaemonRpc daemon: daemon of the test network.
        :param MoneroWallet wallet: test wallet, that funds the multisig wallet and gets the funds back.
        :param int m: multisig threshold.
        :param int n: number of participants.
        """
        # create n participants
        participants: list[MoneroWallet] = []
        try:
            for _ in range(n):
                participants.append(self._create_wallet(MoneroWalletConfig()))

            # test multisig
            self._test_multisig_participants(daemon, wallet, participants, m, n)
        finally:
            # stop mining at end of test
            self._stop_mining()

            # save and close participants
            for participant in participants:
                self._close_wallet(participant, True)

    def _test_multisig_participants(
        self, daemon: MoneroDaemonRpc, wallet: MoneroWallet, participants: list[MoneroWallet], m: int, n: int
    ) -> None:
        """Make the participants a m/n multisig wallet, fund it and spend its funds with a send, a sweep of an output and a sweep.

        :param MoneroDaemonRpc daemon: daemon of the test network.
        :param MoneroWallet wallet: test wallet, that funds the multisig wallet and gets the funds back.
        :param list[MoneroWallet] participants: participants of the multisig wallet.
        :param int m: multisig threshold.
        :param int n: number of participants.
        """
        logger.info(f"test_multisig_participants({m}, {n})")
        assert len(participants) == n

        # init and fund multisig wallets
        account_idx: int = 0
        self._init_multisig_wallets(daemon, wallet, participants, m, n, account_idx, 3)
        participant: MoneroWallet = participants[0]

        # create txs to send funds from a subaddress in the multisig wallet
        logger.info("Sending")
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = wallet.get_address(account_idx, 0)
        config.amount = TxWalletUtils.MAX_FEE
        config.account_index = account_idx
        config.subaddress_indices = [0]
        txs: list[MoneroTxWallet] = participant.create_txs(config)
        assert len(txs) > 0
        tx_set: MoneroTxSet | None = txs[0].tx_set
        assert tx_set is not None
        self._test_multisig_tx_set(tx_set)

        # parse multisig tx hex and test
        assert tx_set.multisig_tx_hex is not None
        TxWalletUtils.test_described_tx_set(participant.describe_multisig_tx_set(tx_set.multisig_tx_hex), Utils.NETWORK_TYPE)

        # sign the tx with participants 1 through m - 1 to meet threshold, and submit it to the network
        logger.info("Signing")
        tx_hashes: list[str] = self._sign_and_submit(participants, m, tx_set.multisig_tx_hex)
        assert len(tx_hashes) > 0

        # synchronize the multisig participants since spending outputs
        logger.info("Synchronizing participants")
        self._synchronize_multisig_participants(participants)

        # fetch the wallet's multisig txs
        self._test_multisig_txs(participant, tx_hashes)

        # sweep an output from subaddress [account_idx, 1]
        return_address: str = wallet.get_primary_address()
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.account_index = account_idx
        output_query.subaddress_index = 1
        outputs: list[MoneroOutputWallet] = participant.get_outputs(output_query)
        assert len(outputs) > 0
        assert outputs[0].is_spent is False
        assert outputs[0].key_image is not None
        sweep_config: MoneroTxConfig = MoneroTxConfig()
        sweep_config.address = return_address
        sweep_config.key_image = outputs[0].key_image.hex
        sweep_config.relay = True
        tx_set = participant.sweep_output(sweep_config).tx_set
        assert tx_set is not None
        self._test_multisig_tx_set(tx_set)
        assert len(tx_set.txs) > 0

        # parse multisig tx hex and test
        assert tx_set.multisig_tx_hex is not None
        TxWalletUtils.test_described_tx_set(participant.describe_multisig_tx_set(tx_set.multisig_tx_hex), Utils.NETWORK_TYPE)

        # sign the tx with participants 1 through m - 1 to meet threshold, and submit it to the network
        logger.info("Signing sweep output")
        tx_hashes = self._sign_and_submit(participants, m, tx_set.multisig_tx_hex)

        # synchronize the multisig participants since spending outputs
        logger.info("Synchronizing participants")
        self._synchronize_multisig_participants(participants)

        # fetch the wallet's multisig txs
        self._test_multisig_txs(participant, tx_hashes)

        # sweep remaining balance
        logger.info("Sweeping")
        sweep_config = MoneroTxConfig()
        sweep_config.address = return_address
        sweep_config.account_index = account_idx
        sweep_config.relay = True
        # TODO: test multisig with sweep_each_subaddress which will generate multiple tx sets without synchronizing participants
        txs = participant.sweep_unlocked(sweep_config)
        assert len(txs) > 0, "No txs created on sweep_unlocked"
        tx_set = txs[0].tx_set
        assert tx_set is not None
        for tx in txs:
            assert tx.tx_set is tx_set
            assert tx in tx_set.txs
        self._test_multisig_tx_set(tx_set)

        # parse multisig tx hex and test
        TxWalletUtils.test_described_tx_set(participant.describe_tx_set(tx_set), Utils.NETWORK_TYPE)

        # sign the tx with participants 1 through m - 1 to meet threshold, and submit it to the network
        logger.info("Signing sweep")
        assert tx_set.multisig_tx_hex is not None
        tx_hashes = self._sign_and_submit(participants, m, tx_set.multisig_tx_hex)

        # synchronize the multisig participants since spending outputs
        logger.info("Synchronizing participants")
        self._synchronize_multisig_participants(participants)

        # fetch the wallet's multisig txs
        self._test_multisig_txs(participant, tx_hashes)

    def _init_multisig_wallets(
        self, daemon: MoneroDaemonRpc, wallet: MoneroWallet, participants: list[MoneroWallet], m: int, n: int,
        account_idx: int, num_addresses_to_fund: int
    ) -> None:
        """Make the participants a m/n multisig wallet and fund subaddresses of its account from the test wallet.

        The first participant is restored from the multisig seed, and replaced in `participants`.

        :param MoneroDaemonRpc daemon: daemon of the test network.
        :param MoneroWallet wallet: test wallet, that funds the multisig wallet.
        :param list[MoneroWallet] participants: participants of the multisig wallet.
        :param int m: multisig threshold.
        :param int n: number of participants.
        :param int account_idx: account of the multisig wallet to fund.
        :param int num_addresses_to_fund: number of subaddresses of the account to fund (0 to fund nothing).
        """
        logger.info(f"init_multisig_wallets({m}, {n})")
        assert len(participants) == n

        # prepare multisig hexes
        prepared_multisig_hexes: list[str] = [participant.prepare_multisig() for participant in participants]

        # make wallets multisig
        made_multisig_hexes: list[str] = []
        for i, participant in enumerate(participants):

            # test bad input
            with pytest.raises(Exception) as exc_info:
                participant.make_multisig(["asd", "dsa"], m, Utils.WALLET_PASSWORD)
            if str(exc_info.value) != "Kex message unexpectedly small.":
                logger.warning(f"Unexpected error message: {exc_info.value}")

            # collect prepared multisig hexes from wallet's peers and make the wallet multisig
            peer_multisig_hexes: list[str] = [peer_hex for j, peer_hex in enumerate(prepared_multisig_hexes) if j != i]
            made_multisig_hexes.append(participant.make_multisig(peer_multisig_hexes, m, Utils.WALLET_PASSWORD))

        # try to get seed before wallet initialized
        with pytest.raises(Exception) as seed_exc_info:
            participants[0].get_seed()
        assert str(seed_exc_info.value) == "This wallet is multisig, but not yet finalized"

        # exchange keys N - M + 1 times
        address: str | None = None
        assert len(made_multisig_hexes) == n
        prev_multisig_hexes: list[str] = made_multisig_hexes
        for i in range(n - m + 1):

            # exchange multisig keys with each wallet and collect results
            exchange_multisig_hexes: list[str] = []
            for j, participant in enumerate(participants):

                # test bad input
                with pytest.raises(Exception) as exc_info:
                    participant.exchange_multisig_keys(["asd", "dsa"], Utils.WALLET_PASSWORD)
                assert len(str(exc_info.value)) > 0

                # import the multisig hexes of the wallet's peers from last round
                peer_multisig_hexes = [peer_hex for k, peer_hex in enumerate(prev_multisig_hexes) if k != j]
                result: MoneroMultisigInitResult = participant.exchange_multisig_keys(peer_multisig_hexes, Utils.WALLET_PASSWORD)

                # test result
                assert result.multisig_hex is not None
                assert len(result.multisig_hex) > 0
                if i == n - m:  # result on last round has address
                    assert result.address is not None
                    assert len(result.address) > 0
                    if address is None:
                        address = result.address
                    else:
                        assert address == result.address
                else:
                    assert result.address is None
                    exchange_multisig_hexes.append(result.multisig_hex)

            # use results for next round of exchange
            prev_multisig_hexes = exchange_multisig_hexes

        # validate final multisig
        participant: MoneroWallet = participants[0]
        MoneroUtils.validate_address(participant.get_primary_address(), Utils.NETWORK_TYPE)
        WalletUtils.test_multisig_info(participant.get_multisig_info(), m, n)
        seed: str = participant.get_seed()
        assert len(seed) > 0

        # restore participant from multisig seed
        self._close_wallet(participant)
        restore_config: MoneroWalletConfig = MoneroWalletConfig()
        restore_config.restore_height = daemon.get_height()
        restore_config.seed = seed
        restore_config.is_multisig = True
        participant = self._create_wallet(restore_config)
        participants[0] = participant
        MoneroUtils.validate_address(participant.get_primary_address(), Utils.NETWORK_TYPE)
        assert address == participant.get_primary_address()
        WalletUtils.test_multisig_info(participant.get_multisig_info(), m, n)
        assert seed == participant.get_seed()

        # test sending a multisig transaction if configured
        if num_addresses_to_fund == 0:
            return

        # create accounts in the first multisig wallet to receive funds
        for _ in range(account_idx):
            participant.create_account()

        # get destinations to subaddresses within the account of the multisig wallet
        destinations: list[MoneroDestination] = []
        for i in range(num_addresses_to_fund):
            destinations.append(MoneroDestination(participant.get_address(account_idx, i), MoneroUtils.xmr_to_atomic_units(2)))
            if i + 1 < num_addresses_to_fund:
                participant.create_subaddress(account_idx)

        # wait for txs to confirm and for sufficient unlocked balance
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        Utils.WALLET_TX_TRACKER.wait_for_unlocked_balance(wallet, 0, None, TxWalletUtils.MAX_FEE * 20)

        # send funds from the main test wallet to destinations in the first multisig wallet
        assert wallet.get_balance() > 0
        logger.info("Sending funds from main wallet")
        fund_config: MoneroTxConfig = MoneroTxConfig()
        fund_config.account_index = 0
        fund_config.destinations = destinations
        fund_config.relay = True
        wallet.create_tx(fund_config)

        # start mining
        logger.info("Starting mining")
        if not MiningUtils.is_mining():
            MiningUtils.start_mining()

        # wait for the multisig wallet's funds to unlock
        # TODO: replace with MoneroWalletListener.on_output_received() which is called when output unlocked
        last_num_confirmations: int | None = None
        while True:

            # wait a moment
            GenUtils.wait_for(Utils.SYNC_PERIOD_IN_MS)

            # fetch and test outputs
            outputs: list[MoneroOutputWallet] = participant.get_outputs()
            if len(outputs) == 0:
                logger.info("No outputs reported yet")
                continue

            # print num confirmations
            output_tx = outputs[0].tx
            assert output_tx is not None
            output_height: int | None = output_tx.get_height()
            assert output_height is not None
            num_confirmations: int = daemon.get_height() - output_height
            if last_num_confirmations != num_confirmations:
                logger.info(f"Output has {num_confirmations} confirmations")
            last_num_confirmations = num_confirmations

            # outputs are not spent
            for output in outputs:
                assert output.is_spent is False

            # break if output is unlocked
            if output_tx.is_locked is False:
                break

        # stop mining
        self._stop_mining()

        # multisig wallet should have unlocked balance in subaddresses 0-3
        for i in range(num_addresses_to_fund):
            assert participant.get_unlocked_balance(account_idx, i) > 0
        account_query: MoneroOutputQuery = MoneroOutputQuery()
        account_query.account_index = account_idx
        outputs = participant.get_outputs(account_query)
        assert len(outputs) > 0
        if len(outputs) < 3:
            logger.warning("Not one output per subaddress?")
        for output in outputs:
            assert output.tx is not None
            assert output.tx.is_locked is False

        # wallet requires importing multisig to be reliable
        assert participant.is_multisig_import_needed()

        # attempt creating and relaying transaction without synchronizing with participants
        return_address: str = wallet.get_primary_address()  # funds will be returned to this address from the multisig wallet
        unsynced_config: MoneroTxConfig = MoneroTxConfig()
        unsynced_config.account_index = account_idx
        unsynced_config.address = return_address
        unsynced_config.amount = TxWalletUtils.MAX_FEE * 3
        with pytest.raises(Exception) as exc_info:
            participant.create_txs(unsynced_config)
        assert str(exc_info.value) == "No transaction created"

        # synchronize the multisig participants since receiving outputs
        logger.info("Synchronizing participants")
        self._synchronize_multisig_participants(participants)

        # expect error exporting key images
        try:
            participant.export_key_images(True)
        except Exception as e:
            assert "key_image generated not matched with cached key image" in str(e), f"Unexpected error: {e}"

        # attempt relaying created transactions without co-signing
        relay_config: MoneroTxConfig = MoneroTxConfig()
        relay_config.address = return_address
        relay_config.amount = TxWalletUtils.MAX_FEE
        relay_config.account_index = account_idx
        relay_config.subaddress_indices = [0]
        relay_config.relay = True
        with pytest.raises(Exception) as exc_info:
            participant.create_tx(relay_config)
        assert str(exc_info.value) == "Cannot relay multisig transaction until co-signed"

    @staticmethod
    def _sign_and_submit(participants: list[MoneroWallet], m: int, multisig_tx_hex: str) -> list[str]:
        """Sign the multisig tx hex with participants 1 through m - 1 to meet the threshold, then submit it with the first one.

        :param list[MoneroWallet] participants: participants of the multisig wallet.
        :param int m: multisig threshold.
        :param str multisig_tx_hex: multisig tx hex to sign.
        :returns list[str]: hashes of the submitted txs.
        """
        for i in range(1, m):
            result: MoneroMultisigSignResult = participants[i].sign_multisig_tx_hex(multisig_tx_hex)
            assert result.signed_multisig_tx_hex is not None
            multisig_tx_hex = result.signed_multisig_tx_hex

        # submit the signed multisig tx hex to the network
        logger.info("Submitting")
        return participants[0].submit_multisig_tx_hex(multisig_tx_hex)

    @staticmethod
    def _synchronize_multisig_participants(wallets: list[MoneroWallet]) -> None:
        """Synchronize the multisig participants: each one imports the multisig hex of its peers.

        :param list[MoneroWallet] wallets: participants of the multisig wallet.
        """
        # collect multisig hex of all participants to synchronize
        multisig_hexes: list[str] = []
        for wallet in wallets:
            wallet.sync()
            multisig_hexes.append(wallet.export_multisig_hex())  # TODO: does wallet need saved?

        # import each wallet's peer multisig hex
        for i, wallet in enumerate(wallets):
            peer_multisig_hexes: list[str] = [peer_hex for j, peer_hex in enumerate(multisig_hexes) if j != i]
            # TODO monero-project: creating multisig tx fails if wallet not explicitly synced before import_multisig_hex:
            # https://github.com/monero-project/monero/issues/6850
            wallet.sync()
            wallet.import_multisig_hex(peer_multisig_hexes)

    @staticmethod
    def _test_multisig_tx_set(tx_set: MoneroTxSet) -> None:
        """Test that a tx set created by a multisig wallet has only the multisig tx hex."""
        assert tx_set.multisig_tx_hex is not None
        assert tx_set.signed_tx_hex is None
        assert tx_set.unsigned_tx_hex is None

    @staticmethod
    def _test_multisig_txs(participant: MoneroWallet, tx_hashes: list[str]) -> None:
        """Test that the multisig wallet has the submitted txs."""
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hashes = tx_hashes
        assert len(participant.get_txs(tx_query)) == len(tx_hashes)

    @staticmethod
    def _stop_mining() -> None:
        """Stop mining, if the daemon is mining."""
        if MiningUtils.is_mining():
            MiningUtils.stop_mining()

    #endregion


@pytest.mark.integration
class TestMoneroWalletFullMultisig(FullWalletSupport, BaseTestMoneroWalletMultisig):
    """Full wallet multisig integration tests."""

    # Supports multisig sample code
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_multisig_sample(self) -> None:
        self._test_multisig_sample(1, 2)
        self._test_multisig_sample(1, 4)
        self._test_multisig_sample(2, 2)
        self._test_multisig_sample(2, 3)
        self._test_multisig_sample(2, 4)


@pytest.mark.integration
class TestMoneroWalletRpcMultisig(RpcWalletSupport, BaseTestMoneroWalletMultisig):
    """Rpc wallet multisig integration tests."""

    # each participant is a wallet open in a monero-wallet-rpc container, and the tests have only DockerWalletRpcManager.MAX_SLOTS of
    # them: monero-java starts a process for each one, and makes also 2/3 and 2/4 multisig wallets
    MULTISIG_CONFIGS: list[tuple[int, int]] = [(2, 2)]

    # Supports multisig sample code
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_multisig_sample(self) -> None:
        self._test_multisig_sample(1, 2)
        self._test_multisig_sample(2, 2)


@pytest.mark.unit
class TestMoneroWalletKeysMultisig(KeysWalletSupport, BaseTestMoneroWalletMultisig):
    """Keys-only wallet multisig unit tests."""

    @pytest.mark.not_supported
    @override
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        return super().test_is_multisig_needed(wallet)

    @pytest.mark.not_supported
    @override
    def test_multisig(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_multisig(daemon, wallet)
