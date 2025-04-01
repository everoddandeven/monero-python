from monero import Wallet

wallet = Wallet(seed="your seed here", restore_height=0)
print("Address:", wallet.get_primary_address())
print("Balance:", wallet.get_balance())
