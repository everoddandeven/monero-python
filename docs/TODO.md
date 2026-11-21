# TODO

## Versioned documentation

**Status:** not started. **When:** after 1.0. Until then the API changes from one release to the next, the users take the last
release, and the site of `main` is the one they need. With a site for each release, a fix to the docs has to reach each of them.

### Goal

The site has the docs of each release and of `main`, with a version selector in the header (the one of Material for MkDocs):

```
https://libmonero.github.io/monero-python/            -> the last release
https://libmonero.github.io/monero-python/0.9/        -> the docs of 0.9.x
https://libmonero.github.io/monero-python/1.0/        -> the docs of 1.0.x
https://libmonero.github.io/monero-python/dev/        -> the docs of main, with the coverage reports
```

### How the site is published now

- `ci.yml` calls `docs.yml` on `main`, after its `coverage` job. `docs.yml` builds the site, adds the coverage reports of the run in
  `coverage/` and deploys it with `actions/upload-pages-artifact` and `actions/deploy-pages`.
- GitHub Pages is set to the source **GitHub Actions** (Settings → Pages). There is no `gh-pages` branch.
- Each deploy replaces the whole site: it has one version, the one of the last commit of `main`.
- `release.yml` runs on a `v*` tag and makes a draft release. It does not touch the docs.

### Options

#### A. mike

