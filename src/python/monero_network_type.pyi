from enum import IntEnum


class MoneroNetworkType(IntEnum):
    """Enumerates a `Monero network type`_.

    .. _Monero network type: https://docs.getmonero.org/infrastructure/networks/
    """

    MAINNET = 0
    """`0` indicates `Mainnet network`_.

    .. _Mainnet network: https://docs.getmonero.org/infrastructure/networks/#mainnet
    """

    TESTNET = 1
    """`1` indicates `Testnet network`_.

    .. _Testnet network: https://docs.getmonero.org/infrastructure/networks/#testnet
    """

    STAGENET = 2
    """`2` indicates `Stagenet network`_.

    .. _Stagenet network: https://docs.getmonero.org/infrastructure/networks/#stagenet
    """
