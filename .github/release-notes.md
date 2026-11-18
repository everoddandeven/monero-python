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

