import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import threading
import random

# This is the base of CIDDS simulator
#
#  Here we have a Directed Acyclic Graph (DAG), which is
#
#  Implementation of algorithms for MCMC and URTS are inspired from inputs by
#  Alon Gal from IOTA foundation and Minh-nghia, Nguyen.
#  For more details on their individual works visit:
#  https://github.com/iotaledger/iotavisualization
#  https://github.com/minh-nghia/TangleSimulator

class User(object):
    def __init__(self, id: int, malicious: bool):
        self.id = id
        self.step_counter = 1
        self.malicious = malicious
        self.mana = 1
    
    def increaseMana(self): 
        self.mana += 1

    def resetMana(self):
        self.mana = 0

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

class CacNode(object):
    def __init__(self, dag, traId: str, nodeId: int, time: float, user: User, malicious: bool):
        self.x = 300
        self.y = 200
        self.traId = traId
        self.nodeId = nodeId
        self.time = time
        self.isTip = False
        self.approved_time = float('inf')
        self.user = user
        self.malicious = malicious

        self.dag = dag
        self.vote = None
        self.neighbourNodeIds = []

    def add_neighbour(self, node):
        if node.traId not in self.neighbourNodeIds:
                self.neighbourNodeIds.append(node.traId)

    def get_vote(self):
        numTrue = 0
        numFalse = 0

        #get neightbours vote from dag.nodes because python is pass by value... :(
        # for node in self.neighbourNodes:
        for node in (n for n in self.dag.nodes if (n.traId in self.neighbourNodeIds)):
            if node.vote == True:
                numTrue += 1
            if node.vote == False:
                numFalse += 1
    
        if numTrue > numFalse:
            self.vote = True
        elif numTrue < numFalse:
            self.vote = False
        else:
            if len(self.neighbourNodeIds) == 0:
                return True
            #add mana here
            # print(self.neighbourNodeIds)
            # print([n.vote for n in self.dag.nodes if (n.traId in self.neighbourNodeIds)])
            numTrue = 0
            numFalse = 0
            for node in (n for n in self.dag.nodes if (n.traId in self.neighbourNodeIds)):
                if node.vote == True:
                    numTrue += node.user.mana
                if node.vote == False:
                    numFalse += node.user.mana
            if numTrue != 0 and numFalse != 0:
                self.vote = numTrue >= numFalse
        # print("/////")
        # print(self.traId)
        # print(self.vote)
        # print("/////")
        return self.vote

    def is_tip_delayed(self):
        return self.dag.time - 5.0 < self.approved_time

