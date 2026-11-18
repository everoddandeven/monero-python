from enum import IntEnum


class MoneroAddressType(IntEnum):
    """Models a `Monero public address type`_.

    .. _Monero public address type: https://docs.getmonero.org/public-address/
    """

    PRIMARY_ADDRESS = 0
    """`0` Indicates that the Monero address format is `standard`_, also known as `primary`.

    .. _standard: https://docs.getmonero.org/public-address/standard-address/
    """

    INTEGRATED_ADDRESS = 1
    """`1` Indicates that the Monero address format is `integrated`_.

    .. _integrated: https://docs.getmonero.org/public-address/integrated-address/
    """

    SUBADDRESS = 2
    """`2` Indicates that the Monero address format is `subaddress`_.

    .. _subaddress: https://docs.getmonero.org/public-address/subaddress/
    """
