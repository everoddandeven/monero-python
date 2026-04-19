class MoneroConnectionPriorityComparator:
    """Connection priority compare utils."""

    @staticmethod
    def compare(p1: int, p2: int) -> bool:
        """
        Compare connection priorities.

        :param int p1: first priority to check.
        :param int p2: second priority to check.

        :returns bool: `True` if `p1` comes before `p2`, `False` otherwise.
        """
        ...
