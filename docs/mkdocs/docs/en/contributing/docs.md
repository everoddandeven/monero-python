---
title: Writing the Docs
# the page shows the syntax of the macros, which it does not use
render_macros: false
---
# Writing the Docs

The site is made with [MkDocs](https://www.mkdocs.org){ target="_blank" rel="noopener" } and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){ target="_blank" rel="noopener" }, from the Markdown of
`docs/mkdocs/docs/en` and from the stubs of `src/monero`. Its configuration is `docs/mkdocs/mkdocs.yml`, the versions of its tools
`docs/mkdocs/requirements.in`.

## Seeing it

| How | What |
| --- | --- |
| `./bin/docs.sh serve` | the site at `http://127.0.0.1:8000`, built again at every change |
| `./bin/docs.sh build` | the site in `docs/mkdocs/public`, strict as in CI |
| **Run and Debug → `docs: build and serve`** in VS Code | the strict build and the server, opened in the browser; a breakpoint in the extensions of griffe stops |

`bin/docs.sh` installs the tools of `requirements.in` in `.cache` the first time, and again when the file changes.

The build is **strict**: a warning fails it, as in CI. A warning is:

- a reference to the API that does not resolve, as `[MoneroWallet.sync][monero.MoneroWallet.sync]` to a method that is not there;
- a link to a page or to an anchor that does not exist, as `[x](../api/wallet.md#no-such-section)`;
- a page that is not in the `nav`, or a variable of the macros that does not exist.

## A page

A page is a Markdown file in `docs/mkdocs/docs/en`, with a `title` in its front matter, and an entry in the `nav` of `mkdocs.yml`:

```markdown
---
title: Proof of Reserves
---
# Proof of Reserves

The text of the page.
```

What a page can use:

| To | Write |
| --- | --- |
| link a class or a method of the API | `` [`sync`][monero.MoneroWallet.sync] ``: autorefs finds its page and its anchor |
| link another page | `[Glossary](../api/glossary.md#amounts)`, relative to the page, with the anchor of a heading |
| link a page outside the site, opened in a new tab | `[monero-cpp](https://github.com/woodser/monero-cpp){ target="_blank" rel="noopener" }` |
| a note or a warning | `!!! note "Title"` or `!!! warning "Title"`, with the text indented under it |
| a diagram | a code block of the language `mermaid`, drawn by Material ([Wallet Data Model](../api/data_model/wallet/index.md) has some) |
| a part of a file of the repository, kept in one place | `--8<-- "README.md:installation"`, see below |

## The API Reference

The pages of the API are made by mkdocstrings from the **stubs** of `src/monero`, without importing the module. What a reader sees of
a class or a method is its stub: its signature, and its docstring in the style of Sphinx.

```python
def get_balance(self, account_idx: int) -> int:
    """
    Get the balance of an account.

    :param int account_idx: index of the account.
    :returns int: the balance of the account, in atomic units.
    :raises MoneroError: if the account does not exist.
    """
    ...
```

- `:param`, `:returns` and `:raises` are the fields that the parser reads: a field with another name, as `:params`, is left out of the
  page.
- A link in a docstring is written as in reStructuredText, which editors show as it is: `` `monerod-rpc`_ `` and its target
  `.. _monerod-rpc: https://...` in the same docstring. The extension `griffe_rst_links.py` makes it a link of the page, opened in a
  new tab.
- A function with `@typing.overload` and no implementation, as most of the stubs have, is shown by the extension `griffe_overloads.py`:
  one signature for each overload, and one docstring made from theirs.
- A signature longer than a line is formatted on more lines by Ruff.

A page of the API is the directive of the class, `::: monero.MoneroWallet`, after a text that says what the class is for.

## The code of the examples

The ` ```python ` blocks of the pages and of `README.md` are checked against the stubs with pyright, by `bin/check_examples.py`, in CI
and before a pull request:

```bash
python3 bin/check_examples.py
```

- The blocks of a page are one file: a block can use what a block before it defined.
- An error is reported at its line of the Markdown, as `query_wallet_txs_and_transfers.md:67:5`.
- A value that the reader fills in is `"..."`, a string: the code stays valid.
- The pages of the tests are not checked: they show pieces of the code of `tests/`, which is checked where it is.

## Snippets

A part of a file of the repository that a page shows, as the installation of `README.md` or the reporting of `SECURITY.md`, is kept in
that file, between two markers, and the page includes it:

```markdown
<!-- --8<-- [start:installation] -->
The text, in README.md.
<!-- --8<-- [end:installation] -->
```

```markdown
--8<-- "README.md:installation"
```

The path is from the root of the repository. A snippet that is not found fails the build.

## The macros

A page can use the variables of [mkdocs-macros](https://mkdocs-macros-plugin.readthedocs.io){ target="_blank" rel="noopener" }, in
`{{ ... }}` and `{% ... %}`:

| Variable | Where it comes from | Used by |
| --- | --- | --- |
| `commit` | `GITHUB_SHA`, read by `docs/mkdocs/variables.py` | the Coverage page |
| `wallet_support` | `tests/wallet/wallet_support.yml` | the Wallet Support page |

A variable that does not exist fails the build. A page that shows these braces as text, as this one, has `render_macros: false` in its
front matter.

## The checks

| Command | What it checks |
| --- | --- |
| `./bin/docs.sh build` | the site, strict |
| `python3 bin/check_examples.py` | the code of the examples |
| `./bin/check_spelling.sh` | the spelling, with the words that are not typos in `.codespellrc` |
| `./bin/check_links.sh` | the links to the web, which CI checks every week |

CI builds the site, and checks the examples, on every pull request that changes the docs, the stubs or `README.md`
([Continuous Integration](ci.md)).
