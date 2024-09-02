import base58, base64, asyncio
import json

from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed

from jupiter_python_sdk.jupiter import Jupiter, Jupiter_DCA


# network endpoint
rpc_endpoint = "https://api.mainnet-beta.solana.com"  # mainnet

async def execute_swap(token_to_buy: str, amount: int | float, slippage: int | float, user_key: str):
    try:
        private_key = Keypair.from_bytes(base58.b58decode(user_key)) # Private key as string

        print(private_key.pubkey())

        async_client = AsyncClient(rpc_endpoint)
        jupiter = Jupiter(async_client, private_key)

        # balance 
        bal = await async_client.get_balance(private_key.pubkey())
        print(bal)

        """
        EXECUTE A SWAP
        """
        transaction_data = await jupiter.swap(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint=token_to_buy,
            amount=int(amount * 1_000_000),
            slippage_bps=slippage,
        )
        # Returns str: serialized transactions to execute the swap.

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
        
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
    except Exception as a:
        print("execute swap:", a)


# sol value to trade:eg 1, 0.4, 0.008
amount = 0.5

# mint to trade, maybe wif, doge etc
token_to_buy = 'CLoUDKc4Ane7HeQcPpE3YHnznRxhMimJ4MyaUqyHFzAu'

user_key = 'private key of user who wants to trade'

asyncio.run(execute_swap(token_to_buy, amount, 1, user_key))
