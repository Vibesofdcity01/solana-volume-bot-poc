Solana Volume Bot POC
Proof of Concept for a Solana-py SDK-based volume bot simulating organic trading activity on Raydium.
Features

Randomized buy/sell transactions with configurable parameters.
Connects to Solana Devnet via RPC endpoint.
Simulates natural trading behavior.

Setup

Install dependencies:pip3 install solana==0.36.7 aiohttp python-dotenv solders --index-url https://pypi.org/simple


Configure Solana wallet in ~/.solana/test-wallet.json.
Set up .env:echo "RPC_ENDPOINT=https://api.devnet.solana.com" > .env


Run the bot:python3 volume_bot.py



Notes

Uses simplified SOL transfers for demo; full Raydium integration for production.
Requires SOL in test wallet (use solana airdrop 1).
Network issues? Check DNS (nameserver 8.8.8.8 in /etc/resolv.conf).

