/**
 * Copyright (c) everoddandeven
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Parts of this file are originally copyright (c) 2025-2026 woodser
 *
 * Parts of this file are originally copyright (c) 2014-2019, The Monero Project
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * All rights reserved.
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of
 *    conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list
 *    of conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be
 *    used to endorse or promote products derived from this software without specific
 *    prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
 * THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Parts of this file are originally copyright (c) 2012-2013 The Cryptonote developers
 */
#pragma once

#include "common/monero_error.h"
#include "daemon/py_monero_daemon.h"
#include "daemon/monero_daemon_rpc.h"
#include "wallet/py_monero_wallet.h"
#include "wallet/monero_wallet_rpc.h"
#include "wallet/monero_wallet_keys.h"
#include "wallet/monero_wallet_full.h"
#include "utils/py_monero_utils.h"

#define MONERO_CATCH_AND_RETHROW(expr)         \
  try {                                        \
    return expr;                               \
  } catch (const monero_rpc_error& e) {        \
    throw;                                     \
  } catch (const monero_error& e) {            \
    throw;                                     \
  }                                            \
  catch (const std::exception& e) {            \
    throw monero_error(e.what());              \
  }

using VectorInt = std::vector<int>;
using VectorUint8 = std::vector<uint8_t>;
using VectorUint32 = std::vector<uint32_t>;
using VectorUint64 = std::vector<uint64_t>;
using VectorString = std::vector<std::string>;

using VectorMoneroOutgoingTransfer = std::vector<std::shared_ptr<monero_outgoing_transfer>>;
using VectorMoneroIncomingTransfer = std::vector<std::shared_ptr<monero_incoming_transfer>>;
using VectorMoneroTx = std::vector<std::shared_ptr<monero_tx>>;
using VectorMoneroTxWallet = std::vector<std::shared_ptr<monero_tx_wallet>>;
using VectorMoneroSubaddress = std::vector<monero_subaddress>;
using VectorMoneroDestination = std::vector<std::shared_ptr<monero_destination>>;


PYBIND11_MAKE_OPAQUE(VectorInt);
PYBIND11_MAKE_OPAQUE(VectorUint8);
PYBIND11_MAKE_OPAQUE(VectorUint32);
PYBIND11_MAKE_OPAQUE(VectorUint64);

/**
 * Holds every pybind11 type handle that must be registered before any
 * method is bound, so classes can reference each other (as base classes
 * or in method signatures) no matter which translation unit ultimately
 * defines their methods. Construction order matches base-before-derived
 * registration order and must not be reordered.
 */
struct PyMoneroTypes {
  py::class_<serializable_struct, std::shared_ptr<serializable_struct>> py_serializable_struct;
  py::class_<monero_rpc_payment_info, serializable_struct, std::shared_ptr<monero_rpc_payment_info>> py_monero_rpc_payment_info;
  py::class_<monero_rpc_connection, serializable_struct, std::shared_ptr<monero_rpc_connection>> py_monero_rpc_connection;

