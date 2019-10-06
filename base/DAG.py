import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import threading

# This is the base of CIDDS simulator
#
#  Here we have a Directed Acyclic Graph (DAG), which is
#
#  Implementation of algorithms for MCMC and URTS are inspired from inputs by
#  Alon Gal from IOTA foundation and Minh-nghia, Nguyen.
#  For more details on their individual works visit:
#  https://github.com/iotaledger/iotavisualization
#  https://github.com/minh-nghia/TangleSimulator

class Node(object):
    '''
    Stores the individual transaction detail for  a tangle
    '''
    def __init__(self, id: str, time: float):
        '''
        constructor
        :param id: id of the node
        :param time: timestamp in unit time
        '''
        self.x = 300
        self.y = 200
        self.id = id
        self.time = time

    def __init__(self, dag, id: str, time: float):
        # Used only for CAC
        self.x = 300
        self.y = 200
        self.id = id
        self.time = time

        self.dag = dag
        self.vote = None
        self.neighbourNodeIds = []

    def add_neighbour(self, nId):
        if nId not in self.neighbourNodeIds:
                self.neighbourNodeIds.append(nId)

    def get_vote(self):
        numTrue = 0
        numFalse = 0

        for nId in self.neighbourNodeIds:
            node = [n for n in self.dag.nodes if int(n.id) == nId][0]
            if node.vote == True:
                numTrue = numTrue + 1
            if node.vote == False:
                numFalse = numFalse + 1
            

        self.vote = numTrue >= numFalse
        return self.vote

    def is_tip_delayed(self):
        return self.dag.time - 5.0 < self.time

class Link(object):
    '''
    Class for showing connections between the nodes in graph - Approval details
    '''
    def __init__(self, source: Node, target: Node):
        '''
        Constuctor
        :param source: Approving node
        :param target: Node with is approved
        '''
        self.source = source
        self.target = target

class DAG(object):

    def __init__(self, rate=50, alpha=0.001, algorithm='mcmc', plot=False):
        self.time = 1.0
        self.rate = rate
        self.alpha = alpha

        if plot:
            self.graph = nx.OrderedDiGraph()

        self.genesis = Genesis(self)
        self.transactions = [self.genesis]
        self.step_counter = 1
        self.algorithm = algorithm

        self.cw_cache = dict()
        self.transaction_cache = set()
        self.tip_walk_cache = list()
        self.nodes = [Node(self, id=0, time=0)] #Genesis is in by default
        self.links = []

    def generate_next_node(self):
        time_difference = np.random.exponential(1.0 / self.rate)
        self.time += time_difference
        self.step_counter += 1

        if self.algorithm == 'mcmc':
            approved_tips = set(self.mcmc())
        elif self.algorithm == 'urts':
            approved_tips = set(self.urts())
        elif self.algorithm == 'cac':
            approved_tips = set(self.cac())
        else:
            raise Exception()

        transaction = Transaction(self, self.time, approved_tips,
                                  self.step_counter - 1)
        newNode = Node(self, id=str(transaction.num), time=transaction.time)
        self.nodes.append(newNode)
        self.transactions.append(transaction)

        for t in approved_tips:
            t.approved_time = np.minimum(self.time, t.approved_time)
            t._approved_directly_by.add(transaction)

            self.addNeighbourToNode(t.num, transaction.num)
            self.addNeighbourToNode(transaction.num, t.num)

            if hasattr(self, 'graph'):
                self.graph.add_edges_from([(transaction.num, t.num)])
                self.links.append(Link(
                    source=newNode,
                    target=Node(self, id=str(t.num),
                                time=t.time)))
        self.cw_cache = {}
    
    def addNeighbourToNode(self, nodeId, newNodeId):
        node = [n for n in self.nodes if int(n.id) == nodeId][0]
        node.add_neighbour(newNodeId)

    def tips(self):
        return [t for t in self.transactions if t.is_visible() and t.is_tip_delayed()]

    def getTipNodes(self):
        # return [n for n in self.nodes if self.getLinkNum(n.id) < 2]
        return [n for n in self.nodes if n.is_tip_delayed()]

    def getLinkNum(self, targetNodeId):
        linkNum = 0
        for l in self.links:
            if int(l.target.id) == int(targetNodeId):
                linkNum = linkNum + 1
        return linkNum
        
    def cac(self):
        tipNodes = self.getTipNodes()
        if len(tipNodes) > 2:
            selectedTips = np.random.choice(tipNodes, 2)
        else:
            selectedTips = tipNodes

        for tip in selectedTips:
            tip.vote = True
        
        result = self.vote()

        #set all nodes votes to None after geting the final result
        for node in self.nodes:
            node.vote = None
        
        transactionTips = []
        if result:
            for tip in selectedTips:
                transactionTips.append([t for t in self.transactions if t.num == int(tip.id)][0])

        return transactionTips
    
    def vote(self):
        votes = []
        for node in self.nodes:
            votes.append(node.get_vote())
        
        if len(set(votes)) == 1:
            return votes[0]
        else:
            self.vote()
        return False #Will never execute
        
    def urts(self):
        tips = self.tips()
        if len(tips) == 0:
            return np.random.choice(
                [t for t in self.transactions if t.is_visible()]),
        if len(tips) == 1:
            return tips[0],
        return np.random.choice(tips, 2)

    def mcmc(self):
        num_particles = 10
        lower_bound = int(np.maximum(0, self.step_counter - 20.0 * self.rate))
        upper_bound = int(np.maximum(1, self.step_counter - 10.0 * self.rate))

        candidates = self.transactions[lower_bound:upper_bound]
        particles = np.random.choice(candidates, num_particles)
        distances = {}
        for p in particles:
            t = threading.Thread(target=self.mcmc_walk(p))
            t.start()
        tips = self.tip_walk_cache[:2]
        self.tip_walk_cache = list()

        return tips

    def mcmc_walk(self, starting_transaction):
        p = starting_transaction
        while not p.is_tip_delayed() and p.is_visible():
            if len(self.tip_walk_cache) >= 2:
                return

            next_transactions = p.approved_directly_by()
            if self.alpha > 0:
                p_cw = p.calculate_delayed_cumulative_weight()
                c_weights = np.array([])
                for transaction in next_transactions:
                    c_weights = np.append(c_weights,
                                          transaction.calculate_delayed_cumulative_weight())

                deno = np.sum(np.exp(-self.alpha * (p_cw - c_weights)))
                probs = np.divide(np.exp(-self.alpha * (p_cw - c_weights)),
                                  deno)
            else:
                probs = None

            p = np.random.choice(next_transactions, p=probs)

        self.tip_walk_cache.append(p)

    def plot(self):
        if hasattr(self, 'graph'):
            pos = nx.get_node_attributes(self.graph, 'pos')
            nx.draw_networkx_nodes(self.graph, pos)
            nx.draw_networkx_labels(self.graph, pos)
            nx.draw_networkx_edges(self.graph, pos, edgelist=self.graph.edges(),
                                   arrows=True)
            plt.xlabel('Time')
            plt.yticks([])
            return plt

