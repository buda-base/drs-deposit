"""
find_work.py
Implements strategies for locating a work in a deck
"""
import os
from collections import Counter
from pathlib import Path


def hist_folder(root: Path) -> dict:
    """
    Count the distribution of top level folders in a tree, binned by various algorithms
    """
    buckets = Counter()
    for obj in os.scandir(root):
        if obj.is_dir():
            buckets[obj.name[-2:]] += 1
    return buckets


if __name__ == '__main__':
    print(hist_folder(Path('/Users/jimk/tmp')))
