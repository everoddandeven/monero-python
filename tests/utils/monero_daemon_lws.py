import logging
import time
from typing import Any
from monero import MoneroRpcConnection

logger: logging.Logger = logging.getLogger("MoneroDaemonLws")


class MoneroDaemonLws:
    """Thin client for the monero-lws REST API, both the client (wallet) surface and the
    admin surface.

    Client: `/login`, `/get_address_info`, `/get_address_txs`, `/get_random_outs`,
    `/get_subaddrs`, `/get_unspent_outs`, `/get_version`, `/import_wallet_request`,
    `/provision_subaddrs`, `/submit_raw_tx`, `/upsert_subaddrs`, and the undocumented
    `/daemon_status` convenience endpoint. `MoneroWalletLight` exercises this same surface
    internally; this exists to inspect the raw server responses directly (e.g. to correlate
    `scanned_block_height`/`start_height` against the daemon's own height during debugging).
    `/feed` (websocket upgrade) and `/get_tree_path` (fcmp++ tree signing) are out of scope.

    Admin: `/accept_requests`, `/add_account`, `/list_accounts`, `/list_requests`,
    `/modify_account_status`, `/reject_requests`, `/rescan`, `/validate`, `/webhook_add`,
    `/webhook_delete`, `/webhook_delete_uuid`, and `/webhook_list`.
    """

    rpc: MoneroRpcConnection | None
    """Rpc connection to the monero-lws client (wallet) REST server, or `None` if this
    instance was constructed without a client `uri` (admin-only usage)."""
    admin_rpc: MoneroRpcConnection | None
    """Rpc connection to the monero-lws admin REST server, or `None` if this instance was
    constructed without an `admin_uri` (client-only usage).

    monero-lws serves the client and admin surfaces on separate listeners (`--rest-server`
    and `--admin-rest-server`), which can be different ports entirely, or the same host:port
    merged by path prefix -- either way they are logically and physically distinct
    connections, so each gets its own `MoneroRpcConnection` rather than sharing one."""
    auth: str | None
    """Admin auth key from `monero-lws-admin create_admin`, or `None` if the server was
    started with `--disable-admin-auth`."""

    def __init__(self, uri: str | None = None, admin_uri: str | None = None, auth: str | None = None) -> None:
        """Initialize a new monero-lws client, admin, or combined client.

        At least one of `uri`/`admin_uri` must be given. Calling a client method without a
        `uri`, or an admin method without an `admin_uri`, raises `RuntimeError`.

        :param str | None uri: client (wallet) REST server uri, e.g. `http://127.0.0.1:8443`.
        :param str | None admin_uri: admin REST server uri, e.g. `http://127.0.0.1:8444`.
        :param str | None auth: admin auth key, if the server requires one.
        """
        if uri is None and admin_uri is None:
            raise ValueError("Must provide at least one of uri or admin_uri")

        # do not call MoneroRpcConnection.check_connection() here: it probes with a binary
        # get_blocks_by_height request meant for a monerod daemon connection, which monero-lws
        # doesn't implement (404, tolerated) -- but reusing that same keep-alive connection
        # afterwards for a JSON request (e.g. get_address_info) then arrives at the server with
        # a corrupted/truncated body ("missing required field: address"). A connection that's
        # genuinely unreachable will fail clearly on the first real request anyway.
        self.rpc = MoneroRpcConnection(uri) if uri is not None else None
        self.admin_rpc = MoneroRpcConnection(admin_uri) if admin_uri is not None else None

        self.auth = auth

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Send an admin request and return the parsed JSON response.

        :param str endpoint: admin endpoint name (without the leading `/`).
        :param dict[str, Any] | None params: endpoint-specific `params` object, if any.
        :returns Any: the parsed JSON response.
        :raises RuntimeError: if this instance was constructed without an `admin_uri`.
        """
        if self.admin_rpc is None:
            raise RuntimeError("MoneroDaemonLws was constructed without admin_uri; cannot call admin endpoints")

        body: dict[str, Any] = {}
        if params is not None:
            body["params"] = params
        if self.auth is not None:
            body["auth"] = self.auth
        logger.debug(f"POST (admin) /{endpoint} {body}")
        return self.admin_rpc.send_path_request(endpoint, body)

    def _client_request(self, endpoint: str, body: dict[str, Any]) -> Any:
        """Send a client (wallet) request and return the parsed JSON response.

        Unlike the admin surface, client endpoints take the request fields directly at the
        top level of the body -- there is no `params`/`auth` wrapper.

        :param str endpoint: client endpoint name (without the leading `/`).
        :param dict[str, Any] body: the full request body.
        :returns Any: the parsed JSON response.
        :raises RuntimeError: if this instance was constructed without a client `uri`.
        """
        if self.rpc is None:
            raise RuntimeError("MoneroDaemonLws was constructed without uri; cannot call client endpoints")

        logger.debug(f"POST /{endpoint} {body}")
        return self.rpc.send_path_request(endpoint, body)

    @staticmethod
    def _address_meta(lookahead: tuple[int, int]) -> dict[str, int]:
        """Build an `address_meta` (subaddress lookahead) object.

        :param tuple[int, int] lookahead: `(maj_i, min_i)`.
        :returns dict[str, int]: `{"maj_i": ..., "min_i": ...}`.
        """
        return {"maj_i": lookahead[0], "min_i": lookahead[1]}

    #region Client API

    def daemon_status(self) -> dict[str, Any]:
        """Get the underlying daemon's connection/sync state, as seen by monero-lws.

        Undocumented convenience endpoint (mentioned in `wallet.yaml`'s description but not
        given its own path entry).

        :returns dict[str, Any]: `state`, `outgoing_connections_count`,
            `incoming_connections_count`, `height`, `target_height`, `network`.
        """
        return self._client_request("daemon_status", {})

    def login(
        self,
        address: str,
        view_key: str,
        create_account: bool = False,
        generated_locally: bool = False,
        lookahead: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        """Create and/or check an account's status.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param bool create_account: attempt account creation if it doesn't already exist.
        :param bool generated_locally: `True` if this is a brand new (not restored) wallet.
        :param tuple[int, int] | None lookahead: desired `(maj_i, min_i)` lookahead for a
            newly created account.
        :returns dict[str, Any]: `new_address`, `generated_locally`, `start_height`, `lookahead`.
        """
        body: dict[str, Any] = {
            "address": address,
            "view_key": view_key,
            "create_account": create_account,
            "generated_locally": generated_locally,
        }
        if lookahead is not None:
            body["lookahead"] = self._address_meta(lookahead)
        return self._client_request("login", body)

    def get_address_info(self, address: str, view_key: str) -> dict[str, Any]:
        """Get the minimal information needed to calculate a wallet's balance.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :returns dict[str, Any]: `locked_funds`, `total_received`, `total_sent`,
            `scanned_height`, `scanned_block_height`, `start_height`, `transaction_height`,
            `blockchain_height`, `spent_outputs`, `lookahead`, `lookahead_failure`, `rates`.
        """
        return self._client_request("get_address_info", {"address": address, "view_key": view_key})

    def wait_for_scan_height(
        self,
        address: str,
        view_key: str,
        height: int,
        timeout_seconds: float = 60.0,
        poll_interval_seconds: float = 2.0,
    ) -> int:
        """Poll `get_address_info` for an already-registered account until its scan progress
        reaches `height`.

        monero-lws scans blocks asynchronously in the background, so an account's
        `scanned_height` can lag behind the daemon's live height for a short while after new
        blocks appear. A newly created account's own `start_height` is assigned from the
        server's current scan progress at that instant, so callers that need a new account's
        `start_height` to match a specific daemon height should wait for an already-registered
        account to catch up to that height first, before creating the new one.

        :param str address: base58 primary address of an already-registered account.
        :param str view_key: hex-encoded private view key for `address`.
        :param int height: block height to wait for.
        :param float timeout_seconds: give up and raise after this many seconds.
        :param float poll_interval_seconds: delay between polls.
        :returns int: the reached `scanned_height` (>= `height`).
        :raises TimeoutError: if `height` isn't reached within `timeout_seconds`.
        """
        deadline = time.monotonic() + timeout_seconds
        scanned_height = 0
        while True:
            scanned_height = self.get_address_info(address, view_key)["scanned_height"]
            if scanned_height >= height:
                return scanned_height
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"monero-lws scan did not reach height {height} within {timeout_seconds}s "
                    f"(stuck at {scanned_height})"
                )
            time.sleep(poll_interval_seconds)

    def get_address_txs(
        self,
        address: str,
        view_key: str,
        since_tx_id: int | None = None,
        since_tx_block_hash: str | None = None,
    ) -> dict[str, Any]:
        """Get transaction history.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param int | None since_tx_id: only return transactions newer than this known tx id.
        :param str | None since_tx_block_hash: block hash of the `since_tx_id` transaction,
            required if `since_tx_id` is given (guards against a reorg invalidating it).
        :returns dict[str, Any]: `total_received`, `scanned_height`, `scanned_block_height`,
            `start_height`, `blockchain_height`, `transactions`, `lookahead`,
            `lookahead_failure`, `since_tx_id`.
        """
        body: dict[str, Any] = {"address": address, "view_key": view_key}
        if since_tx_id is not None:
            body["since_tx_id"] = since_tx_id
        if since_tx_block_hash is not None:
            body["since_tx_block_hash"] = since_tx_block_hash
        return self._client_request("get_address_txs", body)

    def get_random_outs(self, count: int, amounts: list[str]) -> dict[str, Any]:
        """Get server-selected decoy outputs for ring signatures.

        :param int count: mixin (number of decoys per amount).
        :param list[str] amounts: XMR amounts (as decimal strings) that need decoys; `"0"`
            for RingCT outputs.
        :returns dict[str, Any]: `{"amount_outs": [...]}`.
        """
        return self._client_request("get_random_outs", {"count": count, "amounts": amounts})

    def get_subaddrs(self, address: str, view_key: str) -> dict[str, Any]:
        """Get all subaddresses provisioned for a wallet.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :returns dict[str, Any]: `all_subaddrs`, `max_subaddrs`.
        """
        return self._client_request("get_subaddrs", {"address": address, "view_key": view_key})

    def get_unspent_outs(
        self,
        address: str,
        view_key: str,
        amount: int,
        mixin: int,
        use_dust: bool,
        dust_threshold: str | None = None,
    ) -> dict[str, Any]:
        """Get outputs available for spending (client must determine what's already spent).

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param int amount: XMR amount intended to be sent.
        :param int mixin: minimum mixin for source outputs.
        :param bool use_dust: return all available outputs, including dust.
        :param str | None dust_threshold: ignore outputs below this amount (decimal string).
        :returns dict[str, Any]: `per_byte_fee`, `fee_mask`, `amount`, `outputs`, `fees`
            (priority-ordered fee-per-byte estimates, lowest first).
        """
        body: dict[str, Any] = {
            "address": address,
            "view_key": view_key,
            "amount": amount,
            "mixin": mixin,
            "use_dust": use_dust,
        }
        if dust_threshold is not None:
            body["dust_threshold"] = dust_threshold
        return self._client_request("get_unspent_outs", body)

    def get_version(self) -> dict[str, Any]:
        """Get basic information about the monero-lws server itself.

        :returns dict[str, Any]: `server_type`, `last_git_commit_hash`, `last_commit_date`,
            `monero_version_full`, `blockchain_height`, `api`, `max_subaddresses`, `network`,
            `testnet`.
        """
        return self._client_request("get_version", {})

    def import_wallet_request(
        self,
        address: str,
        view_key: str,
        from_height: int | None = None,
        lookahead: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        """Request a rescan from an earlier height, with optional subaddress lookahead.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param int | None from_height: height to rescan from (server assumes `0` if omitted).
        :param tuple[int, int] | None lookahead: desired `(maj_i, min_i)` lookahead for the
            rescan (server assumes `(0, 0)` if omitted).
        :returns dict[str, Any]: `payment_address`, `payment_id`, `import_fee`, `new_request`,
            `request_fulfilled`, `status`, `lookahead`.
        """
        body: dict[str, Any] = {"address": address, "view_key": view_key}
        if from_height is not None:
            body["from_height"] = from_height
        if lookahead is not None:
            body["lookahead"] = self._address_meta(lookahead)
        return self._client_request("import_wallet_request", body)

    def provision_subaddrs(
        self,
        address: str,
        view_key: str,
        maj_i: int | None = None,
        min_i: int | None = None,
        n_maj: int | None = None,
        n_min: int | None = None,
        get_all: bool | None = None,
    ) -> dict[str, Any]:
        """Request new subaddress ranges be provisioned, starting at the given lower bounds.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param int | None maj_i: major index lower bound (server default `0`).
        :param int | None min_i: minor index lower bound (server default `0`).
        :param int | None n_maj: number of major indices to provision.
        :param int | None n_min: number of minor indices to provision (per major).
        :param bool | None get_all: include all (not just newly provisioned) subaddresses
            in the response (server default `True`).
        :returns dict[str, Any]: `new_subaddrs`, `all_subaddrs`.
        """
        body: dict[str, Any] = {"address": address, "view_key": view_key}
        if maj_i is not None:
            body["maj_i"] = maj_i
        if min_i is not None:
            body["min_i"] = min_i
        if n_maj is not None:
            body["n_maj"] = n_maj
        if n_min is not None:
            body["n_min"] = n_min
        if get_all is not None:
            body["get_all"] = get_all
        return self._client_request("provision_subaddrs", body)

    def submit_raw_tx(self, tx_hex: str) -> str:
        """Relay a raw transaction to the Monero network.

        :param str tx_hex: hex-encoded raw transaction.
        :returns str: the daemon's relay status (typically `"OK"`).
        """
        result = self._client_request("submit_raw_tx", {"tx": tx_hex})
        return result["status"]

    def upsert_subaddrs(
        self,
        address: str,
        view_key: str,
        subaddrs: dict[str, list[list[int]]],
        get_all: bool | None = None,
    ) -> dict[str, Any]:
        """Upsert subaddresses at specific major/minor indexes (idempotent).

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :param dict[str, list[list[int]]] subaddrs: major index (as a string key) mapped to
            a list of `[min, max]` inclusive minor-index ranges.
        :param bool | None get_all: include all (not just upserted) subaddresses in the
            response (server default `True`).
        :returns dict[str, Any]: `new_subaddrs`, `all_subaddrs`.
        """
        body: dict[str, Any] = {"address": address, "view_key": view_key, "subaddrs": subaddrs}
        if get_all is not None:
            body["get_all"] = get_all
        return self._client_request("upsert_subaddrs", body)

    #endregion

    #region Account Administration

    def accept_requests(self, request_type: str, addresses: list[str]) -> list[str]:
        """Accept pending create or import account requests.

        :param str request_type: `"create"` or `"import"`.
        :param list[str] addresses: base58 addresses to accept.
        :returns list[str]: addresses that were updated.
        """
        result = self._request("accept_requests", {"type": request_type, "addresses": addresses})
        return result["updated"]

    def reject_requests(self, request_type: str, addresses: list[str]) -> list[str]:
        """Reject pending create or import account requests.

        :param str request_type: `"create"` or `"import"`.
        :param list[str] addresses: base58 addresses to reject.
        :returns list[str]: addresses that were updated.
        """
        result = self._request("reject_requests", {"type": request_type, "addresses": addresses})
        return result["updated"]

    def add_account(self, address: str, view_key: str) -> list[str]:
        """Add a new account directly, bypassing the `/login` create-request flow.

        :param str address: base58 primary address.
        :param str view_key: hex-encoded private view key for `address`.
        :returns list[str]: addresses that were updated.
        """
        result = self._request("add_account", {"address": address, "key": view_key})
        return result["updated"]

    def list_accounts(self) -> dict[str, list[dict[str, Any]]]:
        """List all accounts by state.

        :returns dict[str, list[dict]]: `{"active": [...], "inactive": [...], "hidden": [...]}`,
            each entry an object with `address`, `scan_height`, and `access_time`.
        """
        return self._request("list_accounts")

    def list_requests(self) -> dict[str, list[dict[str, Any]]]:
        """List all pending create and import account requests.

        :returns dict[str, list[dict]]: `{"create": [...], "import": [...]}`, each entry
            an object with `address` and `start_height`.
        """
        return self._request("list_requests")

    def modify_account_status(self, status: str, addresses: list[str]) -> list[str]:
        """Move account(s) to another state.

        :param str status: `"active"`, `"inactive"`, or `"hidden"`.
        :param list[str] addresses: base58 addresses to modify.
        :returns list[str]: addresses that were updated.
        """
        result = self._request("modify_account_status", {"status": status, "addresses": addresses})
        return result["updated"]

    def rescan(self, height: int, addresses: list[str]) -> list[str]:
        """Force account(s) to rescan from a specific block height.

        :param int height: block height to rescan from.
        :param list[str] addresses: base58 addresses to rescan.
        :returns list[str]: addresses that were updated.
        """
        result = self._request("rescan", {"height": height, "addresses": addresses})
        return result["updated"]

    def validate(self, spend_public_hex: str, view_public_hex: str, view_key_hex: str) -> str:
        """Validate that a spend public key, view public key, and view secret key are consistent,
        and derive the corresponding address.

        :param str spend_public_hex: hex-encoded public spend key.
        :param str view_public_hex: hex-encoded public view key.
        :param str view_key_hex: hex-encoded private view key.
        :returns str: the base58 address derived from the given keys.
        :raises RuntimeError: if the keys are not valid/consistent; identifies the offending field.
        """
        result = self._request("validate", {
            "spend_public_hex": spend_public_hex,
            "view_public_hex": view_public_hex,
            "view_key_hex": view_key_hex,
        })
        if "error" in result:
            error = result["error"]
            raise RuntimeError(f"{error['field']}: {error['details']}")
        return result["address"]

    #endregion

    #region Webhook Administration

    def webhook_add_tx_confirmation(
        self,
        url: str,
        address: str,
        payment_id: str | None = None,
        token: str | None = None,
        confirmations: int | None = None,
    ) -> dict[str, Any]:
        """Register a webhook fired when a transaction to `address` is confirmed.

        :param str url: destination URL, or `"zmq"` to publish over ZMQ PUB/SUB only.
        :param str address: base58 address to watch.
        :param str | None payment_id: optional 8-byte hex payment ID filter.
        :param str | None token: optional token echoed back in the webhook payload.
        :param int | None confirmations: confirmations required before firing (server default 1).
        :returns dict[str, Any]: webhook-value with `event_id`, `payment_id`, `token`,
            `confirmations`, and `url`.
        """
        params: dict[str, Any] = {"type": "tx-confirmation", "url": url, "address": address}
        if payment_id is not None:
            params["payment_id"] = payment_id
        if token is not None:
            params["token"] = token
        if confirmations is not None:
            params["confirmations"] = confirmations
        return self._request("webhook_add", params)

    def webhook_add_tx_spend(
        self,
        url: str,
        address: str,
        payment_id: str | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        """Register a webhook fired when an output belonging to `address` is spent.

        :param str url: destination URL, or `"zmq"` to publish over ZMQ PUB/SUB only.
        :param str address: base58 address to watch.
        :param str | None payment_id: optional 8-byte hex payment ID filter.
        :param str | None token: optional token echoed back in the webhook payload.
        :returns dict[str, Any]: webhook-value with `event_id`, `payment_id`, `token`,
            `confirmations`, and `url`.
        """
        params: dict[str, Any] = {"type": "tx-spend", "url": url, "address": address}
        if payment_id is not None:
            params["payment_id"] = payment_id
        if token is not None:
            params["token"] = token
        return self._request("webhook_add", params)

    def webhook_add_new_account(self, url: str, token: str | None = None) -> dict[str, Any]:
        """Register a webhook fired whenever a new account is created.

        :param str url: destination URL, or `"zmq"` to publish over ZMQ PUB/SUB only.
        :param str | None token: optional token echoed back in the webhook payload.
        :returns dict[str, Any]: webhook-value with `event_id`, `payment_id`, `token`,
            `confirmations`, and `url`.
        """
        params: dict[str, Any] = {"type": "new-account", "url": url}
        if token is not None:
            params["token"] = token
        return self._request("webhook_add", params)

    def webhook_delete(self, addresses: list[str]) -> None:
        """Delete webhooks associated with the given address(es).

        :param list[str] addresses: base58 addresses whose webhooks should be removed.
        """
        self._request("webhook_delete", {"addresses": addresses})

    def webhook_delete_uuid(self, event_ids: list[str]) -> None:
        """Delete webhooks by event UUID.

        :param list[str] event_ids: 16-byte hex event UUIDs to remove.
        """
        self._request("webhook_delete_uuid", {"event_ids": event_ids})

    def webhook_list(self) -> dict[str, Any]:
        """List all registered webhooks.

        :returns dict[str, Any]: `{"webhooks": {...}}`.
        """
        return self._request("webhook_list")

    #endregion
