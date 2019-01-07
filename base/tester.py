import json
import time
import numpy as np
import matplotlib.pyplot as plt

from base.DAG import DAG

def start_helper():

    plt.rc('axes', labelsize=20)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)

    plt.figure(figsize=(25, 10))

    t = DAG(rate=1, algorithm='urts', plot=True)
    for i in range(10):
        t.generate_next_node()

    nodes = json.dumps(t.nodes)
    # finalPlot.show()
    return t


if __name__== "__main__":
    start_helper()
