---
title: The Daemon and its Network
---
# The Daemon and its Network

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroNetworkType`][monero.MoneroNetworkType] | mainnet, testnet or stagenet ([Glossary](../../glossary.md#networks)) | the network of a daemon, of a wallet, of an address |
| [`MoneroVersion`][monero.MoneroVersion] | the version of a daemon, or of a wallet server | [`get_version`][monero.MoneroDaemon.get_version] |
| [`MoneroDaemonInfo`][monero.MoneroDaemonInfo] | the state of the daemon: height, network, connections, size of the chain | [`get_info`][monero.MoneroDaemon.get_info] |
| [`MoneroDaemonSyncInfo`][monero.MoneroDaemonSyncInfo], [`MoneroConnectionSpan`][monero.MoneroConnectionSpan] | how far the daemon is in syncing the chain, and the blocks that it is downloading from its peers | [`get_sync_info`][monero.MoneroDaemon.get_sync_info] |
| [`MoneroPeer`][monero.MoneroPeer], [`MoneroBan`][monero.MoneroBan] | a peer of the daemon, and a peer that it bans | [`get_peers`][monero.MoneroDaemon.get_peers], [`get_peer_bans`][monero.MoneroDaemon.get_peer_bans], [`set_peer_ban`][monero.MoneroDaemon.set_peer_ban] |
| [`MoneroDaemonNetworkStats`][monero.MoneroDaemonNetworkStats] | the traffic of the daemon | [`get_network_stats`][monero.MoneroDaemon.get_network_stats] |
| [`MoneroDaemonUpdateCheckResult`][monero.MoneroDaemonUpdateCheckResult], [`MoneroDaemonUpdateDownloadResult`][monero.MoneroDaemonUpdateDownloadResult] | a new version of monero, and its download | [`check_for_update`][monero.MoneroDaemon.check_for_update], [`download_update`][monero.MoneroDaemon.download_update] |
| [`MoneroRpcPaymentInfo`][monero.MoneroRpcPaymentInfo] | the credits of a daemon that is paid for its RPC: the base of the results that report them | |

[`MoneroDaemonListener`][monero.MoneroDaemonListener] is told of the new blocks: [Listening to a Wallet](../../../examples/basics/listening_to_a_wallet.md#a-daemon).

::: monero.MoneroNetworkType

::: monero.MoneroVersion

::: monero.MoneroDaemonInfo

::: monero.MoneroDaemonSyncInfo

::: monero.MoneroConnectionSpan

::: monero.MoneroPeer

::: monero.MoneroBan

::: monero.MoneroDaemonNetworkStats

::: monero.MoneroDaemonUpdateCheckResult

::: monero.MoneroDaemonUpdateDownloadResult

::: monero.MoneroRpcPaymentInfo

::: monero.MoneroDaemonListener
