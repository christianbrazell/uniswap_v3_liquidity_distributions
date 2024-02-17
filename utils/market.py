import pandas as pd
import numpy as np


def get_liquidity_in_depth(depth, pool, order_type):
    # First take from token supply at current tick
    # Second
    if order_type == 'buy':
        depth_price = pool.active_tick_price * (1. + depth)
        liquidity_in_depth = pool.lp.loc[
            (pool.lp.price >= pool.active_tick_price) &
            (pool.lp.price < depth_price)
        ]
    elif order_type == 'sell':
        depth_price = pool.active_tick_price * (1. - depth)
        liquidity_in_depth = pool.lp.loc[
            (pool.lp.price <= pool.active_tick_price) &
            (pool.lp.price > depth_price)
        ]
    else:
        print('please prove a correct order type')
        return None

    return liquidity_in_depth


def get_depth(depth, pool, order_type):
    liquidity_in_depth = get_liquidity_in_depth(depth, pool, order_type)
    depth = liquidity_in_depth.amount.sum()

    return depth


def get_slippage(depth, pool, order_type):
    liquidity_in_depth = get_liquidity_in_depth(depth, pool, order_type)
    numerator = (liquidity_in_depth.amount * liquidity_in_depth.price).sum()
    denominator = pool.active_tick_price * get_depth(depth, pool, order_type)
    slippage = abs(numerator / denominator - 1.)

    return slippage


def get_efficiency(depth, pool):
    # Consider an efficiency metric for capital allocation in V3 Pool:
    # Efficiency = slippage per amount allocated
    # At a given depth (percentage from active price) we can calculate this efficiency

    # Buy side efficiency
    slippage_buy = get_slippage(depth, pool, 'buy')
    depth_buy = get_depth(depth, pool, 'buy')
    efficiency_buy = slippage_buy / depth_buy

    # Sell side efficiency
    slippage_sell = get_slippage(depth, pool, 'sell')
    depth_sell = get_depth(depth, pool, 'sell')
    efficiency_sell = slippage_sell / depth_sell

    # Average buy and sell efficiency
    efficiency = np.mean([efficiency_buy, efficiency_sell])

    return efficiency


def get_efficiency_2(depth, pool):
    return np.mean(
        [
            get_slippage(depth, pool, 'buy'),
            get_slippage(depth, pool, 'sell')
        ]
    )

def get_tilt(depth, pool):
    liquidity_buy = get_liquidity_in_depth(depth, pool, 'buy')
    liquidity_sell = get_liquidity_in_depth(depth, pool, 'sell')
    tilt = liquidity_buy.amount.sum() / liquidity_sell.amount.sum()

    return tilt
