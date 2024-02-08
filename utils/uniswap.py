import math
import pandas as pd

def fee_tier_to_tick_spacing(fee_tier):
    return {
        '10000': 200,
        '3000': 60,
        '500': 10,
        '100': 1
    }.get(fee_tier, 60)

def tick_to_adjusted_price(tick, token_0, token_1):
    return 1. / ((1.0001 ** tick) / 10 ** (token_1.decimals - token_0.decimals))

def tick_to_price(tick):
    return 1.0001 ** tick


# def process_liquidity(ticks, pool):
#
#     # # Get current tick amounts
#     # price = tick_to_price(pool.tick)
#     # price_a = tick_to_price(pool.active_tick_lower)
#     # price_b = tick_to_price(pool.active_tick_upper)
#     #
#     # sp = price ** 0.5
#     # sa = price_a ** 0.5
#     # sb = price_b ** 0.5
#     #
#     # active_amount_0 = pool.liquidity * (sb - sp) / (sp * sb)
#     # active_amount_1 = pool.liquidity * (sp - sa)
#     #
#     # # Adjust to human-readable format
#     # adjusted_active_amount_0 = active_amount_0 / 10 ** pool.token_0.decimals
#     # adjusted_active_amount_1 = active_amount_1 / 10 ** pool.token_1.decimals
#
#     # Get current tick liquidity
#     liquidity_active = pd.DataFrame(
#         {
#             "tick": [pool.active_tick_lower],
#             "liquidity": [pool.liquidity]
#         }
#     )
#
#     # Get top half liquidity
#     ticks_above = ticks.loc[ticks.tickIdx > pool.active_tick_upper].sort_values(by="tickIdx", ascending=True)
#     liquidity = pool.liquidity
#     liquidity_above = pd.DataFrame(
#         {
#             "tick": [],
#             "liquidity": []
#         }
#     )
#     for (index, row) in ticks_above.iterrows():
#         liquidity += row.liquidityNet
#         liquidity_above.loc[len(liquidity_above)] = [row.tickIdx, liquidity]
#
#     # Get bottom half liquidity
#     ticks_below = ticks.loc[ticks.tickIdx < pool.active_tick_lower].sort_values(by="tickIdx", ascending=False)
#     liquidity = pool.liquidity
#     liquidity_below = pd.DataFrame(
#         {
#             "tick": [],
#             "liquidity": []
#         }
#     )
#     for (index, row) in ticks_below.iterrows():
#         liquidity += row.liquidityNet
#         liquidity_below.loc[len(liquidity_below)] = [row.tickIdx, liquidity]
#
#     # Join dataframes
#     liquidity_df = pd.concat(
#         [liquidity_below, liquidity_active, liquidity_above]
#     ).sort_values(by="tick", ascending=True)
#
#
#     return liquidity_df


def process_tick(tick, pool):

    tick_lower = tick.tick_lower
    tick_upper = tick.tick_upper
    liquidity = tick.liquidity

    # Get lower tick price for reference
    adj_price = tick_to_adjusted_price(
        tick_lower,
        pool.token_0,
        pool.token_1
    )

    # Get unadjusted sqrt prices of ticks
    price = tick_to_price(pool.tick)
    price_a = tick_to_price(tick_lower)
    price_b = tick_to_price(tick_upper)

    sp = price ** 0.5
    sa = price_a ** 0.5
    sb = price_b ** 0.5

    # If tick range is below active tick
    if pool.active_tick_lower >= tick_upper:
        amount_0 = 0.00
        amount_1 = liquidity * (sb - sa)
    # If tick range is above active tick
    elif pool.active_tick_upper <= tick_lower:
        amount_0 = liquidity * (sb - sa) / (sa * sb)
        amount_1 = 0.00
    # If tick range includes active tick
    elif (pool.tick > tick_lower) and (pool.tick < tick_upper):
        amount_0 = liquidity * (sb - sp) / (sp * sb)
        amount_1 = liquidity * (sp - sa)
    # Bypass tick in edge case
    else:
        amount_0 = 0.00
        amount_1 = 0.00
        pass

    # Adjust to human-readable format
    adjusted_amount_0 = amount_0 / 10 ** pool.token_0.decimals
    adjusted_amount_1 = amount_1 / 10 ** pool.token_1.decimals

    return adjusted_amount_0, adjusted_amount_1

class Token:
    def __init__(self, token):
        self.symbol = token['symbol']
        self.decimals = int(token['decimals'])
        self.id = token['id']

class Pool:
    def __init__(self, pool):
        self.token_0 = Token(pool['token0'])
        self.token_1 = Token(pool['token1'])
        self.tick = int(pool['tick'])
        self.fee_tier = pool['feeTier']
        self.liquidity = int(pool['liquidity'])
        # self.tvl = float(pool['totalValueLockedUSD'])

        self.tick_spacing = fee_tier_to_tick_spacing(self.fee_tier)
        self.active_tick_lower = math.floor(self.tick / self.tick_spacing) * self.tick_spacing
        self.active_tick_upper = self.active_tick_lower + self.tick_spacing

