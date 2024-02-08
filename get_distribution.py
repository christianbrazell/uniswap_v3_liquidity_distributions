import math
import os

from utils.subgraph import *
from utils.uniswap import *


url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3?source=uniswap"

pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
price_fixed_digits = 4
default_surround_ticks = 300

num_surround_ticks = default_surround_ticks


if __name__=="__main__":

    # Load subgraph queries
    pool_query_path = os.path.join('subgraph_queries', 'pool_query.txt')
    tick_query_path = os.path.join('subgraph_queries', 'tick_query.txt')

    with open(pool_query_path, 'r') as file:
        pool_query = file.read()

    with open(tick_query_path, 'r') as file:
        tick_query = file.read()

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
    tick_lower_bound = pool.active_tick_lower - pool.tick_spacing * num_surround_ticks
    tick_upper_bound = pool.active_tick_lower + pool.tick_spacing * num_surround_ticks

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
    tick_df = pd.DataFrame(tick_data)
    for col in tick_df.columns:
        tick_df[col] = pd.to_numeric(tick_df[col], errors='coerce', downcast='float')
    tick_df['price'] = tick_to_adjusted_price(tick_df['tickIdx'], pool.token_0, pool.token_1)
    tick_df['cumulative_liquidityNet'] = tick_df['liquidityNet'].cumsum()

    active_tick_df = tick_df.loc[tick_df.tickIdx==pool.active_tick_lower]
    liquidity_offset = pool.liquidity - active_tick_df.cumulative_liquidityNet.values[0]
    tick_df['liquidity'] = tick_df.cumulative_liquidityNet + liquidity_offset

    # Convert liquidity into real token amounts
    tick_df['tick_upper'] = tick_df.tickIdx
    tick_df['tick_lower'] = tick_df.tickIdx - pool.tick_spacing

    token_amount_0_list = []
    token_amount_1_list = []
    for (index, row) in tick_df.iterrows():
        amount_0, amount_1 = process_tick(row, pool)
        token_amount_0_list.append(amount_0)
        token_amount_1_list.append(amount_1)

    tick_df['amount_0'] = token_amount_0_list
    tick_df['amount_1'] = token_amount_1_list


