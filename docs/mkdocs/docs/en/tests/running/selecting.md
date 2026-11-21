---
title: Choosing the Tests
---
# Choosing the Tests

pytest runs what the command names: markers, paths, node ids and names.

## By marker

Every test is `unit` or `integration`. A marker expression combines them with `and`, `or` and `not`:

```bash
pytest -m unit
pytest -m "integration and not not_supported"
pytest -m not_implemented                   # the tests of what is not implemented yet
```

## By file, class or test

A test is named by its node id, the path of its file, its class and its name, joined by `::`:

```bash
pytest tests/wallet/test_sweep.py                                            # a file: one topic, every wallet type
pytest tests/wallet/test_sweep.py::TestMoneroWalletRpcSweep                  # a class: one topic, one wallet type
pytest tests/wallet/test_sweep.py::TestMoneroWalletRpcSweep::test_sweep_dust # one test
pytest tests/daemon/rpc                                                      # a folder
pytest tests/wallet/model tests/daemon/model                                 # several
```

A test of a parametrized function has its parameters in its id, between brackets:

```bash
pytest "tests/wallet/test_support.py::TestMoneroWalletSupport::test_support[sync]"
pytest "tests/wallet/test_interface.py::TestMoneroWalletInterface::test_call[get_balance()]"
```

## By name

`-k` takes an expression on the names of the files, of the classes and of the tests:

```bash
pytest tests/wallet -k Rpc                      # the rpc wallet, in every topic
pytest tests/wallet -k "Full and not Sync"      # the full wallet, without the sync tests
pytest -k "payment_uri or integrated_address"   # the tests of a feature, everywhere
pytest tests/daemon -k "deserialize"            # the deserialization of the daemon models
```

## Listing them first

To see what a selection runs, without running it:

```bash
pytest --collect-only -q -m unit tests/wallet
pytest --co -q -k Keys tests/wallet | tail -1    # just the number
```

## The order of the wallet tests

`tests/wallet/conftest.py` sorts the tests of `tests/wallet` (not the ones of `tests/wallet/model`): all the tests of the full wallet,
then the ones of the rpc wallet, then the keys-only ones, and inside each type the tests of `test_send.py` first. The wallet of a type
is the same for all its tests, and some of them use what the ones before made in it: the tests of the proofs and of the payment ids
look for the transactions that the send tests sent, and fail with "run send tests" without them.

To run one of those alone, run the send tests of the same type with it, in any order of the command:

```bash
pytest tests/wallet/test_proofs.py tests/wallet/test_send.py -k Rpc
```
