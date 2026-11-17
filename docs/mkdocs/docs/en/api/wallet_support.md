---
title: Wallet Support
---
# Wallet Support

Which methods of the [wallet interface][monero.MoneroWallet] each wallet implements: the [full wallet][monero.MoneroWalletFull], the
[RPC wallet][monero.MoneroWalletRpc], the [light wallet][monero.MoneroWalletLight] and the [keys-only wallet][monero.MoneroWalletKeys].
A method that a wallet does not implement raises an error that says it is not supported. The unit tests call every method on each wallet
and fail when this table says otherwise.

{% set icons = {
    "supported": ':material-check:{ .wallet-support--supported title="Supported" }',
    "partial": ':material-circle-half-full:{ .wallet-support--partial title="Partially supported" }',
    "todo": ':material-progress-wrench:{ .wallet-support--todo title="Not implemented yet" }',
    "unsupported": ':material-close:{ .wallet-support--unsupported title="Not supported" }',
} %}

| | |
| --- | --- |
| {{ icons.supported }} | supported |
| {{ icons.partial }} | partially supported: some of its overloads, the note under the method says which |
| {{ icons.todo }} | not implemented yet |
| {{ icons.unsupported }} | not supported: what the wallet is made on can not do it |

{# the entries by key, not entry.keys: jinja looks up an attribute first, and entry.keys is the method keys() of the dict #}
{% for section, methods in wallet_support.items() %}
## {{ section }}

| Method | Full | RPC | Light | Keys-only |
| --- | :---: | :---: | :---: | :---: |
{% for method, entry in methods.items() -%}
| [`{{ method }}`][monero.MoneroWallet.{{ method }}]{% if entry.get("note") %}<br><small>{{ entry["note"] }}</small>{% endif %} | {{ icons[entry["full"]] }} | {{ icons[entry["rpc"]] }} | {{ icons[entry["light"]] }} | {{ icons[entry["keys"]] }} |
{% endfor %}
{% endfor %}
