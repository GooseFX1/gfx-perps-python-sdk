# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from io import BytesIO
from solders.pubkey import Pubkey as PublicKey
from solana.transaction import AccountMeta
from solders.instruction import Instruction as TransactionInstruction

from ..utils import to_account_meta
from typing import Union

# LOCK-END


# LOCK-BEGIN[ix_cls(close_trader_risk_group)]: DON'T MODIFY
@dataclass
class CloseTraderRiskGroupIx:
    program_id: PublicKey

    # account metas
    owner: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    system_program: AccountMeta
    
    def to_instruction(self):
        keys = []
        keys.append(self.owner)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.system_program)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CLOSE_TRADER_RISK_GROUP))

        return TransactionInstruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(close_trader_risk_group)]: DON'T MODIFY
def close_trader_risk_group(
    owner: Union[str, PublicKey, AccountMeta],
    trader_risk_group: Union[str, PublicKey, AccountMeta],
    market_product_group: Union[str, PublicKey, AccountMeta],
    system_program: Union[str, PublicKey, AccountMeta],
    program_id: PublicKey,
):

    if isinstance(owner, (str, PublicKey)):
        owner = to_account_meta(
            owner,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(trader_risk_group, (str, PublicKey)):
        trader_risk_group = to_account_meta(
            trader_risk_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_product_group, (str, PublicKey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(system_program, (str, PublicKey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
        )
    return CloseTraderRiskGroupIx(
        program_id=program_id,
        owner=owner,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        system_program=system_program,
    ).to_instruction()

# LOCK-END
