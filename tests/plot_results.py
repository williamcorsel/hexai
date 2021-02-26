""" 
plot_results.py: Plot rating history from pickle file
"""
import argparse
import pickle
import matplotlib.pyplot as plt
import numpy as np


# Parse arguments
parser = argparse.ArgumentParser(description='Plot experiment results')
parser.add_argument("file", type=str,
                    help='Data file')
args = parser.parse_args()

def plot_rating_hist(hist):
    """Plot rating history

    Args:
        hist (dict): Dict with rating history lists
    """
    for key in hist.keys():
        means = np.array([rating.mu for rating in hist[key]])
        
        x = range(0,len(means))
        if "10000_" in key:
            plt.plot(x, means, "-", label=key)
        elif "1000_" in key:
            plt.plot(x, means, "--", label=key)
        elif "100_" in key:
            plt.plot(x, means, ":", label=key)
    
    plt.xlabel("Number of games")
    plt.ylabel("Rating")
    plt.legend(loc='upper left')
    plt.show()
    

hist_file = open(args.file, "rb")
hist = pickle.load(hist_file)

plot_rating_hist(hist)
