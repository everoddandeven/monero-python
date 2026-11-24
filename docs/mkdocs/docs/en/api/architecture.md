---
title: Architecture
---
# Architecture

monero-python is a Python binding of [monero-cpp](https://github.com/woodser/monero-cpp){ target="_blank" rel="noopener" }, which is
built on [monero-project](https://github.com/monero-project/monero){ target="_blank" rel="noopener" }: a call of Python goes through the
binding to the C++ of monero-cpp, and from there to the wallet of monero, `wallet2`, or to the RPC of a daemon or of a wallet server.

<p align="center">
    <img width="100%" height="auto" src="../../images/architecture.png" alt="The architecture of monero-python: a Python application uses the wallets, the daemon client, the utilities and the RPC connection of the library, which are Python bindings of the same classes of monero-cpp, which talks to monero-wallet-rpc and monerod over HTTP(S) and runs wallet2 of monero-project in the process"/><br>
</p>

## The layers

| Layer | Where | What it is |
| --- | --- | --- |
| Python | your application | `from monero import ...`: the classes of the diagram, with the types of the stubs |
| The module `monero` | `src/cpp` | one compiled module (`monero.cpython-*.so`, `.pyd` on Windows), made with [pybind11](https://pybind11.readthedocs.io){ target="_blank" rel="noopener" }: it binds the classes of monero-cpp, and has no Python code of its own |
| The stubs | `src/monero/*.pyi` | the types and the docstrings of every class and function, installed next to the module with `py.typed`: type checkers and editors read them, and the [API Reference](wallet.md) is made from them |
| monero-cpp | `external/monero-cpp` | the data model and the interfaces of the daemon and of the wallet, with their implementations, in C++ |
| monero-project | `external/monero-cpp/external/monero-project` | `wallet2`, the wallet of monero, and the code that `monerod` and `monero-wallet-rpc` are made of |

monero-cpp and monero-project are linked into the module: an application needs no library of monero installed, only a daemon to talk
to, or a wallet server for the RPC wallet.

## The daemon and the wallets

The daemon has one implementation, the wallet has three. Each wallet implements the same interface, [`MoneroWallet`][monero.MoneroWallet],
and code written for it works with any of them, within what each one supports ([Wallet Support](wallet_support.md)).

| Class | What it is made on | What it needs |
| --- | --- | --- |
| [`MoneroDaemonRpc`][monero.MoneroDaemonRpc] | a client of the RPC of `monerod`, over HTTP(S) | a daemon |
| [`MoneroWalletFull`][monero.MoneroWalletFull] | `wallet2` in the process: a wallet file on disk, which syncs with a daemon | a daemon to sync with |
| [`MoneroWalletRpc`][monero.MoneroWalletRpc] | a client of `monero-wallet-rpc`, over HTTP(S): the wallet files are on the server | a wallet server, connected to a daemon |
| [`MoneroWalletKeys`][monero.MoneroWalletKeys] | the keys of a wallet alone, in memory: seed, keys, addresses | nothing, it works offline |

The connection to a server is a [`MoneroRpcConnection`][monero.MoneroRpcConnection]: its URI, its credentials, a proxy, and the time to
wait for an answer.

## The data model

The model is the one of monero-cpp and monero-java, with the names of Python. Its classes have the fields of what they model, which are
`None` while they are not known, or not returned by the server: a transaction of the pool has no block. That is why their types are
`X | None`.

- The objects are linked both ways: a block has its transactions and a transaction its block, a transaction has its outputs and an output
  its transaction.
- A wallet has more fields than the daemon on the same objects: [`MoneroTxWallet`][monero.MoneroTxWallet] extends
  [`MoneroTx`][monero.MoneroTx] with its transfers and its outputs of the wallet.
- A query is the type that it selects, with the fields to match: [`MoneroTxQuery`][monero.MoneroTxQuery] extends
  [`MoneroTxWallet`][monero.MoneroTxWallet], [`MoneroTransferQuery`][monero.MoneroTransferQuery] extends
  [`MoneroTransfer`][monero.MoneroTransfer], [`MoneroOutputQuery`][monero.MoneroOutputQuery] extends
  [`MoneroOutputWallet`][monero.MoneroOutputWallet].
- The classes of the model extend [`SerializableStruct`][monero.SerializableStruct], whose `serialize()` turns them into JSON.
- Two objects of the model are equal if they hold the same values, and the same object only with `is`
  ([Equality and Identity](equality.md)).

## Listeners

[`MoneroWalletListener`][monero.MoneroWalletListener] and [`MoneroDaemonListener`][monero.MoneroDaemonListener] are classes to extend
in Python: the binding calls the methods of the subclass from C++, as the methods of any other listener.

A wallet or a daemon can call its listeners from a thread of its own, the one that syncs the wallet in the background or polls the
daemon, and not from the thread that added them: a listener that changes the state of the application has to be safe to call from
another thread ([Listening to a Wallet](../examples/basics/listening_to_a_wallet.md)).

## Threads and the GIL

The methods of the daemon and of the wallets release the GIL while they run: a sync, a request to a server, the creation of a
transaction do not stop the other threads of Python. The methods of the model, which only read or set a field, keep it.

When the last reference to a wallet or to a daemon goes, the binding releases the GIL to delete it: its destructor waits for the thread
that calls the listeners, which may be waiting for the GIL in turn.

## Memory

The objects of the model are linked both ways, a block to its transactions and each transaction to its block, a transaction to its
transfers and outputs and each of them to it. In C++ these links are `shared_ptr`, which keep each other alive: a block and its
transactions are a cycle, which Python's garbage collector does not see, since it is inside the module. When the last reference of
Python to such a graph goes, its memory is not freed: about a kilobyte for each transaction, never given back.

[`MoneroUtils.free`][monero.MoneroUtils.free] breaks the links of a graph, so that it is freed when Python drops it. An application that
runs for long, and asks a wallet or a daemon for transactions, transfers or outputs again and again, frees what it got once it is done
with it:

```python
from monero import MoneroIncomingTransfer, MoneroUtils, MoneroWallet


def received(wallet: MoneroWallet) -> int:
    transfers: list[MoneroIncomingTransfer] = wallet.get_incoming_transfers()
    total = sum(transfer.amount or 0 for transfer in transfers)
    MoneroUtils.free(transfers)     # done with them: their transactions and blocks are freed too
    return total
```

`free` takes a block, a transaction, or a list of blocks, transactions, transfers or outputs, and frees the whole graph that each one is
in. After it the links are `None`: `transfer.tx`, `output.tx`, `tx.block`. The fields of each object stay, its amount, its hash. A
script that runs once and exits does not need it.

An application that frees what it gets, and still grows, can try [jemalloc](https://jemalloc.net/){ target="_blank" rel="noopener" } as
the allocator of the process, with `LD_PRELOAD=/path/to/libjemalloc.so.2` (the `libjemalloc2` package of Debian and Ubuntu): the
allocator of glibc can keep memory that the process freed.

The objects that a wallet gives to a [listener](../examples/basics/listening_to_a_wallet.md) are freed by the wallet itself, after the
listener returns: a listener copies what it needs, the hash of the transaction, the amount, and does not keep the object for later.

## Errors

| Error | Raised for |
| --- | --- |
| [`MoneroRpcError`][monero.MoneroRpcError] | an error that a server returned over RPC, with its `code` |
| [`MoneroError`][monero.MoneroError] | an error of monero-cpp or of monero: a wallet that does not support a method, an argument that is not valid, a failure of the wallet |

The binding raises `monero_rpc_error` of C++ as `MoneroRpcError`, `monero_error` as `MoneroError`, and turns the other errors of C++ of
most calls into a `MoneroError` with their message. `MoneroRpcError` is a `MoneroError`, which is a `RuntimeError`: [Errors](errors.md).

## The specification

The data model and the interfaces are described, with diagrams, in the
[data model and API specification](https://github.com/libmonero/monero-python/blob/main/docs/monero-spec.pdf){ target="_blank" rel="noopener" }
(PDF, 21 pages): the methods of the daemon and of the wallet, and the fields of every type, with the names and the types of Python. It is
the specification of monero-cpp and monero-java, for this library.

The sources of the diagrams, `docs/architecture.drawio` and `docs/monero-spec.drawio`, are in the repository: they open in
[diagrams.net](https://app.diagrams.net){ target="_blank" rel="noopener" }, and their exports are `docs/architecture.png` and
`docs/monero-spec.pdf`.
