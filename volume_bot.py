import asyncio
import random
import os
import json
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", "https://api.devnet.solana.com")
TEST_WALLET_PATH = os.path.expanduser("~/.solana/test-wallet.json")
TOKEN_MINT = "5LbmX6E15UQWA2oWUfgM9WBfak2JNLUua2xZtptBTjc5"  # Test SPL token (placeholder)
RAYDIUM_PROGRAM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")  # Raydium program ID

# Load test wallet
try:
    with open(TEST_WALLET_PATH, "r") as f:
        keypair_data = json.load(f)
        if len(keypair_data) != 64:
            raise ValueError("Invalid keypair length")
        keypair = Keypair.from_bytes(bytes(keypair_data))
except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
    print(f"Error loading wallet: {e}")
    exit(1)

async def simulate_trade(client, keypair, is_buy, amount_lamports):
    """Simulate a buy or sell transaction."""
    try:
        transfer_instruction = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=Pubkey.from_string(TOKEN_MINT),  # Placeholder for pool address
                lamports=amount_lamports
            )
        )
        
        tx = Transaction().add(transfer_instruction)
        blockhash_resp = await client.get_latest_blockhash()
        if not blockhash_resp.value:
            raise ValueError("Failed to get blockhash")
        message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[transfer_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash_resp.value.blockhash
        )
        
        async with client:
            response = await client.send_transaction(VersionedTransaction(message, [keypair]))
            print(f"{'Buy' if is_buy else 'Sell'} transaction: {response.value}")
    except Exception as e:
        print(f"Transaction error: {e}")

async def volume_bot():
    """Main bot loop."""
    async with AsyncClient(RPC_ENDPOINT) as client:
        for _ in range(3):  # Simulate 3 trades for testing
            is_buy = random.choice([True, False])
            amount = random.randint(100000, 500000)  # Small amounts for Devnet
            await simulate_trade(client, keypair, is_buy, amount)
            await asyncio.sleep(random.uniform(15, 45))  # Random delay

if __name__ == "__main__":
    asyncio.run(volume_bot())
