from enum import IntEnum


class MoneroMessageSignatureType(IntEnum):
    """Enumerates the type of a Monero message signature."""

    SIGN_WITH_SPEND_KEY = 0
    """`0` Indicates that the message verification was signed with the wallet `private spend key`_.

    .. _private spend key: https://docs.getmonero.org/cryptography/asymmetric/private-key/#private-spend-key
    """

    SIGN_WITH_VIEW_KEY = 1
    """`1` Indicates that the message verification was signed with the wallet `private view key`_.

    .. _private view key: https://docs.getmonero.org/cryptography/asymmetric/private-key/#private-spend-key
    """
