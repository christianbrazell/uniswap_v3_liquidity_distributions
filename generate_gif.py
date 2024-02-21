import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import imageio
import pickle

from utils.uniswap import *

pools = [
    '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
    '0xcbcdf9626bc03e24f779434178a73a0b4bad62ed'
]

for pool in pools:
    dir = os.path.join('data', pool)
    image_path = os.path.join('images', pool)

    # Ensure the data directories exists
    os.makedirs('images', exist_ok=True)
    os.makedirs(image_path, exist_ok=True)

    for fname in sorted(os.listdir(dir)):
        # Process the saved Pool objects
        if fname[-4:] != '.pkl':
            continue

        print(fname)
        with open(os.path.join(dir, fname), 'rb') as file:
            p = pickle.load(file)

        # Generate frames
        plt.style.use("dark_background")
        plt.figure(figsize=(10, 8), dpi=100)

        sns.lineplot(data=p.lp, x="price", y="amount")
        plt.fill_between(x=p.lp['price'], y1=p.lp['amount'], alpha=0.3)
        plt.axvline(x=p.active_tick_price, color='red', linestyle='--')

        plt.title(f"{fname[:-4]} UniswapV3 {p.token_0.symbol}/{p.token_1.symbol} {p.fee_tier}")
        plt.xlabel(f"Price [{p.token_0.symbol}]")
        plt.ylabel(f"Liquidity in Tick [{p.token_0.symbol}]")
        plt.grid(alpha=0.2)

        plt.savefig(os.path.join(image_path, fname[:-4]+'.png'))
        plt.close()

    # Generate GIF
    frames = []
    for fname in sorted(os.listdir(image_path)):
        image = imageio.v2.imread(os.path.join(image_path, fname))
        frames.append(image)

    imageio.mimsave(
    f'{pool}.gif',
        frames,
        fps=7,
        loop=0
    )