from abc import ABC


class GenUtils(ABC):
    """Collection of generic utilities."""

    @staticmethod
    def get_uuid() -> str:
        """
        Return a random unique identifier.

        :returns str: a unique id.
        """
        ...

    @staticmethod
    def wait_for(duration_ms: int) -> None:
        """
        Block the calling thread for the given duration. Releases the GIL
        while sleeping.

        :param int duration_ms: duration to wait, in milliseconds.
        :raises TypeError: Must be a non-negative number that fits in a valid `uint64_t` range.
        """
        ...

    @staticmethod
    def bool_equals(val: bool, opt_val: bool | None) -> bool:
        """
        Compare a bool to an optional bool.

        :param bool val: value to compare.
        :param bool|None opt_val: optional value to compare against; `False` if `None`.

        :returns bool: `True` if `opt_val` is set and equals `val`, `False` otherwise.
        """
        ...

    @staticmethod
    def reconcile_bool(
        val1: bool | None,
        val2: bool | None,
        resolve_defined: bool | None = None,
        resolve_true: bool | None = None,
        resolve_max: bool | None = None,
        err_msg: str = "",
    ) -> bool | None:
        """
        Reconcile two optional bools to a single value, the same logic used
        internally to merge model fields (e.g. `MoneroTx.merge()`).

        - If both are equal (including both `None`), returns that value.
        - If exactly one is `None`, returns the other, unless `resolve_defined`
          is `False`, in which case `None` is returned.
        - Otherwise, if both are set and differ: `resolve_true` picks whichever
          operand equals `resolve_true`; else `resolve_max` picks the greater
          (`True`) or lesser (`False`) of the two, treating `True` as 1 and
          `False` as 0.

        :param bool|None val1: first value.
        :param bool|None val2: second value.
        :param bool|None resolve_defined: when only one side is set and this
            is `False`, return `None` instead of the set side.
        :param bool|None resolve_true: when both sides are set and differ,
            prefer whichever operand equals this value.
        :param bool|None resolve_max: when both sides are set and differ
            (and `resolve_true` didn't resolve it), prefer the greater (`True`)
            or lesser (`False`) value.
        :param str err_msg: extra context appended to the error message on conflict.

        :returns bool|None: the reconciled value.
        :raises RuntimeError: If none of the above resolves.
        """
        ...

    @staticmethod
    def reconcile_uint64(
        val1: int | None,
        val2: int | None,
        resolve_defined: bool | None = None,
        resolve_true: bool | None = None,
        resolve_max: bool | None = None,
        err_msg: str = "",
    ) -> int | None:
        """
        Reconcile two optional unsigned 64-bit integers. See `reconcile_bool`
        for the resolution rules (`resolve_max` here picks the numeric max/min).

        :param int|None val1: first value.
        :param int|None val2: second value.
        :param bool|None resolve_defined: see `reconcile_bool`.
        :param bool|None resolve_true: see `reconcile_bool`.
        :param bool|None resolve_max: prefer the larger (`True`) or smaller (`False`) value.
        :param str err_msg: extra context appended to the error message on conflict.

        :returns int|None: the reconciled value.
        :raises RuntimeError: If none of the above resolves.
        """
        ...

    @staticmethod
    def reconcile_string(
        val1: str | None,
        val2: str | None,
        resolve_defined: bool | None = None,
        resolve_true: bool | None = None,
        resolve_max: bool | None = None,
        err_msg: str = "",
    ) -> str | None:
        """
        Reconcile two optional strings. Unlike the bool/int overloads,
        `resolve_true`/`resolve_max` are accepted for signature symmetry but
        are not used.

        :param str|None val1: first value.
        :param str|None val2: second value.
        :param bool|None resolve_defined: see `reconcile_bool`.
        :param bool|None resolve_true: accepted but ignored.
        :param bool|None resolve_max: accepted but ignored.
        :param str err_msg: extra context appended to the error message on conflict.

        :returns str|None: the reconciled value.
        :raises RuntimeError: on different strings always regardless of `resolve_true`/`resolve_max` flags.
        """
        ...

    @staticmethod
    def reconcile_string_list(v1: list[str], v2: list[str], err_msg: str = "") -> list[str]:
        """
        Reconcile two string lists: equal lists are returned as-is, an empty
        list yields the other.

        :param list[str] v1: first list.
        :param list[str] v2: second list.
        :param str err_msg: extra context appended to the error message on conflict.

        :returns list[str]: the reconciled list.
        :raises RuntimeError: on two different non-empty lists.
        """
        ...
