import pandas as pd
import numpy as np


def get_liquidity_in_depth(depth, pool, order_type):
    if order_type == 'buy':
        depth_price = pool.active_tick_price * (1. + depth)
        liquidity_in_depth = pool.lp.loc[
            (pool.lp.price > pool.active_tick_price) &
            (pool.lp.price <= depth_price)
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


def get_efficiency(depth, pool, order_type):
    slippage = get_slippage(depth, pool, order_type)
    depth = get_depth(depth, pool, order_type)
    efficiency = slippage / depth

    return efficiency


def get_tilt(depth, pool):
    liquidity_buy = get_liquidity_in_depth(depth, pool, 'buy')
    liquidity_sell = get_liquidity_in_depth(depth, pool, 'sell')
    tilt = liquidity_buy.amount.sum() / liquidity_sell.amount.sum()

    return tilt
