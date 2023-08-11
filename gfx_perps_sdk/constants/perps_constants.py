from typing import List, TypedDict
from solana.publickey import PublicKey

Network = TypedDict("Network", {"MAINNET": dict, "DEVNET": dict})

ADDRESSES: Network = {
    "MAINNET": {
        "MPG_ID": PublicKey("E9xDgYChJ6QP5xGRwoU6FtjWDXsnmoYu3DWECUU2fXAp"),
        "DEX_ID": PublicKey("BjpU1ACJY2bFj7aVTiMJLhM7H1ePxwkfDhjyY9dW9dbo"),
        "INSTRUMENTS_ID": PublicKey("VXD2JfYWTiLuQLZA4jXN58cCxQe1XhaquNHAA1FEDWW"),
        "FEES_ID": PublicKey("2o2VABUDicRrLSzb5U4VvBrnVbtnDdCMowrMg9x7RGnD"),
        "RISK_ID": PublicKey("GW31SEFBLtoEhBYFJi2KUdmdnBG4xapjE7ARBWB5MQT2"),
        "ORDERBOOK_P_ID": PublicKey("Cet4WZvLjJJFfPCfFsGjH8aHHCLgoUWWYXXunf28eAFT"),
        "PYTH_MAINNET": PublicKey("H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG"),
        "PYTH_DEVNET": PublicKey("J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix"),
        "PRODUCTS": [
            {
                "name": "SOL-PERP",
                "PRODUCT_ID": PublicKey("ExyWP65F2zsALQkC2wSQKfR7vrXyPWAG4SLWExVzgbaW"),
                "ORDERBOOK_ID": PublicKey("Ggw9mU8vfP3NucANaPJBZSZMRSiMPrsvFmxj5wM3qvn3"),
                "BIDS": PublicKey("DmB2CBjeLAh6awvWvySuygSom1JHdT95ZVEQmZF4TBXD"),
                "ASKS": PublicKey("FPTSdA4vPQRz4KyjKi5YYdNNq9EbKDSgKMNyadrbVhG8"),
                "EVENT_QUEUE": PublicKey("2Kv94KZTX8yePkdNZT1zXpzDaTpLYLpeiv7Gp8vLA6kL"),
                "tick_size": 100,
                "decimals": 5
            }
        ],
        "VAULT_MINT": PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        "VAULT_SEED": "market_vault",
        "FEES_SEED": "fee_model_config_acct",
        "TRADER_FEE_ACCT_SEED": "trader_fee_acct",
        "BUDDY_LINK_PROGRAM": PublicKey("BUDDYtQp7Di1xfojiCSVDksiYLQx511DPdj2nbtG9Yu5")
    },
    "DEVNET": {
        "MPG_ID": PublicKey("BFqj3JFXV92vrBLhmXnLM2Dkkg9VJN6k8NbGoTxxeiUv"),
        "DEX_ID": PublicKey("BjpU1ACJY2bFj7aVTiMJLhM7H1ePxwkfDhjyY9dW9dbo"),
        "INSTRUMENTS_ID": PublicKey("VXD2JfYWTiLuQLZA4jXN58cCxQe1XhaquNHAA1FEDWW"),
        "FEES_ID": PublicKey("2o2VABUDicRrLSzb5U4VvBrnVbtnDdCMowrMg9x7RGnD"),
        "RISK_ID": PublicKey("GW31SEFBLtoEhBYFJi2KUdmdnBG4xapjE7ARBWB5MQT2"),
        "ORDERBOOK_P_ID": PublicKey("Cet4WZvLjJJFfPCfFsGjH8aHHCLgoUWWYXXunf28eAFT"),
        "PYTH_MAINNET": PublicKey("H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG"),
        "PYTH_DEVNET": PublicKey("J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix"),
        "PRODUCTS": [
            {
                "name": "SOL-PERP",
                "PRODUCT_ID": PublicKey("n3Lx4oVjUN1XAD6GMB9PLLhX9W7TPakdzW461mhF95u"),
                "ORDERBOOK_ID": PublicKey("3RPexPyzUBQ2iamwr4CfTc37we4dgYNn2CkP4Bn8WbZT"),
                "BIDS": PublicKey("7HAA7GWvhZCeXe2pheowgMox66Mh2fQQ6S2ZB9yha7cU"),
                "ASKS": PublicKey("9PeKnBnyBZRK5Ys6PyR4upP2861bU55VGB59wfSUAczS"),
                "EVENT_QUEUE": PublicKey("HJRax1uuCxs1hDzSyZveZ6eYx5h5UEbypTMrQ1AoWpjo"),
                "tick_size": 100,
                "decimals": 7
            }
        ],
        "VAULT_MINT": PublicKey("3Q6dz8cLd4BW1kyuGyUaS7qhTtFP7tGS55Y7fybCUfNy"),
        "VAULT_SEED": "market_vault",
        "FEES_SEED": "fee_model_config_acct",
        "TRADER_FEE_ACCT_SEED": "trader_fee_acct",
        "BUDDY_LINK_PROGRAM": PublicKey("9zE4EQ5tJbEeMYwtS2w8KrSHTtTW4UPqwfbBSEkUrNCA")
    }
}

API_BASE = "https://api-services.goosefx.io"

TRADE_HISTORY = "/perps-apis/getTradeHistory"
