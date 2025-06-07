import asyncio
import random
import os
import json
import logging
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse
from solders.message import MessageV0
from solders.transaction import VersionedTransaction, Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", "https://api.devnet.solana.com")
TEST_WALLET_PATH = os.path.expanduser("~/.solana/test-wallet.json")
TOKEN_MINT = "5LbmX6E15UQWA2oWUfgM9WBfak2JNLUua2xZtptBTjc5"  # Your wallet pubkey for testing
RAYDIUM_PROGRAM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")  # Raydium program ID
MIN_LAMPORTS = 100000  # 0.0001 SOL
MAX_LAMPORTS = 500000  # 0.0005 SOL
MIN_DELAY = 15  # seconds
MAX_DELAY = 45  # seconds
NUM_TRADES = 3
MIN_BALANCE_LAMPORTS = 1000000  # 0.001 SOL for fees

# Load test wallet
try:
    with open(TEST_WALLET_PATH, "r") as f:
        keypair_data = json.load(f)
        if len(keypair_data) != 64:
            raise ValueError("Invalid keypair length")
        keypair = Keypair.from_bytes(bytes(keypair_data))
    logger.info(f"Loaded wallet: {keypair.pubkey()}")
except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
    logger.error(f"Error loading wallet: {e}")
    exit(1)

async def check_rpc_connection(client: AsyncClient) -> bool:
    """Check if RPC endpoint is responsive."""
    try:
        await client.is_connected()
        logger.info(f"Connected to RPC: {RPC_ENDPOINT}")
        return True
    except Exception as e:
        logger.error(f"RPC connection failed: {e}")
        return False

async def check_balance(client: AsyncClient, pubkey: Pubkey) -> int:
    """Check wallet balance in lamports."""
    try:
        response: RPCResponse = await client.get_balance(pubkey)
        balance = response.value
        logger.info(f"Wallet balance: {balance} lamports")
        return balance
    except Exception as e:
        logger.error(f"Balance check failed: {e}")
        return 0

async def simulate_trade(client: AsyncClient, keypair: Keypair, is_buy: bool, amount_lamports: int):
    """Simulate a buy or sell transaction (uses SOL transfer for POC)."""
    try:
        # Check balance before transaction
        balance = await check_balance(client, keypair.pubkey())
        if balance < amount_lamports + MIN_BALANCE_LAMPORTS:
            logger.error(f"Insufficient balance: {balance} lamports, need {amount_lamports + MIN_BALANCE_LAMPORTS}")
            return

        # Create transfer instruction
        # Note: For Raydium, replace with swap instruction using AMM pool
        transfer_instruction = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=Pubkey.from_string(TOKEN_MINT),
                lamports=amount_lamports
            )
        )

        # Get recent blockhash
        blockhash_resp = await client.get_latest_blockhash()
        if not blockhash_resp.value:
            logger.error("Failed to get blockhash")
            return
        recent_blockhash = blockhash_resp.value.blockhash

        # Compile transaction message
        message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[transfer_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash
        )

        # Create and sign transaction
        tx = VersionedTransaction(message, [keypair])

        # Send transaction
        async with client:
            response = await client.send_transaction(tx)
            logger.info(f"{'Buy' if is_buy else 'Sell'} transaction: {response.value}")
    except Exception as e:
        logger.error(f"Transaction error: {e}")

async def volume_bot():
    """Main bot loop."""
    async with AsyncClient(RPC_ENDPOINT) as client:
        if not await check_rpc_connection(client):
            logger.error("Aborting due to RPC connection failure")
            return
        
        for i in range(NUM_TRADES):
            is_buy = random.choice([True, False])
            amount = random.randint(MIN_LAMPORTS, MAX_LAMPORTS)
            logger.info(f"Executing trade {i+1}/{NUM_TRADES}: {'Buy' if is_buy else 'Sell'} {amount} lamports")
            await simulate_trade(client, keypair, is_buy, amount)
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            logger.info(f"Waiting {delay:.2f} seconds before next trade")
            await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(volume_bot())
