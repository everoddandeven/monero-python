from typing_extensions import override
from monero import MoneroWalletListener


class WalletSyncPrinter(MoneroWalletListener):

    next_increment: float
    sync_resolution: float

    def __init__(self, sync_resolution: float = 0.05) -> None:
        super().__init__()
        self.next_increment = 0
        self.sync_resolution = sync_resolution

    @override
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str):
        if (percent_done == 1.0 or percent_done >= self.next_increment):
            msg = f"on_sync_progess({height}, {start_height}, {end_height}, {percent_done}, {message})"
            print(msg)
            self.next_increment += self.sync_resolution
