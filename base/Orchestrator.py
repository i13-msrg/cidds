import threading
from pprint import pprint
import matplotlib.pyplot as plt
from base.DAG import DAG

def start_helper(sim):

    '''

    :param sim: simulator object
    :return: dag : DAG
    '''

    # Set plots for resulting dag image
    plt.rc('axes', labelsize=20)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)

    plt.figure(figsize=(25, 10))

    # Call the DAG to generate transactions
    dag = DAG(rate=sim.alpha, algorithm=sim.algorithm, plot=True)

    if sim.algorithm == "cac":
        #use cac specific func
        transactions = sim.numTotalUser * sim.traUser
        for i in range(transactions):
            maliciousNode = i % 3 == 0
            dag.generate_next_node(malicious=maliciousNode)
    else:
        for i in range(sim.transactions):
            dag.generate_next_node()

    # Return the result
    return dag



def _p_resolveConflict(self, sim, t):
    '''

    :param self: Orchestrator
    :param sim: simulation object
    :param t: executed thread
    :return: simulator
    '''

    # Lock the current thread
    lock = threading.Lock()
    lock.acquire()
    try:
        # Initiate simualtion
        self.start_helper(sim)
    except Exception as ex:
        # Handle error
        thread_name = threading.current_thread().name
        pprint("Error in initiating simulation {}.{}".format(thread_name, ex))
    finally:
        # Release lock after execution
        lock.release()

    return sim
