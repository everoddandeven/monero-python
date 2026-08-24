from .monero_incoming_transfer import MoneroIncomingTransfer


class IncomingTransferComparator:
    """Compares two incoming transfers by ascending account and subaddress indices."""

    @staticmethod
    def compare(transfer1: MoneroIncomingTransfer, transfer2: MoneroIncomingTransfer) -> bool:
        """
        Compare two incoming transfers.

        Compares by transaction height first (see `TxHeightComparator`), then
        by account index, then by subaddress index.

        :param MoneroIncomingTransfer transfer1: first transfer to compare.
        :param MoneroIncomingTransfer transfer2: second transfer to compare.

        :returns bool: `True` if transfer1 sorts before transfer2, `False` otherwise.
        """
        ...
