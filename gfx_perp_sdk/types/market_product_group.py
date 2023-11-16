# LOCK-BEGIN[imports]: DON'T MODIFY
import gfx_perp_sdk.types as types
from .account_tag import AccountTag
from .bitset import Bitset
from .fractional import Fractional
from .product_array import ProductArray
from .solana_pubkey import Solana_pubkey

from podite import (
    FixedLenArray,
    I16,
    U128,
    U16,
    U64,
    U8,
    pod,
)
from solders.pubkey import Pubkey as PublicKey

# LOCK-END

from typing import Iterable


# LOCK-BEGIN[class(MarketProductGroup)]: DON'T MODIFY
@pod
class MarketProductGroup:
    tag: U64
    name: FixedLenArray[U8, 16]
    authority: Solana_pubkey
    successor: Solana_pubkey
    vault_mint: Solana_pubkey
    collected_fees: Fractional
    fee_collector: Solana_pubkey
    decimals: U64
    risk_engine_program_id: Solana_pubkey
    fee_model_program_id: Solana_pubkey
    fee_model_configuration_acct: Solana_pubkey
    risk_model_configuration_acct: Solana_pubkey
    active_flags_products: Bitset
    ewma_windows: FixedLenArray[U64, 4]
    # market_products: FixedLenArray[U8, 143360]
    market_products: "ProductArray"
    vault_bump: U16
    risk_and_fee_bump: U16
    find_fees_discriminant_len: U16
    validate_account_discriminant_len: U16
    find_fees_discriminant: FixedLenArray[U8, 8]
    validate_account_health_discriminant: FixedLenArray[U8, 8]
    validate_account_liquidation_discriminant: FixedLenArray[U8, 8]
    create_risk_state_account_discriminant: FixedLenArray[U8, 8]
    max_maker_fee_bps: I16
    min_maker_fee_bps: I16
    max_taker_fee_bps: I16
    min_taker_fee_bps: I16
    fee_output_register: Solana_pubkey
    risk_output_register: Solana_pubkey
    sequence_number: U128
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            'tag': int(self.tag),
            'name': bytes(self.name).rstrip(b'\x00').decode('utf-8'),
            'authority': str(PublicKey(self.authority.bytes)),
            'successor': str(PublicKey(self.successor.bytes)),
            'vault_mint': str(PublicKey(self.vault_mint.bytes)),
            'collected_fees': float(self.collected_fees.value),
            'fee_collector': str(PublicKey(self.fee_collector.bytes)),
            'decimals': int(self.decimals),
            'risk_engine_program_id': str(PublicKey(self.risk_engine_program_id.bytes)),
            'fee_model_program_id': str(PublicKey(self.fee_model_program_id.bytes)),
            'fee_model_configuration_acct': str(PublicKey(self.fee_model_configuration_acct.bytes)),
            'risk_model_configuration_acct': str(PublicKey(self.risk_model_configuration_acct.bytes)),
            'active_flags_products': [format(x, '0128b') for x in self.active_flags_products.inner],
            'ewma_windows': [int(x) for x in self.ewma_windows],
            'market_products': self.market_products.to_json(),
            'vault_bump': int(self.vault_bump),
            'risk_and_fee_bump': int(self.risk_and_fee_bump),
            'find_fees_discriminant_len': int(self.find_fees_discriminant_len),
            'validate_account_discriminant_len': int(self.validate_account_discriminant_len),
            'find_fees_discriminant': [int(x) for x in self.find_fees_discriminant],
            'validate_account_health_discriminant': [int(x) for x in self.validate_account_health_discriminant],
            'validate_account_liquidation_discriminant': [int(x) for x in self.validate_account_liquidation_discriminant],
            'create_risk_state_account_discriminant': [int(x) for x in self.create_risk_state_account_discriminant],
            'max_maker_fee_bps': int(self.max_maker_fee_bps),
            'min_maker_fee_bps': int(self.min_maker_fee_bps),
            'max_taker_fee_bps': int(self.max_taker_fee_bps),
            'min_taker_fee_bps': int(self.min_taker_fee_bps),
            'fee_output_register': str(PublicKey(self.fee_output_register.bytes)),
            'risk_output_register': str(PublicKey(self.risk_output_register.bytes)),
            'sequence_number': str(self.sequence_number),
        }

    def active_products(self) -> Iterable["types.Product"]:
        for p in self.market_products.array:
            if p.metadata().product_key != SENTINAL_KEY:
                yield p


SENTINAL_KEY = PublicKey.from_string("11111111111111111111111111111111")
