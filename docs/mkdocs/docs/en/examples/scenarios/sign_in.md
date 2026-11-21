---
title: Sign in with Monero
---
# Sign in with Monero

A site can let its users sign in with their Monero address instead of a password: the user proves that they have the keys of the
address by signing a message that the site gives, and the address is the account. The site keeps no password, and needs no daemon: a
[keys-only wallet](../../api/wallet_keys.md), offline, checks the signatures.

## The site: the challenge

The site gives a challenge for each sign-in: a random value, used once and only for a few minutes, and the name of the site, so that a
signature for one site does not open another.

```python
import secrets
import time

CHALLENGE_TTL = 300     # seconds
challenges: dict[str, float] = {}       # the challenges given, and when


def new_challenge() -> str:
    nonce = secrets.token_hex(16)
    challenge = f"Sign in to shop.example: {nonce}"
    challenges[challenge] = time.time()
    return challenge
```

## The user: the signature

The wallet of the user signs the challenge with the spend key of the address, which only its owner has:

```python
from monero import MoneroMessageSignatureType, MoneroNetworkType, MoneroWalletFull

user = MoneroWalletFull.open_wallet("wallets/user", "supersecretpassword123", MoneroNetworkType.MAINNET)
challenge = "Sign in to shop.example: ..."      # as the site gave it
signature = user.sign_message(challenge, MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY)
address = user.get_primary_address()
# send address and signature to the site
```

## The site: the check

```python
from monero import MoneroMessageSignatureType, MoneroNetworkType, MoneroUtils, MoneroWalletConfig, MoneroWalletKeys

# any wallet checks a signature: a keys-only one, made once when the site starts
config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
verifier = MoneroWalletKeys.create_wallet_random(config)


def sign_in(challenge: str, address: str, signature: str) -> bool:
    """Whether the signature of the challenge is of the address: the user of that address signs in."""
    given = challenges.pop(challenge, None)         # a challenge serves once
    if given is None or time.time() - given > CHALLENGE_TTL:
        return False
    if not MoneroUtils.is_valid_address(address, MoneroNetworkType.MAINNET):
        return False
    result = verifier.verify_message(challenge, address, signature)
    return result.is_good and result.signature_type == MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY
```

The site asks for a signature with the **spend key**: a signature with the view key proves only the view key, which the owner may have
given to others, as to an accountant.

## What the address is

- The account is the address: the same user signs in with the same address. A user with more wallets has more accounts.
- A signature proves the keys, not a person: whoever has the seed signs in. A lost seed is a lost account, and a stolen seed a stolen one.
- The address of the account is public to the site: it sees the payments to that address only with the view key, which the sign-in does
  not give. A user that does not want the site to link the account to their payments signs in with an address that they use for nothing
  else, such as a subaddress (`sign_message` takes its account and subaddress index).
