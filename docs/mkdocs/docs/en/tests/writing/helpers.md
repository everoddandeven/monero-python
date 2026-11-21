---
title: Helpers
---
# Helpers

`tests/utils` has the helpers of the tests, imported as `from utils import ...`. The main ones:

| Helper | What it gives |
| --- | --- |
| `TestUtils` | the configuration of `config.ini`, and the daemon and the wallets of the tests: `get_daemon_rpc()`, `get_wallet_full()`, `get_wallet_rpc()`, `get_wallet_keys()`, `get_wallet_full_offline()` |
| `IntegrationTestUtils` | prepares the chain and funds a wallet type, before the tests of the type |
| `BlockchainUtils`, `MiningUtils` | the height of the chain, generating and mining blocks, waiting for them |
| `WalletUtils`, `DaemonUtils`, `TxUtils`, `TransferUtils`, `OutputUtils`, `BlockUtils` | the checks of the models that the calls return |
| `AssertUtils`, `GenUtils`, `StringUtils` | assertions, waits, random strings |
| `WalletTxTracker` | waits for the transactions of the wallets to leave the pool, before the next one |
| `SingleTxSender`, `ToMultipleTxSender`, `FromMultipleTxSender`, `WalletSweeper` | send or sweep funds in a test, and check the result |
| `WalletNotificationsTester`, `WalletSyncTester`, `SyncSeedTester`, `MultisigSampleCodeTester`... | the scenarios that several tests share |
| `FakeDaemonRpcServer`, `FakeWalletRpcServer` | local rpc servers that answer with a new block or height at each request: the unit tests of the listeners and of the tx tracker run on them, with no network |
| `WalletCall`, `WALLET_CALLS` | a call of each method of the wallet interface |

The data of a test (addresses, keys, seeds) goes in `tests/config`, in an `.ini` of its own or in the one of its topic.
