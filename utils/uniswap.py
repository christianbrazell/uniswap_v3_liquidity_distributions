import math


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


def percent_to_ticks(percent, pool): ###
    ticks = None
    return ticks


def process_tick(tick, pool):
    tick_lower = tick.tick_lower
    tick_upper = tick.tick_upper
    liquidity = tick.liquidity

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
    """
    Include the following in cache:
    pool_address
    token_0.symbol
    token_1.symbol
    fee_tier
    active_tick_price
    tick
    lp
    """
    def __init__(self, pool):
        self.pool_address = pool['id']
        self.token_0 = Token(pool['token0'])
        self.token_1 = Token(pool['token1'])
        self.tick = int(pool['tick'])
        self.fee_tier = pool['feeTier']
        self.liquidity = int(pool['liquidity'])

        self.tick_spacing = fee_tier_to_tick_spacing(self.fee_tier)
        self.active_tick_lower = math.floor(self.tick / self.tick_spacing) * self.tick_spacing
        self.active_tick_upper = self.active_tick_lower + self.tick_spacing
        self.active_tick_price = tick_to_adjusted_price(self.tick, self.token_0, self.token_1)
        self.lp = None
