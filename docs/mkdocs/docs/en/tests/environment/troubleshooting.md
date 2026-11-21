---
title: Troubleshooting
---
# Troubleshooting

What can go wrong when running the tests, and what to do.

| What happens | Why, and what to do |
| --- | --- |
| `ModuleNotFoundError: No module named 'monero'` | the module is not in the path: `export PYTHONPATH="$PWD/build"`, or `pip install .` |
| the integration tests fail to connect | the containers do not run: `docker compose -f tests/docker-compose.yml ps`, and `logs` for the reason |
| `Daemon is busy` | the daemon is still syncing or processing: pytest runs the test again, up to 5 times. If it lasts, the node is stuck: restart the network |
| the first test waits for minutes | it is preparing the chain and funding the wallets, the log says at which height it is |
| the wallets of a run see the funds of an earlier one | the chain of the volumes is the old one: `down -v`, then start the network again |
| a test of `test_proofs.py` or `test_txs.py` says "run send tests" | it looks for the transactions that the send tests make: run it with `test_send.py` of the same wallet type ([Running the Tests](../running/selecting.md#the-order-of-the-wallet-tests)) |