  py::class_<ssl_options, serializable_struct, std::shared_ptr<ssl_options>> py_monero_ssl_options;
  py::class_<monero_version, serializable_struct, std::shared_ptr<monero_version>> py_monero_version;
  py::class_<monero_block_header, serializable_struct, std::shared_ptr<monero_block_header>> py_monero_block_header;
  py::class_<monero_block, monero_block_header, std::shared_ptr<monero_block>> py_monero_block;
  py::class_<monero_tx, serializable_struct, std::shared_ptr<monero_tx>> py_monero_tx;
  py::class_<monero_key_image, serializable_struct, std::shared_ptr<monero_key_image>> py_monero_key_image;
  py::class_<monero_output, serializable_struct, std::shared_ptr<monero_output>> py_monero_output;
  py::class_<monero_wallet_config, serializable_struct, std::shared_ptr<monero_wallet_config>> py_monero_wallet_config;
  py::class_<monero_subaddress, serializable_struct, std::shared_ptr<monero_subaddress>> py_monero_subaddress;
  py::class_<monero_sync_result, serializable_struct, std::shared_ptr<monero_sync_result>> py_monero_sync_result;
  py::class_<monero_account, serializable_struct, std::shared_ptr<monero_account>> py_monero_account;
  py::class_<monero_account_tag, serializable_struct, std::shared_ptr<monero_account_tag>> py_monero_account_tag;
  py::class_<monero_destination, serializable_struct, std::shared_ptr<monero_destination>> py_monero_destination;
  py::class_<monero_transfer, serializable_struct, PyMoneroTransfer, std::shared_ptr<monero_transfer>> py_monero_transfer;
  py::class_<monero_incoming_transfer, monero_transfer, std::shared_ptr<monero_incoming_transfer>> py_monero_incoming_transfer;
  py::class_<monero_outgoing_transfer, monero_transfer, std::shared_ptr<monero_outgoing_transfer>> py_monero_outgoing_transfer;
  py::class_<monero_transfer_query, monero_transfer, std::shared_ptr<monero_transfer_query>> py_monero_transfer_query;
  py::class_<monero_output_wallet, monero_output, std::shared_ptr<monero_output_wallet>> py_monero_output_wallet;
  py::class_<monero_output_query, monero_output_wallet, std::shared_ptr<monero_output_query>> py_monero_output_query;
  py::class_<monero_tx_wallet, monero_tx, std::shared_ptr<monero_tx_wallet>> py_monero_tx_wallet;
  py::class_<monero_tx_query, monero_tx_wallet, std::shared_ptr<monero_tx_query>> py_monero_tx_query;
  py::class_<monero_tx_set, serializable_struct, std::shared_ptr<monero_tx_set>> py_monero_tx_set;
  py::class_<monero_integrated_address,  serializable_struct, std::shared_ptr<monero_integrated_address>> py_monero_integrated_address;
  py::class_<monero_decoded_address, serializable_struct, std::shared_ptr<monero_decoded_address>> py_monero_decoded_address;
  py::class_<monero_tx_config, serializable_struct, std::shared_ptr<monero_tx_config>> py_monero_tx_config;
  py::class_<monero_key_image_export_result, serializable_struct, std::shared_ptr<monero_key_image_export_result>> py_monero_key_image_export_result;
  py::class_<monero_key_image_import_result, serializable_struct, std::shared_ptr<monero_key_image_import_result>> py_monero_key_image_import_result;
  py::class_<monero_message_signature_result,  serializable_struct, std::shared_ptr<monero_message_signature_result>> py_monero_message_signature_result;
  py::class_<monero_check,  serializable_struct, std::shared_ptr<monero_check>> py_monero_check;
  py::class_<monero_check_tx, monero_check, std::shared_ptr<monero_check_tx>> py_monero_check_tx;
  py::class_<monero_check_reserve, monero_check, std::shared_ptr<monero_check_reserve>> py_monero_check_reserve;
  py::class_<monero_multisig_info, serializable_struct, std::shared_ptr<monero_multisig_info>> py_monero_multisig_info;
  py::class_<monero_multisig_init_result, serializable_struct, std::shared_ptr<monero_multisig_init_result>> py_monero_multisig_init_result;
  py::class_<monero_multisig_sign_result, serializable_struct, std::shared_ptr<monero_multisig_sign_result>> py_monero_multisig_sign_result;
  py::class_<monero_address_book_entry, serializable_struct, std::shared_ptr<monero_address_book_entry>> py_monero_address_book_entry;
  py::class_<monero_wallet_listener, PyMoneroWalletListener, std::shared_ptr<monero_wallet_listener>> py_monero_wallet_listener;
  py::class_<monero_daemon_listener, PyMoneroDaemonListener, std::shared_ptr<monero_daemon_listener>> py_monero_daemon_listener;
  py::class_<monero_daemon, std::shared_ptr<monero_daemon>> py_monero_daemon;
  py::class_<monero_daemon_rpc, monero_daemon, std::shared_ptr<monero_daemon_rpc>> py_monero_daemon_rpc;
  py::class_<monero_wallet, PyMoneroWallet, std::shared_ptr<monero_wallet>> py_monero_wallet;
  py::class_<monero_wallet_keys, monero_wallet, std::shared_ptr<monero_wallet_keys>> py_monero_wallet_keys;
  py::class_<monero_wallet_full, monero_wallet, std::shared_ptr<monero_wallet_full>> py_monero_wallet_full;
  py::class_<monero_wallet_rpc, monero_wallet, std::shared_ptr<monero_wallet_rpc>> py_monero_wallet_rpc;
  py::class_<PyMoneroUtils> py_monero_utils;

