---
title: Equality and Identity
---
# Equality and Identity

The objects of the [data model](architecture.md#the-data-model) are compared like in monero-java, with the operators of Python:
`==` tells whether two objects hold the same values, `is` whether they are the same object. A test ported from monero-java has to
pick the right one, since Java writes them the other way around.

## Equality

Two objects are equal if they have the same class and the same JSON, the one of [`serialize`][monero.SerializableStruct.serialize]:

```python
tx1: MoneroTxWallet = wallet.get_tx(tx_hash)
tx2: MoneroTxWallet = wallet.get_tx(tx_hash)
assert tx1 == tx2      # the same values
assert tx1 is not tx2  # two objects
```

- **The children are compared, the back references are not.** A block compares its txs and a tx its outputs, but a tx does not
  compare its block and an output its tx, as with `equals` in monero-java. Two txs with the same values in two different blocks are
  equal.
- **The class has to be the same.** A [`MoneroTx`][monero.MoneroTx] does not equal a [`MoneroTxWallet`][monero.MoneroTxWallet], and a
  [`MoneroTxQuery`][monero.MoneroTxQuery] does not equal the tx that it selects, even with the same JSON.
- **What is not serialized is not compared**, and what is serialized is: the `server` of a
  [`MoneroWalletConfig`][monero.MoneroWalletConfig] is compared by its JSON, with its priority and its state, unlike two
  [`MoneroRpcConnection`][monero.MoneroRpcConnection] on their own.

[`MoneroRpcConnection`][monero.MoneroRpcConnection] is compared as in monero-java, by uri, username, password, proxy uri, zmq uri and
ssl verify. Its JSON also has the priority, the timeout and the state of the connection (`responseTime`, `isOnline`), which are not
compared: a connection equals the one that a wallet returns for it.

## Hashing

The objects can be changed, so they are not hashable: they can not be keys of a `dict` or go in a `set`, and `hash(tx)` raises
`TypeError`. Key them by what identifies them:

```python
txs_by_hash: dict[str, MoneroTxWallet] = {tx.hash: tx for tx in txs}
```

or, to tell the objects apart rather than their values, by their `id()` while a reference keeps them alive (see below).

## Identity

An object of the model is a Python object around a C++ object. The bindings give the same Python object for the same C++ object as long
as one is alive, so the back references are the objects that they point to:

```python
for output in tx.outputs:
    assert output.tx is tx
assert tx.block is None or tx in tx.block.txs
```

When no Python object is alive, the next access makes a new one: the `id()` of a temporary object can change from an access to the
next. Keep a reference before taking it:

```python
block: MoneroBlock | None = tx.block
if block is not None and id(block) not in seen_blocks:
    seen_blocks.add(id(block))
    blocks.append(block)  # keeps it alive, so its id is not used again
```

## Lists of the model

The fields that hold a list of objects of the model, as `block.txs`, `tx.inputs`, `tx.outputs`, `tx.incoming_transfers` or
`tx_set.txs`, are the vectors of C++ (`VectorMoneroTx`, `VectorMoneroOutput`...), and what the vector does compares its objects
**by identity**: `in`, `==`, `index`, `remove` and `count`. A `list` compares them by value:

| | a vector, `tx.outputs` | a `list`, `list(tx.outputs)` |
| --- | --- | --- |
| `output in ...` | the same object is there | an equal object is there |
| `tx1.outputs == tx2.outputs` | the same objects, in the same order | equal objects, in the same order |

```python
copy: MoneroOutputWallet = output.copy()
assert copy == output
assert copy not in output.tx.outputs  # not the same object
assert copy in list(output.tx.outputs)  # an equal one
```

## Representation

The `repr` of an object is its class with its JSON, `MoneroTxWallet({"hash":"...",...})`, which is what pytest shows when an `==`
fails. [`MoneroRpcConnection`][monero.MoneroRpcConnection] shows `***` for its password, and
[`MoneroWalletConfig`][monero.MoneroWalletConfig] for its password, seed, seed offset, private keys and the password of its server, so
that they do not end up in a log. `serialize()` keeps them.

## Differences from monero-java

| monero-java | monero-python | |
| --- | --- | --- |
| `a == b`, `a != b` | `a is b`, `a is not b` | the same object |
| `a.equals(b)`, `assertEquals(a, b)` | `a == b` | the same values |
| `equals` of each class, field by field | `serialize()` of the two objects | the fields that are not serialized are not compared |
| `hashCode()`, `Set<MoneroBlock>`, `Map<MoneroTx, ...>` | not hashable | key by the hash, or by `id()` |
| `list.contains(x)`, with `equals` | `x in vector` by identity, `x in list(vector)` by value | the vectors of the model |
| `toString()`, an indented text | `repr()`, the JSON on one line | with the secrets hidden |

## Porting a test from monero-java

monero-java checks a copy with a pair of asserts, one for each meaning:

```java
MoneroTxConfig configCopy = config.copy();
// ...
assertTrue(configCopy != config);   // another object
assertEquals(configCopy, config);   // with the same values
```

In Python, the first is `is not`, not `!=`: `configCopy != config` would fail, since the copy has the same values.

```python
config_copy: MoneroTxConfig = config.copy()
# ...
assert config_copy is not config
assert config_copy == config
```

The same goes for the back references, which monero-java checks with `==`: `assertTrue(tx == output.getTx())` is
`assert output.tx is tx`. A `==` there would also pass with a copy of the tx, which is not what the test checks.
