---
title: Docker Network
---
# Docker Network

The regtest network of `tests/docker-compose.yml`, which the integration tests run on.

## Start the network

```bash
./bin/setup_test_environment.sh
```

It is the same as:

```bash
docker compose -f tests/docker-compose.yml up -d node_1 node_2 xmr_wallet_1 xmr_wallet_2 xmr_wallet_3
```

To see that the containers run, and their logs:

```bash
docker compose -f tests/docker-compose.yml ps
docker compose -f tests/docker-compose.yml logs -f node_2
```

To stop them and remove the chain, so that the next run starts from a new one:

```bash
docker compose -f tests/docker-compose.yml down -v
```

`./bin/cleanup_test_environment.sh` does the same, and also removes what the tests leave in the repository: the wallets of
`test_wallets/`, the logs of `test_logs/`, the coverage (`.coverage`, `coverage.xml`, the reports and the counters of the C++),
`.pytest_cache` and the `__pycache__` folders.

### The containers

| Container | Image | What it is | Ports on the host |
| --- | --- | --- | --- |
| `node_1` | `monero-daemon-rpc` | `monerod`, the peer of `node_2`. It has no zmq | 18089 (rpc), 48080 (p2p) |
| `node_2` | `monero-daemon-rpc` | `monerod`, the daemon of the tests and of the wallet rpc servers | 18081 (rpc), 18085 (zmq rpc), 18086 (zmq pub), 18080 (p2p) |
| `xmr_wallet_1` | `monero-wallet-rpc` | a wallet rpc server on `node_2` | 18082 |
| `xmr_wallet_2` | `monero-wallet-rpc` | a wallet rpc server on `node_2` | 18083 |
| `xmr_wallet_3` | `monero-wallet-rpc` | a wallet rpc server on `node_2` | 18084 |

- The images are `ghcr.io/libmonero/monero-daemon-rpc` and `ghcr.io/libmonero/monero-wallet-rpc`, at the tag `master`. To test
  with others, set `MONERO_TAG` before starting them: `MONERO_TAG=<tag> ./bin/setup_test_environment.sh`.
- The two nodes are each other's only peer (`--add-exclusive-node`), on `--regtest` with `--fixed-difficulty=500`: a block takes
  little to mine, and the chain is the one of the tests alone.
- The rpc of the nodes asks for the login `rpc_daemon_user:abc123`, the wallet rpc servers for `rpc_user:abc123`. The wallet files
  of a server are in its volume, in `/home/monero/wallets`.
- The chain and the wallets are in docker volumes (`xmr_node_1_data`, `xmr_wallet_1_data`...): they stay when the containers stop,
  and go with `down -v`.

## How the tests use the network

Before the tests of the full and the rpc wallet, the chain is prepared, once for a chain: a chain that is 100 blocks high already,
as the one of the volumes of an earlier run, is used as it is.

1. **Height.** The chain grows to the height of 100. The blocks go to the mining wallet (`mining_wallet` in `config.ini`). On
   regtest at a low difficulty they are generated with the `generateblocks` rpc, which is faster than mining; otherwise a node mines
   them.
2. **Transactions.** The mining wallet sends a batch of transactions, and 11 blocks confirm them: the chain has transactions for the
   tests that read them.
3. **Alternative chain.** On regtest, a fork of a few blocks, so that the tests of the alternative chains have one.

Then, before the tests of each wallet type, the mining wallet sends funds to the test wallet of that type, and the tests wait for
them to unlock.

The tests that need more blocks mine or generate them as they go. The wallet of each type (full, rpc, keys-only) is the same for
all its tests and has the seed of `config.ini`: the tests of a type spend what the type before left, so the funds are sent again
when the tests of the next type start.
