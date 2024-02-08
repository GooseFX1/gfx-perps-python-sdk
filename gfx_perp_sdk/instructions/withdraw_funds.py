# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from ..types import WithdrawFundsParams
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


# LOCK-BEGIN[ix_cls(withdraw_funds)]: DON'T MODIFY
@dataclass
class WithdrawFundsIx:
    program_id: PublicKey

    # account metas
    token_program: AccountMeta
    buddy_link_program: AccountMeta
    user: AccountMeta
    user_token_account: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    market_product_group_vault: AccountMeta
    risk_engine_program: AccountMeta
    risk_model_configuration_acct: AccountMeta
    risk_output_register: AccountMeta
    trader_risk_state_acct: AccountMeta
    risk_signer: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: WithdrawFundsParams

    def to_instruction(self):
        keys = []
        keys.append(self.token_program)
        keys.append(self.buddy_link_program)
        keys.append(self.user)
        keys.append(self.user_token_account)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.market_product_group_vault)
        keys.append(self.risk_engine_program)
        keys.append(self.risk_model_configuration_acct)
        keys.append(self.risk_output_register)
        keys.append(self.trader_risk_state_acct)
        keys.append(self.risk_signer)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.WITHDRAW_FUNDS))
        buffer.write(BYTES_CATALOG.pack(WithdrawFundsParams, self.params))

        return TransactionInstruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(withdraw_funds)]: DON'T MODIFY
def withdraw_funds(
    user: Union[str, PublicKey, AccountMeta],
    buddy_link_program: Union[str, PublicKey, AccountMeta],
    user_token_account: Union[str, PublicKey, AccountMeta],
    trader_risk_group: Union[str, PublicKey, AccountMeta],
    market_product_group: Union[str, PublicKey, AccountMeta],
    market_product_group_vault: Union[str, PublicKey, AccountMeta],
    risk_engine_program: Union[str, PublicKey, AccountMeta],
    risk_model_configuration_acct: Union[str, PublicKey, AccountMeta],
    risk_output_register: Union[str, PublicKey, AccountMeta],
    trader_risk_state_acct: Union[str, PublicKey, AccountMeta],
    risk_signer: Union[str, PublicKey, AccountMeta],
    params: WithdrawFundsParams,
    program_id: Union[str, PublicKey, AccountMeta],
    remaining_accounts: List[PublicKey],
    token_program: Union[str, PublicKey, AccountMeta] = PublicKey.from_string(
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),

):
    if isinstance(token_program, (str, PublicKey)):
        token_program = to_account_meta(
            token_program,
            is_signer=False,
            is_writable=False,
        )

    if isinstance(buddy_link_program, (str, PublicKey)):
        buddy_link_program = to_account_meta(
            buddy_link_program,
            is_signer=False,
            is_writable=False,
        )

    if isinstance(user, (str, PublicKey)):
        user = to_account_meta(
            user,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(user_token_account, (str, PublicKey)):
        user_token_account = to_account_meta(
            user_token_account,
            is_signer=False,
            is_writable=True,
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
    if isinstance(market_product_group_vault, (str, PublicKey)):
        market_product_group_vault = to_account_meta(
            market_product_group_vault,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_engine_program, (str, PublicKey)):
        risk_engine_program = to_account_meta(
            risk_engine_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_model_configuration_acct, (str, PublicKey)):
        risk_model_configuration_acct = to_account_meta(
            risk_model_configuration_acct,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_output_register, (str, PublicKey)):
        risk_output_register = to_account_meta(
            risk_output_register,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(trader_risk_state_acct, (str, PublicKey)):
        trader_risk_state_acct = to_account_meta(
            trader_risk_state_acct,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_signer, (str, PublicKey)):
        risk_signer = to_account_meta(
            risk_signer,
            is_signer=False,
            is_writable=False,
        )
    remaining_metas: List[AccountMeta] = []
    for accounts in remaining_accounts:
        if isinstance(accounts, (str, PublicKey)):
            account = to_account_meta(
                accounts,
                is_signer=False,
                is_writable=False,
            )
            remaining_metas.append(account)

    return WithdrawFundsIx(
        program_id=program_id,
        token_program=token_program,
        buddy_link_program=buddy_link_program,
        user=user,
        user_token_account=user_token_account,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        market_product_group_vault=market_product_group_vault,
        risk_engine_program=risk_engine_program,
        risk_model_configuration_acct=risk_model_configuration_acct,
        risk_output_register=risk_output_register,
        trader_risk_state_acct=trader_risk_state_acct,
        risk_signer=risk_signer,
        remaining_accounts=remaining_metas,
        params=params,
    ).to_instruction()

# LOCK-END
