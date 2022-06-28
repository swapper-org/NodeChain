#!/usr/bin/python3
COIN_SYMBOL = "bch"

GET_ADDRESS_HISTORY_METHOD = "getaddresshistory"
GET_ADDRESS_BALANCE_METHOD = "getaddressbalance"
GET_ADDRESS_UNSPENT_METHOD = "getaddressunspent"
GET_BLOCK_METHOD = "getblock"
GET_BLOCK_HASH_METHOD = "getblockhash"
GET_BLOCK_COUNT_METHOD = "getblockcount"
ESTIMATE_SMART_FEE_METHOD = "estimatesmartfee"
GET_ADDRESSES_UNSPENT = "getaddressesunspent"
GET_TRANSACTION_METHOD = "gettransaction"
DECODE_RAW_TRANSACTION_METHOD = "decoderawtransaction"
SEND_RAW_TRANSACTION_METHOD = "sendrawtransaction"
NOTIFY_METHOD = "notify"
GET_BLOCKCHAIN_INFO = "getblockchaininfo"
SYNCING = "syncing"

BCH_PRECISION = 8

VERBOSITY_LESS_MODE = 0
VERBOSITY_DEFAULT_MODE = 1
VERBOSITY_MORE_MODE = 2

RPC_JSON_SCHEMA_FOLDER = "bch/rpcschemas/"
WS_JSON_SCHEMA_FOLDER = "bch/wsschemas/"
SCHEMA_CHAR_SEPARATOR = "_"
REQUEST = "request"
RESPONSE = "response"
SCHEMA_EXTENSION = ".json"
BROADCAST_TRANSACTION = "broadcasttransaction"
GET_ADDRESS_BALANCE = "getaddressbalance"
GET_ADDRESSES_BALANCE = "getaddressesbalance"
GET_ADDRESS_HISTORY = "getaddresshistory"
GET_ADDRESS_UNSPENT = "getaddressunspent"
GET_BLOCK_BY_HASH = "getblockbyhash"
GET_BLOCK_BY_NUMBER = "getblockbynumber"
GET_FEE_PER_BYTE = "getfeeperbyte"
GET_HEIGHT = "getheight"
GET_PENDING_TRANSACTION_COUNT = "getpendingtransactioncount"
GET_TRANSACTION = "gettransaction"
GET_ADDRESS_TRANSACTION_COUNT = "getaddresstransactioncount"
GET_ADDRESSES_TRANSACTION_COUNT = "getaddressestransactioncount"
GET_TRANSACTION_HEX = "gettransactionhex"
GET_ADDRESSES_HISTORY = "getaddresseshistory"
NOTIFY = "notify"

SUBSCRIBE_ADDRESS_BALANCE = "subscribetoaddressbalance"
UNSUBSCRIBE_ADDRESS_BALANCE = "unsubscribefromaddressbalance"
