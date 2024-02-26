# uniswap_v3_liquidity_distributions
Collect, process, and store liquidity distributions from Uniswap V3 Pools.

This repo collects data from the Uniswap V3 Subgraph and processes the liquidity distribution into a human readable format.
To get a liquidity distribution for a pool of interest, run the following script, replacing `pool_id` with your own:

`python get_distribution.py --pool_id 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 --surround_ticks 300`

Please note this repository is a WIP. Market utilities for analyzing pools is a WIP.

![Example liquidity distribution. Liquidity amounts given in token0](assets/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640.gif)