---
title: Logging
---
# Logging

monero-cpp and the wallet of monero log what they do, and nothing is written until the logging is configured. The log is the first
place to look when a wallet does not do what it should:

```python
from monero import MoneroUtils

MoneroUtils.configure_logging("monero.log", False)      # to a file, and not to the console
MoneroUtils.set_log_level(1)                            # 0 is the least, 4 the most
MoneroUtils.set_log_categories("*:WARNING,wallet.wallet2:INFO")
```

The categories are the ones of monero: a list of `category:level`, where `*` is every category. The `log_*` functions write to the
same log, for the messages of the application next to the ones of the wallet.

::: monero.MoneroUtils.configure_logging

::: monero.MoneroUtils.set_log_level

::: monero.MoneroUtils.set_log_categories

::: monero.MoneroUtils.log_trace

::: monero.MoneroUtils.log_debug

::: monero.MoneroUtils.log_info

::: monero.MoneroUtils.log_warning

::: monero.MoneroUtils.log_error