[mike](https://github.com/jimporter/mike) builds each version into a folder of a `gh-pages` branch and writes the `versions.json`
that the selector of Material reads.

- Pages moves to the source **Deploy from a branch** (`gh-pages`), and `deploy-pages` goes.
- The jobs that publish push to `gh-pages`: `contents: write`, and a checkout that keeps its credentials (zizmor reports both, they
  need an ignore with the reason).
- The coverage reports are not part of what mike builds: they would be committed to `gh-pages` by another step, in the folder of
  `dev`, after `mike deploy`.
- `main` and a release can push to `gh-pages` at the same time: one concurrency group for both.
- `gh-pages` grows with every deploy, a commit each time, with the whole site of that version.

#### B. Each release keeps its built site, Pages assembles them (recommended)

The selector of Material only needs a `versions.json` at the root of the site (`extra.version.provider: mike`), it does not need mike.
The deploy of now stays, and builds a site that has every version:

- `release.yml` builds the site of the tag and attaches it to the release, as `docs-<version>.tar.gz`, next to the wheels. It is then
  fixed: a later change of the tools does not change the docs of an old release.
- `docs.yml`, on `main`: builds `dev` (with the coverage reports, as now), downloads the docs of each published release, puts each
  one in its folder, writes `versions.json` and the redirect of the root to the last release, and deploys it all as one artifact, as now.
- No branch, no `contents: write`, the same permissions and the same deploy as now.
- A new release appears on the site at the next deploy of `main`: `release.yml` can call `docs.yml` too, once the release is published.

### Plan (option B)

1. **Version selector.** In `mkdocs.yml`:
   ```yaml
   extra:
     version:
       provider: mike
       default: latest
   ```
   Check that it works with the i18n plugin (`mkdocs-static-i18n`), which puts the pages under `en/` in `docs/`.
2. **Folder of a version.** One folder for each minor version (`0.9`, `1.0`): a patch release replaces the docs of its minor. Decide
   whether `0.9.11` and `0.9.12` need folders of their own (they should not, the API of a patch release does not change).
3. **Docs of a release.** A job in `release.yml`, after `check`: checks out the tag, builds the site with the
   `docs/mkdocs/requirements.in` of the tag, with `site_url` set to the folder of its version, packs `public/` as
   `docs-<version>.tar.gz` and adds it to the assets of the draft release, and to `SHA256SUMS` and to the attestation.
4. **Assembling the site.** In `docs.yml`, a step after the build of `dev`:
   - lists the published releases (`gh release list`, the drafts left out) and downloads their `docs-*.tar.gz`, checked against
     their `SHA256SUMS`;
   - extracts each one in `public/<version>/`, and moves the site of `main` to `public/dev/`;
   - writes `public/versions.json`, the newest version first, with the alias `latest` on the last release:
     ```json
     [
       {"version": "0.9", "title": "0.9.11", "aliases": ["latest"]},
       {"version": "dev", "title": "dev (main)", "aliases": []}
     ]
     ```
   - writes `public/index.html` and `public/latest/index.html`, which redirect to the folder of the last release.
5. **Coverage.** Only in `dev`, as now: the `coverage/` page of `dev` links the reports of the last run of `main`. The docs of a
   release have the page without the reports, or the page leaves the release out (decide which).
6. **Publishing a release.** `release.yml` makes a draft: the docs of a version appear once the release is published. Either
   `docs.yml` also runs on `release: published`, or the next push to `main` brings them.
7. **Links that exist now.** The pages are at the root now (`/api/wallet/`), they will be at `/<version>/api/wallet/`. A link from
   outside to a page of now would give a 404: the `404.html` of the root can send to the same path under `latest/`.
8. **Local preview.** `bin/docs.sh` stays as it is, for the docs of the working tree. To see the site with its versions, a script that
   assembles it as `docs.yml` does, from the releases on GitHub, in a folder of its own.

### To check before starting

- The first release with docs in its assets is the first after this change: the releases before it have no docs to download. Either
  they stay out of the selector, or their docs are built once from their tags and attached to them by hand.
- The size of the artifact of Pages (the limit is 1 GB), with every version and the coverage reports.
- The search of Material is per version: it finds the pages of the version that is open, not the ones of the others.

## Fields of the stubs that can be None

**Status:** to decide. **When:** before 1.0, since it changes the types that the code of the users is checked against.

### The problem

Some fields of the stubs are declared as never `None`, and are `None` at runtime:

| Field | Declared | When it is `None` |
| --- | --- | --- |
| `MoneroTransfer.tx`, and so `MoneroIncomingTransfer.tx`, `MoneroOutgoingTransfer.tx` | `MoneroTxWallet` | a transfer made by hand; any transfer after `MoneroUtils.free`, which breaks its link to the transaction; one given to a listener, after the listener returns |
| `MoneroOutput.tx`, and so `MoneroOutputWallet.tx` | `MoneroTx` | the same: an output made by hand, after `free`, after a listener |
| `MoneroRpcConnection.timeout_ms` | `int` | a connection made without a timeout, which waits the 3 minutes of monero-cpp |

A type checker trusts the stub: `transfer.tx.hash` passes the check, and raises `AttributeError: 'NoneType' object has no attribute
'hash'` when the link was freed.

### Options

- **`X | None`, as it is at runtime.** The stubs say the truth, and the type checker asks for a check before each use:
  `assert transfer.tx is not None`. The tests and the examples of the docs, which use `transfer.tx` and `output.tx` in many places, need
  those checks, and so does the code of the users.
- **Keep them, and document them.** The fields are not `None` for what a wallet or a daemon returns, until `free`: the stubs describe
  the common case, and the docstrings say when they are `None`. The type checker misses the other cases.

`timeout_ms` is apart: `int | None`, with `None` documented as the default of 3 minutes, changes little.

### Finding the others

The fields above were found by making each class of the model with no arguments, and comparing each field with its annotation in the
stubs. It finds a field that is `None` on a new object; a field that becomes `None` only later, as `tx` after `free`, needs the code of
the binding, or of monero-cpp, to be read:

```python
import ast, pathlib, monero

for stub in sorted(pathlib.Path("src/monero").glob("*.pyi")):
    for cls in [node for node in ast.parse(stub.read_text()).body if isinstance(node, ast.ClassDef)]:
        try:
            obj = getattr(monero, cls.name)()
        except Exception:
            continue
        for field in [node for node in cls.body if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)]:
            if "None" not in ast.unparse(field.annotation) and getattr(obj, field.target.id) is None:
                print(f"{cls.name}.{field.target.id}: {ast.unparse(field.annotation)}")
```

The same can be asked of the methods: what a method returns when there is nothing, `None` or an empty object. `MoneroWallet.get_tx`
and `MoneroDaemon.get_tx` already say `| None`.
