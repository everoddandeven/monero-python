from monero import MoneroDaemon

MAX_GENERATE_DIFFICULTY: int = 100
"""Highest difficulty at which blocks are generated instead of mined.

`generateblocks` hashes with one thread in the light mode of RandomX, about 75 hashes per second, so a block takes difficulty / 75 seconds
(0.04 s at difficulty 1, 6.7 s at 500). The miner of the daemon hashes with the full dataset and is much faster: at a high difficulty
mining makes the blocks sooner, at a low one it makes dozens while the tests sleep, and the chain grows past what they want.
"""


def is_generation_fast(daemon: MoneroDaemon) -> bool:
    """Indicates if the daemon generates blocks faster than it mines them: a regtest daemon with a low difficulty.

    :param MoneroDaemon daemon: daemon to ask the difficulty of.
    :returns bool: `True` if blocks should be generated, `False` if they should be mined.
    """
    try:
        info = daemon.get_info()
        difficulty: int = (info.difficulty_high or 0) << 64 | (info.difficulty_low or 0)
        return info.is_regtest is not False and 0 < difficulty <= MAX_GENERATE_DIFFICULTY
    except Exception:
        return False