  py::class_<monero_tx_height_comparator, std::shared_ptr<monero_tx_height_comparator>> py_tx_height_comparator;
  py::class_<monero_incoming_transfer_comparator, std::shared_ptr<monero_incoming_transfer_comparator>> py_incoming_transfer_comparator;
  py::class_<monero_output_comparator, std::shared_ptr<monero_output_comparator>> py_output_comparator;

  explicit PyMoneroTypes(py::module_& m) :
    py_serializable_struct(m, "SerializableStruct"),
    py_monero_rpc_payment_info(m, "MoneroRpcPaymentInfo"),
    py_monero_rpc_connection(m, "MoneroRpcConnection"),
    py_monero_ssl_options(m, "SslOptions"),
    py_monero_version(m, "MoneroVersion"),
    py_monero_block_header(m, "MoneroBlockHeader"),
    py_monero_block(m, "MoneroBlock"),
    py_monero_tx(m, "MoneroTx"),
    py_monero_key_image(m, "MoneroKeyImage"),
    py_monero_output(m, "MoneroOutput"),
    py_monero_wallet_config(m, "MoneroWalletConfig"),
    py_monero_subaddress(m, "MoneroSubaddress"),
    py_monero_sync_result(m, "MoneroSyncResult"),
    py_monero_account(m, "MoneroAccount"),
    py_monero_account_tag(m, "MoneroAccountTag"),
    py_monero_destination(m, "MoneroDestination"),
    py_monero_transfer(m, "MoneroTransfer"),
    py_monero_incoming_transfer(m, "MoneroIncomingTransfer"),
    py_monero_outgoing_transfer(m, "MoneroOutgoingTransfer"),
    py_monero_transfer_query(m, "MoneroTransferQuery"),
    py_monero_output_wallet(m, "MoneroOutputWallet"),
    py_monero_output_query(m, "MoneroOutputQuery"),
    py_monero_tx_wallet(m, "MoneroTxWallet"),
    py_monero_tx_query(m, "MoneroTxQuery"),
    py_monero_tx_set(m, "MoneroTxSet"),
    py_monero_integrated_address(m, "MoneroIntegratedAddress"),
    py_monero_decoded_address(m, "MoneroDecodedAddress"),
    py_monero_tx_config(m, "MoneroTxConfig"),
    py_monero_key_image_export_result(m, "MoneroKeyImageExportResult"),
    py_monero_key_image_import_result(m, "MoneroKeyImageImportResult"),
    py_monero_message_signature_result(m, "MoneroMessageSignatureResult"),
    py_monero_check(m, "MoneroCheck"),
    py_monero_check_tx(m, "MoneroCheckTx"),
    py_monero_check_reserve(m, "MoneroCheckReserve"),
    py_monero_multisig_info(m, "MoneroMultisigInfo"),
    py_monero_multisig_init_result(m, "MoneroMultisigInitResult"),
    py_monero_multisig_sign_result(m, "MoneroMultisigSignResult"),
    py_monero_address_book_entry(m, "MoneroAddressBookEntry"),
    py_monero_wallet_listener(m, "MoneroWalletListener"),
    py_monero_daemon_listener(m, "MoneroDaemonListener"),
    py_monero_daemon(m, "MoneroDaemon"),
    py_monero_daemon_rpc(m, "MoneroDaemonRpc"),
    py_monero_wallet(m, "MoneroWallet"),
    py_monero_wallet_keys(m, "MoneroWalletKeys"),
    py_monero_wallet_full(m, "MoneroWalletFull"),
    py_monero_wallet_rpc(m, "MoneroWalletRpc"),
    py_monero_utils(m, "MoneroUtils"),
    py_tx_height_comparator(m, "TxHeightComparator"),
    py_incoming_transfer_comparator(m, "IncomingTransferComparator"),
    py_output_comparator(m, "OutputComparator")
  {}
};

void py_monero_bind_vectors_and_maps(py::module_& m);
void py_monero_bind_errors_and_enums(py::module_& m);
void py_monero_bind_common(py::module_& m, PyMoneroTypes& t);
void py_monero_bind_daemon(py::module_& m, PyMoneroTypes& t);
void py_monero_bind_wallet(py::module_& m, PyMoneroTypes& t);
void py_monero_bind_utils(py::module_& m, PyMoneroTypes& t);