class Transaction(object):

    def __init__(self, dag, time, approved_transactions, num):
        self.dag = dag
        self.time = time
        self.approved_transactions = approved_transactions
        self._approved_directly_by = set()
        self.approved_time = float('inf')
        self.num = num
        self._approved_by = set()

        if hasattr(self.dag, 'graph'):
            self.dag.graph.add_node(self.num,
                                pos=(self.time, np.random.uniform(-1, 1)))

    def is_visible(self):
        return self.dag.time >= self.time + 1.0

    def is_tip(self):
        return self.dag.time < self.approved_time

    def is_tip_delayed(self):
        return self.dag.time - 1.0 < self.approved_time

    def cumulative_weight(self):
        cw = 1 + len(self.approved_by())
        self.dag.transaction_cache = set()

        return cw

    def calculate_delayed_cumulative_weight(self):
        cached = self.dag.cw_cache.get(self.num)
        if cached:
            return cached
        else:
            cached = 1 + len(self.approved_by_delayed())
            self.dag.transaction_cache = set()
            self.dag.cw_cache[self.num] = cached

        return cached

    def approved_by(self):
        for t in self._approved_directly_by:
            if t not in self.dag.transaction_cache:
                self.dag.transaction_cache.add(t)
                self.dag.transaction_cache.update(t.approved_by())

        return self.dag.transaction_cache

    def approved_by_delayed(self):
        for t in self.approved_directly_by():
            if t not in self.dag.transaction_cache:
                self.dag.transaction_cache.add(t)
                self.dag.transaction_cache.update(t.approved_by_delayed())

        return self.dag.transaction_cache

    def approved_directly_by(self):
        return [p for p in self._approved_directly_by if p.is_visible()]

    def __repr__(self):
        return '<Transaction {}>'.format(self.num)

class Genesis(Transaction):

    def __init__(self, dag):
        self.dag = dag
        self.time = 0
        self.approved_transactions = []
        self.approved_time = float('inf')
        self._approved_directly_by = set()
        self.num = 0
        if hasattr(self.dag, 'graph'):
            self.dag.graph.add_node(self.num, pos=(self.time, 0))

    def __repr__(self):
        return '<Genesis>'
