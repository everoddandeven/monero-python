---
title: Accounts and Addresses
---
# Accounts and Addresses

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroAccount`][monero.MoneroAccount], [`MoneroSubaddress`][monero.MoneroSubaddress] | an account, with its balance and its `subaddresses`, and a subaddress with its own | [`get_accounts`][monero.MoneroWallet.get_accounts], [`get_subaddresses`][monero.MoneroWallet.get_subaddresses] |
| [`MoneroAccountTag`][monero.MoneroAccountTag] | a tag that groups accounts | [`get_account_tags`][monero.MoneroWallet.get_account_tags] |
| [`MoneroIntegratedAddress`][monero.MoneroIntegratedAddress] | an address with a payment ID | [`get_integrated_address`][monero.MoneroWallet.get_integrated_address], [`decode_integrated_address`][monero.MoneroWallet.decode_integrated_address] |
| [`MoneroDecodedAddress`][monero.MoneroDecodedAddress], [`MoneroAddressType`][monero.MoneroAddressType] | an address, with its network and its type: standard, integrated or subaddress | |
| [`MoneroAddressBookEntry`][monero.MoneroAddressBookEntry] | an address saved in the wallet, with its description | [`get_address_book_entries`][monero.MoneroWallet.get_address_book_entries] |

::: monero.MoneroAccount

::: monero.MoneroSubaddress

::: monero.MoneroAccountTag

::: monero.MoneroIntegratedAddress

::: monero.MoneroDecodedAddress

::: monero.MoneroAddressType

::: monero.MoneroAddressBookEntry
