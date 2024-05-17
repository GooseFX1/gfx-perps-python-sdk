from typing import List, TypedDict
from solders.pubkey import Pubkey as PublicKey

TOKEN_PROGRAM_ID = PublicKey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

Network = TypedDict("Network", {"MAINNET": dict, "DEVNET": dict})

ADDRESSES: Network = {
    "MAINNET": {
        "MPG_ID": PublicKey.from_string("E9xDgYChJ6QP5xGRwoU6FtjWDXsnmoYu3DWECUU2fXAp"),
        "DEX_ID": PublicKey.from_string("BjpU1ACJY2bFj7aVTiMJLhM7H1ePxwkfDhjyY9dW9dbo"),
        "INSTRUMENTS_ID": PublicKey.from_string("VXD2JfYWTiLuQLZA4jXN58cCxQe1XhaquNHAA1FEDWW"),
        "FEES_ID": PublicKey.from_string("2o2VABUDicRrLSzb5U4VvBrnVbtnDdCMowrMg9x7RGnD"),
        "RISK_ID": PublicKey.from_string("GW31SEFBLtoEhBYFJi2KUdmdnBG4xapjE7ARBWB5MQT2"),
        "ORDERBOOK_P_ID": PublicKey.from_string("Cet4WZvLjJJFfPCfFsGjH8aHHCLgoUWWYXXunf28eAFT"),
        "PYTH_MAINNET": PublicKey.from_string("H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG"),
        "PYTH_DEVNET": PublicKey.from_string("J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix"),
        "PRODUCTS": [
            {
                "name": "SOL-PERP",
                "PRODUCT_ID": PublicKey.from_string("ExyWP65F2zsALQkC2wSQKfR7vrXyPWAG4SLWExVzgbaW"),
                "ORDERBOOK_ID": PublicKey.from_string("Ggw9mU8vfP3NucANaPJBZSZMRSiMPrsvFmxj5wM3qvn3"),
                "BIDS": PublicKey.from_string("DmB2CBjeLAh6awvWvySuygSom1JHdT95ZVEQmZF4TBXD"),
                "ASKS": PublicKey.from_string("FPTSdA4vPQRz4KyjKi5YYdNNq9EbKDSgKMNyadrbVhG8"),
                "EVENT_QUEUE": PublicKey.from_string("2Kv94KZTX8yePkdNZT1zXpzDaTpLYLpeiv7Gp8vLA6kL"),
                "tick_size": 100,
                "decimals": 7
            }
        ],
        "VAULT_MINT": PublicKey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        "VAULT_SEED": "market_vault",
        "FEES_SEED": "fee_model_config_acct",
        "TRADER_FEE_ACCT_SEED": "trader_fee_acct",
        "BUDDY_LINK_PROGRAM": PublicKey.from_string("BUDDYtQp7Di1xfojiCSVDksiYLQx511DPdj2nbtG9Yu5")
    },
    "DEVNET": {
        "MPG_ID": PublicKey.from_string("GSiRLUGwJsPn3RVozE6auGyTMZ8cg9c7HnAtTKzeb4Z8"),
        "DEX_ID": PublicKey.from_string("BjpU1ACJY2bFj7aVTiMJLhM7H1ePxwkfDhjyY9dW9dbo"),
        "INSTRUMENTS_ID": PublicKey.from_string("VXD2JfYWTiLuQLZA4jXN58cCxQe1XhaquNHAA1FEDWW"),
        "FEES_ID": PublicKey.from_string("2o2VABUDicRrLSzb5U4VvBrnVbtnDdCMowrMg9x7RGnD"),
        "RISK_ID": PublicKey.from_string("GW31SEFBLtoEhBYFJi2KUdmdnBG4xapjE7ARBWB5MQT2"),
        "ORDERBOOK_P_ID": PublicKey.from_string("Cet4WZvLjJJFfPCfFsGjH8aHHCLgoUWWYXXunf28eAFT"),
        "PYTH_MAINNET": PublicKey.from_string("H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG"),
        "PYTH_DEVNET": PublicKey.from_string("J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix"),
        "PRODUCTS": [
            {
                "name": "SOL-PERP",
                "PRODUCT_ID": PublicKey.from_string("DUCFhVbomXJHZFJPdgYEQVtBGfADon9qDMTE2hbnzi26"),
                "ORDERBOOK_ID": PublicKey.from_string("7xiz1kHfapP65m5dYjgt2uVV7RqBFcFa3kxvqrRTGjz3"),
                "BIDS": PublicKey.from_string("DP5fvyaV8bDGTTntrqFjZ2Z1xek21z16x8KfhBsrCTBb"),
                "ASKS": PublicKey.from_string("DJkXtHhwzRiwpz3oDu3SJbj3VPHTHhiLjqqBQM5FtSBj"),
                "EVENT_QUEUE": PublicKey.from_string("Aj7T65BVGVHSfcKv3A52ZG8y6FQiEMUSipgyCHbosAZN"),
                "tick_size": 100,
                "decimals": 7
            }
        ],
        "VAULT_MINT": PublicKey.from_string("Bg2f3jstf2Co4Hkrxsn7evzvRwLbWYmuzaLUPGnjCwAA"),
        "VAULT_SEED": "market_vault",
        "FEES_SEED": "fee_model_config_acct",
        "TRADER_FEE_ACCT_SEED": "trader_fee_acct",
        "BUDDY_LINK_PROGRAM": PublicKey.from_string("9zE4EQ5tJbEeMYwtS2w8KrSHTtTW4UPqwfbBSEkUrNCA")
    }
}
MINT_DECIMALS = 6

API_BASE = "https://api-services.goosefx.io"

TRADE_HISTORY = "/perps-apis/getTradeHistory"
