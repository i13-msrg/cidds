import time
import numpy as np
import matplotlib.pyplot as plt

from base.DAG import DAG


def start_helper(sim):

    plt.rc('axes', labelsize=20)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)

    plt.figure(figsize=(25, 10))

    t = DAG(rate=sim.alpha, tip_selection=sim.algorithm, plot=True)
    for i in range(sim.transactions):
        t.next_transaction()


    # finalPlot.show()
    return t



