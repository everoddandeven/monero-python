from .monero_output_wallet import MoneroOutputWallet


class OutputComparator:
    """Compares two wallet outputs by ascending account, subaddress and output index."""

    @staticmethod
    def compare(output1: MoneroOutputWallet, output2: MoneroOutputWallet) -> bool:
        """
        Compare two wallet outputs.

        Compares by transaction height first (see `TxHeightComparator`), then
        by account index, subaddress index, output index and finally key
        image hex.

        :param MoneroOutputWallet output1: first output to compare.
        :param MoneroOutputWallet output2: second output to compare.

        :returns bool: `True` if output1 sorts before output2, `False` otherwise.
        """
        ...