class DAG(object):

    def __init__(self, rate=50, alpha=0.001, algorithm='mcmc', plot=False, numUsers=1, numMalUsers=0):
        self.time = 1.0
        self.rate = rate
        self.alpha = alpha

        if plot:
            self.graph = nx.OrderedDiGraph()
        self.algorithm = algorithm

        self.cw_cache = dict()
        self.transaction_cache = set()
        self.tip_walk_cache = list()

        if self.algorithm == 'cac':
            self.transactions = []
            self.nodes = []
            self.users = []
            self.step_counter = 0
            for i in range(numUsers):
                malUserIds = np.random.choice(range(1, numUsers), numMalUsers)
                self.users.append(User(id=i, malicious=(i in malUserIds)))
        else:
            self.genesis = Genesis(self)
            self.transactions = [self.genesis]
            self.step_counter = 1
            self.nodes = [Node(id=0, time=0)]

    def generate_next_node(self):
        time_difference = np.random.exponential(1.0 / self.rate)
        self.time += time_difference
        self.step_counter += 1

        if self.algorithm == 'mcmc':
            approved_tips = set(self.mcmc())
        elif self.algorithm == 'urts':
            approved_tips = set(self.urts())
        else:
            raise Exception()

        transaction = Transaction(self, self.time, approved_tips,
                                  self.step_counter - 1)
        newNode = Node(id=str(transaction.num), time=transaction.time)
        self.nodes.append(newNode)
        self.transactions.append(transaction)

        for t in approved_tips:
            t.approved_time = np.minimum(self.time, t.approved_time)
            t._approved_directly_by.add(transaction)

            if hasattr(self, 'graph'):
                self.graph.add_edges_from([(transaction.num, t.num)])
        self.cw_cache = {}
    
    def generate_next_node_for_cac_user(self, userId=1):
        time_difference = np.random.exponential(1.0 / self.rate)
        self.time += time_difference
        user = [u for u in self.users if u.id == userId][0]

        selectedTips = self.getTipNodes()

        # transaction = Transaction(self, self.time, selectedTips, self.step_counter)
        malicious = user.malicious and np.random.randint(2) % 2 == 0
        newNode = CacNode(self, traId=self.step_counter, nodeId=user.step_counter, time=self.time, user=user, malicious=malicious)

        # approved_tips = set(self.cac(selectedTips, newNode))
        approved = self.cac(selectedTips, newNode)
        # print('.......')
        # print(newNode.traId)
        # print(approved)
        # print('.......')
        # print([n.traId for n in selectedTips])
        # print('.......')
        if approved:
            transaction = Transaction(self, self.time, selectedTips, self.step_counter)
            newNode.isTip = True
            newNode.approved_time = float('inf')

            for tip in selectedTips:
                tra = [t for t in self.transactions if t.num == int(tip.traId)][0]
                tra.approved_time = np.minimum(self.time, tra.approved_time)
                tra._approved_directly_by.add(transaction)
            
                self.addNeighbourToNode(tip, newNode)
                self.addNeighbourToNode(newNode, tip)
            
            user.increaseMana()

        else:
            transaction = Transaction(self, self.time, [], self.step_counter)
            for tip in selectedTips:
                tra = [t for t in self.transactions if t.num == int(tip.traId)][0]
                tra.approved_time = np.minimum(self.time, tra.approved_time)
                tra._approved_directly_by.add(transaction)
            
                self.addNeighbourToNode(tip, newNode)
                self.addNeighbourToNode(newNode, tip)
            newNode.isTip = False
            newNode.approved_time = float('inf')
            user.resetMana()
        
        for tip in selectedTips:
            if hasattr(self, 'graph'):
                self.graph.add_edges_from([(transaction.num, tip.traId)])
            if approved and len([n for n in self.nodes if n.isTip]) > 2:
                tip.isTip = False
            else: 
                tip.isTip = True

        self.nodes.append(newNode)
        self.transactions.append(transaction)

        self.step_counter += 1
        user.step_counter += 1
        self.cw_cache = {}
    
    def addNeighbourToNode(self, node, newNode):
        node.add_neighbour(newNode)

    def tips(self):
        return [t for t in self.transactions if t.is_visible() and t.is_tip_delayed()]

    def getTipNodes(self):
        # tipNodes = [n for n in self.nodes if self.getLinkNum(n.id) < 2]
        # tipNodes = [n for n in self.nodes if n.is_tip_delayed()]
        tipNodes = [n for n in self.nodes if n.isTip]
        # print("TIPNODES:")
        # print([t.traId for t in tipNodes])
    

        if len(tipNodes) > 2:
            # selectedTips = np.random.choice(tipNodes, 2)
            selectedTips = random.sample(tipNodes, k=2)
        else:
            selectedTips = tipNodes

        # print([t.traId for t in selectedTips])
        # print("'''''")
        return selectedTips

    def cac(self, selectedTips, node):
        for tip in selectedTips:
            tip.vote = node.malicious != True
        
        result = self.vote()

        #set all nodes votes to None after geting the final result
        for node in self.nodes:
            node.vote = None

        return result
        
    def vote(self):
        votes = []
        for node in self.nodes:
            if node.malicious: continue
            votes.append(node.get_vote())
        if len(set(votes)) == 0:
            return True
        if len(set(votes)) == 1 and votes[0] != None:
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
            if self.algorithm == 'cac':
                user1 = []
                user2 = []
                user3 = []
                labels = dict()
                malNodesLabels = dict()
                for node in self.nodes:
                    if node.malicious:
                        malNodesLabels[int(node.traId)] = node.nodeId
                    else:
                        labels[int(node.traId)] = node.nodeId

                    if node.user.id == 0:
                        user1.append(int(node.traId))
                    elif node.user.id == 1:
                        user2.append(int(node.traId))
                    else:
                        user3.append(int(node.traId))

                nx.draw_networkx_nodes(self.graph, pos, nodelist=user1, node_color='g', node_size=600, alpha=0.5)
                nx.draw_networkx_nodes(self.graph, pos, nodelist=user2, node_color='b', node_size=600, alpha=0.5)
                nx.draw_networkx_nodes(self.graph, pos, nodelist=user3, node_color='y', node_size=600, alpha=0.5)
                nx.draw_networkx_labels(self.graph, pos, labels, font_weight="bold", font_size=20)
                nx.draw_networkx_labels(self.graph, pos, malNodesLabels, font_color='r', font_weight="bold", font_size=20)

            else:
                nx.draw_networkx_nodes(self.graph, pos, node_color='g', node_size=600, alpha=0.5)
                nx.draw_networkx_labels(self.graph, pos, font_color="r", font_weight="bold", font_size=20)
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
