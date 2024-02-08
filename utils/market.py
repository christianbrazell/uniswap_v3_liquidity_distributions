import pandas as pd
import numpy as np

def get_depth(depth, pool):
    # depth %
    depth_price = pool.active_tick_price * (1.+depth)
    liquidity_in_depth = pool.lp.loc[
        (pool.lp.price <= pool.active_tick_price) &
        (pool.lp.price > depth_price)
    ]
    depth = liquidity_in_depth.amount.sum()

    return depth


def get_slippage(depth, pool):
    slippage = None
    return slippage