#!/usr/bin/python3
COIN_SYMBOL = "btc"

GET_HISTORY_METHOD = "blockchain.scripthash.get_history"
GET_BALANCE_METHOD = "blockchain.scripthash.get_balance"
LIST_UNSPENT_METHOD = "blockchain.scripthash.listunspent"
GET_BLOCK_METHOD = "getblock"
GET_BLOCK_HASH_METHOD = "getblockhash"
GET_BLOCK_COUNT_METHOD = "getblockcount"
ESTIMATE_SMART_FEE_METHOD = "estimatesmartfee"
GET_RAW_TRANSACTION_METHOD = "getrawtransaction"
DECODE_RAW_TRANSACTION_METHOD = "decoderawtransaction"
SEND_RAW_TRANSACTION_METHOD = "sendrawtransaction"
NOTIFY_METHOD = "notify"
GET_BLOCKCHAIN_INFO = "getblockchaininfo"
SYNCING = "syncing"

BTC_PRECISION = 8

VERBOSITY_LESS_MODE = 0
VERBOSITY_DEFAULT_MODE = 1
VERBOSITY_MORE_MODE = 2

ADDR_BALANCE_CALLBACK_NAME = "addressBalance"

RPC_JSON_SCHEMA_FOLDER = "btc/rpcschemas/"
WS_JSON_SCHEMA_FOLDER = "btc/wsschemas/"
SCHEMA_CHAR_SEPARATOR = "_"
REQUEST = "request"
RESPONSE = "response"
SCHEMA_EXTENSION = ".json"
BROADCAST_TRANSACTION = "broadcasttransaction"
GET_ADDRESS_BALANCE = "getaddressbalance"
GET_ADDRESSES_BALANCE = "getaddressesbalance"
GET_ADDRESS_HISTORY = "getaddresshistory"
GET_ADDRESS_UNSPENT = "getaddressunspent"
GET_ADDRESSES_UNSPENT = "getaddressesunspent"
GET_BLOCK_BY_HASH = "getblockbyhash"
GET_BLOCK_BY_NUMBER = "getblockbynumber"
GET_FEE_PER_BYTE = "getfeeperbyte"
GET_HEIGHT = "getheight"
GET_PENDING_TRANSACTION_COUNT = "getpendingtransactioncount"
GET_TRANSACTION = "gettransaction"
GET_TRANSACTIONS = "gettransactions"
GET_ADDRESS_TRANSACTION_COUNT = "getaddresstransactioncount"
GET_ADDRESSES_TRANSACTION_COUNT = "getaddressestransactioncount"
GET_TRANSACTION_HEX = "gettransactionhex"
GET_ADDRESSES_HISTORY = "getaddresseshistory"
NOTIFY = "notify"
NEW_HASH_BLOCK_ZMQ_TOPIC = "hashblock"
NEW_RAW_BLOCK_ZMQ_TOPIC = "rawblock"
GET_BLOCK = "getblock"

SUBSCRIBE_ADDRESS_BALANCE = "subscribetoaddressbalance"
UNSUBSCRIBE_ADDRESS_BALANCE = "unsubscribefromaddressbalance"
SUBSCRIBE_TO_NEW_BLOCKS = "subscribetonewblocks"
UNSUBSCRIBE_FROM_NEW_BLOCKS = "unsubscribefromnewblocks"

INVALID_ADDRESS_ERROR = "Invalid address"
