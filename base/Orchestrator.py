import time
import numpy as np
import matplotlib.pyplot as plt

from base.Tangle import Tangle

def start_helper():

    plt.rc('axes', labelsize=20)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)

    plt.figure(figsize=(25, 10))

    t = Tangle(rate=10, tip_selection='urts', plot=True)
    for i in range(10):
        t.next_transaction()

    finalPlot = t.plot()
    # finalPlot.show()
    return finalPlot




    # plt.figure(figsize=(25, 10))
    #
    # t = Tangle(rate=10, tip_selection='mcmc', plot=True)
    # for i in range(100):
    #     t.next_transaction()
    #
    # t.plot()

