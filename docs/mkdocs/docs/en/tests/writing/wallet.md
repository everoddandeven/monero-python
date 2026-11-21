---
title: Wallet Tests
---
# Wallet Tests

A topic of the wallet has a base class with the tests that every wallet type has to pass, and a class for each type, which gets them
from the base class and from the support class of its type:

```python
class BaseTestMoneroWalletMining(BaseTestMoneroWallet):
    """Common wallet mining tests."""

    # Can start and stop mining
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        wallet.start_mining(1, False, True)
        wallet.stop_mining()


@pytest.mark.integration
class TestMoneroWalletFullMining(FullWalletSupport, BaseTestMoneroWalletMining):
    """Full wallet mining integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcMining(RpcWalletSupport, BaseTestMoneroWalletMining):
    """Rpc wallet mining integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysMining(KeysWalletSupport, BaseTestMoneroWalletMining):
    """Keys-only wallet mining unit tests."""

    @pytest.mark.not_supported
    @override
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_mining(daemon, wallet)
```

- The base class has no marker and its name does not start with `Test`: pytest does not run it, only the classes of the types.
- The support classes (`tests/wallet/wallet_support.py`) give the `wallet` fixture of their type, and what differs between the types:
  how a wallet is created, opened and closed, the seed languages.
- `BaseTestMoneroWallet` gives the `daemon` fixture, and before the tests of a full or rpc wallet it prepares the chain and funds the
  wallet ([Test Environment](../environment/network.md#how-the-tests-use-the-network)).
- A test that only one type has goes in the class of that type.

## When a wallet type does not do something

The class of the type overrides the test, calls the one of the base class, and marks it:

| Marker | When | What pytest does |
| --- | --- | --- |
| `@pytest.mark.not_supported` | the type can not do it, by design: a keys-only wallet has no daemon | the test passes only if it raises an error that says "not supported" |
| `@pytest.mark.not_implemented` | the type does not do it yet, and will | a strict xfail: it xfails while it fails, and fails once it passes, so the marker is removed with the change that implements it |

A test that checks what a type does instead goes in the class of the type, with its own name (`test_close_with_save_not_supported`).

## Conditions

The flags of `[general]` in `config.ini` ([Test Environment](../environment/configuration.md#general)) are on `TestUtils`, and the tests skip on
them:

```python
@pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
@pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
```

| Flag | For a test that |
| --- | --- |
| `TEST_NON_RELAYS` | does not send to the network |
| `TEST_RELAYS` | relays a transaction |
| `TEST_NOTIFICATIONS` | waits for the notifications of a listener |
| `TEST_RESETS` | makes a wallet read the chain again |
| `LITE_MODE` | is slow, and can be left out |
