# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from io import BytesIO
from podite import BYTES_CATALOG
from solders.pubkey import Pubkey as PublicKey
from solana.transaction import AccountMeta
from solders.instruction import Instruction as TransactionInstruction

from ..utils import to_account_meta
from typing import (
    List,
    Optional,
    Union,
)

# LOCK-END


# LOCK-BEGIN[ix_cls(choose_successor)]: DON'T MODIFY
@dataclass
class ChooseSuccessorIx:
    program_id: PublicKey

    # account metas
    market_product_group: AccountMeta
    authority: AccountMeta
    new_authority: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.market_product_group)
        keys.append(self.authority)
        keys.append(self.new_authority)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CHOOSE_SUCCESSOR))

        return TransactionInstruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(choose_successor)]: DON'T MODIFY
def choose_successor(
    market_product_group: Union[str, PublicKey, AccountMeta],
    authority: Union[str, PublicKey, AccountMeta],
    new_authority: Union[str, PublicKey, AccountMeta],
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[PublicKey] = None,
):
    if program_id is None:
        program_id = PublicKey.from_string(
            "Dex1111111111111111111111111111111111111111")

    if isinstance(market_product_group, (str, PublicKey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(authority, (str, PublicKey)):
        authority = to_account_meta(
            authority,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(new_authority, (str, PublicKey)):
        new_authority = to_account_meta(
            new_authority,
            is_signer=False,
            is_writable=False,
        )

    return ChooseSuccessorIx(
        program_id=program_id,
        market_product_group=market_product_group,
        authority=authority,
        new_authority=new_authority,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
