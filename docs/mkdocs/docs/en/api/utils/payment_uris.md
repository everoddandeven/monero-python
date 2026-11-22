---
title: Payment URIs
---
# Payment URIs

A payment request as a URI, `monero:<address>?tx_amount=...`, often shown as a QR code: made from a
[`MoneroTxConfig`][monero.MoneroTxConfig], and read back into one ([Checking Out as a
Customer](../../examples/scenarios/checkout.md)).

::: monero.MoneroUtils.get_payment_uri

::: monero.MoneroUtils.parse_payment_uri
