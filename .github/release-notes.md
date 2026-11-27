## Breaking changes

<!-- the ones of this release, since the one before: replace them for the next one, or remove the section -->

- **The objects of the data model compare by value.** `a == b` is true for two objects of the same class with the same JSON (`serialize()`), also in the lists of the model (`in`, `count`, `remove`). It was true only for the same object: use `is` for that. `MoneroRpcConnection` compares the uri, the username, the password, the proxy uri, the zmq uri and the ssl verify.
- **The objects of the data model are not hashable.** `hash()` of one, putting it in a `set` or using it as a key of a `dict` raises `TypeError`: key them by what identifies them, as the hash of a tx, or by `id()`.
- **The raw RPC responses keep the types of their JSON**, in `send_json_request()` and the other raw requests of `MoneroRpcConnection`. A text stays a `str`, also when it looks like a number or a boolean, a large integer stays an `int` instead of becoming a `float`, `null` is `None`, and an empty list or object stays one.
- **Python 3.10 or later** is required: 3.8 and 3.9 are not supported anymore.
- **The macOS wheels need macOS 15 or later**: there is no wheel for macOS 14.
- **Type annotations:** `MoneroOutput.tx`, `MoneroTransfer.tx` and `MoneroRpcConnection.timeout_ms` can be `None`, and `MoneroTxQuery.include_outputs` is a `bool`: a type checker can report new errors.

## Which file to download

| Platform | File |
| --- | --- |
| Debian (`bookworm`, `trixie`) and Ubuntu (`jammy`, `noble`) on `amd64`, `arm64`, `armhf` | `python3-monero_<version>-1<distro>1_<arch>.deb`, installed with `sudo apt install ./<file>` |
| macOS (Apple silicon and Intel) | `monero-<version>-<python>-macosx_*.whl` |
| Windows (x86_64) | `monero-<version>-<python>-win_amd64.whl` |
| Anything else | `monero-python-<version>.tar.gz`, the source with its submodules (the "Source code" archives of GitHub have none of them) |

`coverage_monero_cpp_html.zip` is the coverage report of the tests.

## Verify a download

```bash
sha256sum -c --ignore-missing SHA256SUMS
gh attestation verify <file> --repo libmonero/monero-python
```

The first checks the file against the list published with the release, the second that it was built by the release workflow of this repository.

