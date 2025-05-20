import typing


class MoneroConnectionPollType:
    """
    Members:
    
      PRIORITIZED
    
      CURRENT
    
      ALL
    
      UNDEFINED
    """
    ALL: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.ALL: 2>
    CURRENT: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.CURRENT: 1>
    PRIORITIZED: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.PRIORITIZED: 0>
    UNDEFINED: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.UNDEFINED: 3>
    __members__: typing.ClassVar[dict[str, MoneroConnectionPollType]]  # value = {'PRIORITIZED': <MoneroConnectionPollType.PRIORITIZED: 0>, 'CURRENT': <MoneroConnectionPollType.CURRENT: 1>, 'ALL': <MoneroConnectionPollType.ALL: 2>, 'UNDEFINED': <MoneroConnectionPollType.UNDEFINED: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
