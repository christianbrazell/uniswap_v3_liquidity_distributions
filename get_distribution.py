import os
import argparse
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from utils.subgraph import *
from utils.uniswap import *
from utils.market import *

url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3?source=uniswap" # Subgraph URL
default_pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"  # Default USDC/ETH 0.05%
default_surrounding_ticks = 300  # How many ticks on either side of active tick to query

# Load subgraph queries
pool_query_path = os.path.join('subgraph_queries', 'pool_query.txt')
tick_query_path = os.path.join('subgraph_queries', 'tick_query.txt')

with open(pool_query_path, 'r') as file:
    pool_query = file.read()

with open(tick_query_path, 'r') as file:
    tick_query = file.read()

if __name__ == "__main__":

    # Set query parameters from command line
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--pool_id', type=str, help='ID of the pool', default=default_pool_address)
    parser.add_argument('--surround_ticks', type=int, help='Number of surround ticks',
                        default=default_surrounding_ticks)

    args = parser.parse_args()
    pool_address = args.pool_id
    surrounding_ticks = default_surrounding_ticks

    # Get pool data
    pool_data_payload = {
        "variables": {
            "poolAddress": pool_address
        },
        "query": pool_query
    }

    pool_response = submit_payload(url, pool_data_payload)
    pool_data = pool_response.json()['data']['pool']
    pool = Pool(pool_data)

    # Get lower and upper tick bounds for analysis
    tick_lower_bound = pool.active_tick_lower - pool.tick_spacing * surrounding_ticks
    tick_upper_bound = pool.active_tick_lower + pool.tick_spacing * surrounding_ticks

    # Get tick data
    tick_data_payload = {
        "variables": {
            "poolAddress": pool_address,
            "skip": 0,
            "tickIdxLowerBound": tick_lower_bound,
            "tickIdxUpperBound": tick_upper_bound
        },
        "query": tick_query
    }

    tick_response = submit_payload(url, tick_data_payload)
    tick_data = tick_response.json()['data']['ticks']

    # Process ticks
    tick_df = pd.DataFrame(tick_data, dtype=float)
    tick_df['cumulative_liquidityNet'] = tick_df['liquidityNet'].cumsum()

    # Calculate liquidity at each tick
    # First, find the difference between liquidity and cumulative liquidityNet at active tick
    active_tick_df = tick_df.loc[tick_df.tickIdx == pool.active_tick_lower]
    liquidity_offset = pool.liquidity - active_tick_df.cumulative_liquidityNet.values[0]

    # Now add this offset to all ticks net liquidity to get their liquidity
    tick_df['liquidity'] = tick_df.cumulative_liquidityNet + liquidity_offset

    # Convert liquidity into real token amounts
    # First, set the lower and upper ticks for the liquidity ranges
    tick_df['tick_upper'] = tick_df.tickIdx
    tick_df['tick_lower'] = tick_df.tickIdx - pool.tick_spacing

    # Second, process the LP amounts tick by tick
    token_amount_0_list = []
    token_amount_1_list = []
    for (index, row) in tick_df.iterrows():
        amount_0, amount_1 = process_tick(row, pool)
        token_amount_0_list.append(amount_0)
        token_amount_1_list.append(amount_1)

    tick_df['amount_0'] = token_amount_0_list
    tick_df['amount_1'] = token_amount_1_list

    # Convert token amounts to token_0 prices and aggregate
    tick_df['amount_1_adj'] = tick_df.amount_1 * pool.active_tick_price
    tick_df['amount'] = tick_df.amount_0 + tick_df.amount_1_adj

    # Include price at each tick, for reference
    tick_df['price'] = tick_to_adjusted_price(tick_df['tickIdx'], pool.token_0, pool.token_1)

    # Add lp distribution to pool object
    pool.lp = tick_df[['price', 'amount', 'amount_0', 'amount_1', 'amount_1_adj']]

    # Plot
    plt.style.use("dark_background")
    plt.figure(figsize=(10, 8), dpi=100)  # 80)

    sns.lineplot(data=pool.lp, x="price", y="amount")
    plt.fill_between(x=pool.lp['price'], y1=pool.lp['amount'], alpha=0.3)
    plt.axvline(x=pool.active_tick_price, color='red', linestyle='--')

    plt.title(f"Liquidity Distribution, UniswapV3 {pool.token_0.symbol}/{pool.token_1.symbol} {pool.fee_tier}")
    plt.xlabel(f"Price [{pool.token_0.symbol}]")
    plt.ylabel(f"Liquidity in Tick [{pool.token_0.symbol}]")
    plt.grid(alpha=0.2)
    plt.show()