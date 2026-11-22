---
title: Results and Notifications
---
# Results and Notifications

| Class | From |
| --- | --- |
| [`MoneroSyncResult`][monero.MoneroSyncResult] | [`sync`][monero.MoneroWallet.sync]: the blocks fetched, and whether money was received |
| [`MoneroKeyImageExportResult`][monero.MoneroKeyImageExportResult], [`MoneroKeyImageImportResult`][monero.MoneroKeyImageImportResult] | [`export_key_images`][monero.MoneroWallet.export_key_images], [`import_key_images`][monero.MoneroWallet.import_key_images] |
| [`MoneroMessageSignatureResult`][monero.MoneroMessageSignatureResult] | [`verify_message`][monero.MoneroWallet.verify_message] |
| [`MoneroCheck`][monero.MoneroCheck], [`MoneroCheckTx`][monero.MoneroCheckTx], [`MoneroCheckReserve`][monero.MoneroCheckReserve] | the checks of the [proofs](../../../examples/basics/proofs_and_signatures.md): [`check_tx_key`][monero.MoneroWallet.check_tx_key], [`check_tx_proof`][monero.MoneroWallet.check_tx_proof], [`check_reserve_proof`][monero.MoneroWallet.check_reserve_proof] |
| [`MoneroMultisigInfo`][monero.MoneroMultisigInfo], [`MoneroMultisigInitResult`][monero.MoneroMultisigInitResult], [`MoneroMultisigSignResult`][monero.MoneroMultisigSignResult] | the steps of a [multisig wallet](../../../examples/basics/multisig.md): [`get_multisig_info`][monero.MoneroWallet.get_multisig_info], [`exchange_multisig_keys`][monero.MoneroWallet.exchange_multisig_keys], [`sign_multisig_tx_hex`][monero.MoneroWallet.sign_multisig_tx_hex] |

[`MoneroWalletListener`][monero.MoneroWalletListener] is told what a sync finds: [Listening to a Wallet](../../../examples/basics/listening_to_a_wallet.md).

::: monero.MoneroSyncResult

::: monero.MoneroKeyImageExportResult

::: monero.MoneroKeyImageImportResult

::: monero.MoneroMessageSignatureResult

::: monero.MoneroCheck

::: monero.MoneroCheckTx

::: monero.MoneroCheckReserve

::: monero.MoneroMultisigInfo

::: monero.MoneroMultisigInitResult

::: monero.MoneroMultisigSignResult

::: monero.MoneroWalletListener
