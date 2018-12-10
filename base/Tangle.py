import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import threading

class Node(object):

    def __init__(self, name: str, time: float):
        self.x = 300
        self.y = 200
        self.name = name
        self.time = time

class Link(object):

    def __init__(self, source: Node, target: Node):
        self.source = source
        self.target = target



class Tangle(object):

    def __init__(self, rate=50, alpha=0.001, tip_selection='mcmc', plot=False):
        self.time = 1.0
        self.rate = rate
        self.alpha = alpha

        if plot:
            self.G = nx.OrderedDiGraph()

        self.genesis = Genesis(self)
        self.transactions = [self.genesis]
        self.count = 1
        self.tip_selection = tip_selection

        self.cw_cache = dict()
        self.t_cache = set()
        self.tip_walk_cache = list()
        self.nodes = []
        self.links = []

    def next_transaction(self):
        dt_time = np.random.exponential(1.0 / self.rate)
        self.time += dt_time
        self.count += 1

        if self.tip_selection == 'mcmc':
            approved_tips = set(self.mcmc())
        elif self.tip_selection == 'urts':
            approved_tips = set(self.urts())
        else:
            raise Exception()

        transaction = Transaction(self, self.time, approved_tips,
                                  self.count - 1)
        for t in approved_tips:
            t.approved_time = np.minimum(self.time, t.approved_time)
            t._approved_directly_by.add(transaction)

            if hasattr(self, 'G'):
                self.G.add_edges_from([(transaction.num, t.num)])
                self.links.append(Link(
                    source=Node(name=str(transaction.num),
                                time=transaction.time),
                    target=Node(name=str(t.num),
                                time=t.time)))

        node = Node(name=str(transaction.num), time= transaction.time)
        self.nodes.append(node)
        self.transactions.append(transaction)

        self.cw_cache = {}

    def tips(self):
        return [t for t in self.transactions if
                t.is_visible() and t.is_tip_delayed()]

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
        lower_bound = int(np.maximum(0, self.count - 20.0 * self.rate))
        upper_bound = int(np.maximum(1, self.count - 10.0 * self.rate))

        candidates = self.transactions[lower_bound:upper_bound]
        # at_least_5_cw = [t for t in self.transactions[lower_bound:upper_bound] if t.cumulative_weight_delayed() >= 5]

        particles = np.random.choice(candidates, num_particles)
        distances = {}
        for p in particles:
            t = threading.Thread(target=self._walk2(p))
            t.start()
        #            tip, distance = self._walk(p)
        #            distances[tip] = distance

        # return [key for key in sorted(distances, key=distances.get, reverse=False)[:2]]
        tips = self.tip_walk_cache[:2]
        self.tip_walk_cache = list()

        return tips

    def _walk2(self, starting_transaction):
        p = starting_transaction
        while not p.is_tip_delayed() and p.is_visible():
            if len(self.tip_walk_cache) >= 2:
                return

            next_transactions = p.approved_directly_by()
            if self.alpha > 0:
                p_cw = p.cumulative_weight_delayed()
                c_weights = np.array([])
                for transaction in next_transactions:
                    c_weights = np.append(c_weights,
                                          transaction.cumulative_weight_delayed())

                deno = np.sum(np.exp(-self.alpha * (p_cw - c_weights)))
                probs = np.divide(np.exp(-self.alpha * (p_cw - c_weights)),
                                  deno)
            else:
                probs = None

            p = np.random.choice(next_transactions, p=probs)

        self.tip_walk_cache.append(p)

    def _walk(self, starting_transaction):
        p = starting_transaction
        count = 0
        while not p.is_tip_delayed() and p.is_visible():
            next_transactions = p.approved_directly_by()
            if self.alpha > 0:
                p_cw = p.cumulative_weight_delayed()
                c_weights = np.array([])
                for transaction in next_transactions:
                    c_weights = np.append(c_weights,
                                          transaction.cumulative_weight_delayed())

                deno = np.sum(np.exp(-self.alpha * (p_cw - c_weights)))
                probs = np.divide(np.exp(-self.alpha * (p_cw - c_weights)),
                                  deno)
            else:
                probs = None

            p = np.random.choice(next_transactions, p=probs)
            count += 1

        return p, count

    def plot(self):
        if hasattr(self, 'G'):
            pos = nx.get_node_attributes(self.G, 'pos')
            nx.draw_networkx_nodes(self.G, pos)
            nx.draw_networkx_labels(self.G, pos)
            nx.draw_networkx_edges(self.G, pos, edgelist=self.G.edges(),
                                   arrows=True)
            plt.xlabel('Time')
            plt.yticks([])
            # plt.show()
            return plt


class Transaction(object):

    def __init__(self, tangle, time, approved_transactions, num):
        self.tangle = tangle
        self.time = time
        self.approved_transactions = approved_transactions
        self._approved_directly_by = set()
        self.approved_time = float('inf')
        self.num = num
        self._approved_by = set()

        if hasattr(self.tangle, 'G'):
            self.tangle.G.add_node(self.num,
                                   pos=(self.time, np.random.uniform(-1, 1)))

    def is_visible(self):
        return self.tangle.time >= self.time + 1.0

    def is_tip(self):
        return self.tangle.time < self.approved_time

    def is_tip_delayed(self):
        return self.tangle.time - 1.0 < self.approved_time

    def cumulative_weight(self):
        cw = 1 + len(self.approved_by())
        self.tangle.t_cache = set()

        return cw

    def cumulative_weight_delayed(self):
        cached = self.tangle.cw_cache.get(self.num)
        if cached:
            return cached
        else:
            cached = 1 + len(self.approved_by_delayed())
            self.tangle.t_cache = set()
            self.tangle.cw_cache[self.num] = cached

        return cached

    def approved_by(self):
        for t in self._approved_directly_by:
            if t not in self.tangle.t_cache:
                self.tangle.t_cache.add(t)
                self.tangle.t_cache.update(t.approved_by())

        return self.tangle.t_cache

    def approved_by_delayed(self):
        for t in self.approved_directly_by():
            if t not in self.tangle.t_cache:
                self.tangle.t_cache.add(t)
                self.tangle.t_cache.update(t.approved_by_delayed())

        return self.tangle.t_cache

    def approved_directly_by(self):
        return [p for p in self._approved_directly_by if p.is_visible()]

    def __repr__(self):
        return '<Transaction {}>'.format(self.num)


class Genesis(Transaction):

    def __init__(self, tangle):
        self.tangle = tangle
        self.time = 0
        self.approved_transactions = []
        self.approved_time = float('inf')
        self._approved_directly_by = set()
        self.num = 0
        if hasattr(self.tangle, 'G'):
            self.tangle.G.add_node(self.num, pos=(self.time, 0))

    def __repr__(self):
        return '<Genesis>'
