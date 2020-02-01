import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import threading
from threading import Lock, Thread
import random
import time as timeee

transactionCounter = 0 
lock = Lock()

succesfulAttacks = 0
failedAttacks = 0

class User(object):
    def __init__(self, id: int, malicious: bool):
        self.id = id
        self.node_id_counter = 1
        self.malicious = malicious
        self.mana = 1
    
    def increaseMana(self): 
        self.mana += 1

    def resetMana(self):
        self.mana = 0

class CacNode(object):
    def __init__(self, dag, traId: str, nodeId: int, time: float, user: User, malicious: bool):
        self.traId = traId
        self.nodeId = nodeId
        self.time = time
        self.isTip = True
        self.user = user
        self.malicious = malicious
        self.dag = dag
        self.vote = None
        self.neighbourNodeIds = []

        if hasattr(self.dag, 'graph'):
            if malicious:
                self.dag.graph.add_node(self.traId, pos=(self.time, np.random.uniform(-2, 0)))
            else:
                self.dag.graph.add_node(self.traId, pos=(self.time, np.random.uniform(0, 10)))

    def add_neighbour(self, node):
        if node.traId not in self.neighbourNodeIds:
                self.neighbourNodeIds.append(node.traId)

    def get_vote(self):
        neighbourVotes = []
        #get neightbours vote from dag.nodes because python is pass by value... :(
        for node in (n for n in self.dag.addedNodes if (n.traId in self.neighbourNodeIds)):
            neighbourVotes.append(node.vote)
        votesWithoutNone = [vote for vote in neighbourVotes if vote != None]

        if len(votesWithoutNone) == 0:
            return self.vote
        if len(votesWithoutNone) == 1:
            # If all neighbours have the same vote, set vote to it
            self.vote = votesWithoutNone[0]
            # TODO: burada senin mana mi yoksa neighbour mu buyuk bakmali
            return self.vote
        # Else count the occurences of neighbour nodes
        votesCountDict = {}
        for vote in set(votesWithoutNone):
            votesCountDict[vote] = votesWithoutNone.count(vote)

        # Check if 2 votes have the same number, if so use mana, else return max vote
        maxValue = max(votesCountDict, key=votesCountDict.get)
        if isinstance(maxValue, int):
            self.vote = maxValue
        else:
            votesCountDict = {}
            for vote in set(votesWithoutNone):
                votesCountDict[vote] = 0
            for node in (n for n in self.dag.addedNodes if (n.traId in self.neighbourNodeIds)):
                votesCountDict[node.vote] += node.user.mana
            maxValue = max(votesCountDict, key=votesCountDict.get)
            if isinstance(maxValue, int):
                self.vote = maxValue
            else:
                self.vote = maxValue[0]
        return self.vote

class DAG_C(object):

    def __init__(self, plot=False, numUsers=1, numMalUsers=0, traPerUser=0, reattachment=False):
        self.time = 1.0
        self.realtime = timeee.time()
        
        print("DAG: numUsers:" + str(numUsers) + " numMalUsers:" + str(numMalUsers) + " traPerUser:" + str(traPerUser) + " reattachment:" + str(reattachment))

        if plot:
            self.graph = nx.OrderedDiGraph()

        self.nodes = []
        self.addedNodes = []
        self.unvalidatedNodes = []
        self.users = []
        self.currTime = 0
        self.nodesToAdd = []
        self.traPerUser = traPerUser
        self.reattachment = reattachment
        self.numMalUsers = numMalUsers

        if numUsers < 3:
            self.users.append(User(id=0, malicious=False))
        # TODO: Num mal needs to be 2lower i sayfaya ekle
        else:
            malUserIds = np.random.choice(range(2, numUsers), numMalUsers)
            for i in range(numUsers):
                self.users.append(User(id=i, malicious=(i in malUserIds)))

    def generate_next_node(self, userId=1, time=0, malicious=False):
        if malicious:
            self.malicious_user_attack(userId, time)
        else:
            if userId == None:
                while len(self.nodesToAdd) != 0:
                    self.time += 1
                    self.non_malicious_user(None, self.time)
            else:
                self.non_malicious_user(userId, self.time)

    def malicious_user_attack(self, userId, _time=0):
        global failedAttacks
        global succesfulAttacks
        while len(self.addedNodes) < 1:
            timeee.sleep(random.uniform(1, 3))

        # Select 2 tips from added nodes
        tipNodes = [n for n in self.addedNodes]
        if len(tipNodes) > 2:
            sTips = random.sample(tipNodes, k=2)
        else:
            sTips = tipNodes
        # Check depth of those 2 tips to see if its larger than num transactions
        
        # str([n.traId for n in self.nodesToAdd])
        depth = 0
        removalNodeId = self.addedNodes[0].traId

        for tip in sTips: 
            newDepth = self.getCurrentDepthOfNode(tip.traId)
            if newDepth > depth:
                depth = newDepth
            if tip.traId > removalNodeId:
                removalNodeId = tip.traId
            # TODO: Must change this. Secili tiplerden buyuk olan degil kucuk depth alinmali
            #TODO: Depth hesabida yanlis zaten [0,1,2,4] var 4,2 secti depth 5 diyo! :/
        
        # Create subtree with all transactions of that user
        newTree = self.maliciousTreeWith(sTips, userId, self.traPerUser)

        nodeIdsArray = list([n.traId for n in self.addedNodes])
        idx = nodeIdsArray.index(removalNodeId) + 1
        curdepth = len(self.addedNodes[(idx+1):])
        # Set subtree as main tree or discard as unsuccesfull attack
        if curdepth > self.traPerUser:
            failedAttacks += 1
            print(" -Attack: User:" + str(userId) + " time:" + str(_time) + " -failed")
            #Unsuccessful attack, main tree stays as it is
            user = [u for u in self.users if u.id == userId][0]
            user.resetMana()
        else:
            succesfulAttacks += 1
            print(" -Attack: User:" + str(userId) + " time:" + str(_time) + " -succesfull")

            #Succesful Attack, main tree discards the part after tips and appends malicious tree
            self.unvalidatedNodes += self.addedNodes[(idx+1):]
            self.addedNodes = self.addedNodes[:idx] + newTree
        
    def maliciousTreeWith(self, sTips, userId, depth):
        _addedNodes = []
        #get largest time of selected tips
        startTime = 0 
        for tip in sTips: 
            if tip.time > startTime:
                startTime = tip.time

        tips = sTips
        #creates a malicious tree in graph with given number of transactions
        #add 2 nodes each second until sub tree formed
        for i in range(depth):
            node, tips = self.addMaliciousNodeToGraph(userId, startTime, tips)
            _addedNodes.append(node)
            if i % 2 == 0:
                startTime = startTime + 1
        #returns the list of nodes that have been created
        return _addedNodes

    def non_malicious_user(self, userId=1, time=0):
        global transactionCounter
        self.time = time
        oldNodesToAdd = []
        if userId != None:
            user = [u for u in self.users if u.id == userId][0]
            newNode = CacNode(self, traId=transactionCounter, nodeId=user.node_id_counter, time=self.time, user=user, malicious=False)
            transactionCounter += 1
            user.node_id_counter += 1
        
        nodeToAdd = None
        selectedTips = None

        if (time == self.currTime) and (userId != None):
            self.nodesToAdd.append(newNode)
        else:            
            lock.acquire()
            
            self.currTime = self.time
            oldNodesToAdd = self.nodesToAdd
            self.nodesToAdd = []
            if userId != None:
                self.nodesToAdd.append(newNode)

            if len(self.addedNodes) > 2:
                nodeToAdd, selectedTips = self.cac(oldNodesToAdd)
            else:
                # Add all
                nodeToAdd = None

                if len(oldNodesToAdd) <= 2:
                    for node in oldNodesToAdd:
                        self.addNodeToGraph(node, self.addedNodes)
                else:
                    self.addNodeToGraph(oldNodesToAdd[0], self.addedNodes)
                    self.addNodeToGraph(oldNodesToAdd[1], self.addedNodes)

                    self.nodes.append(oldNodesToAdd[0])
                    self.nodes.append(oldNodesToAdd[1])

                    for node in oldNodesToAdd[2:]:
                        node.time += 1
                        self.graph.node[node.traId]['pos'] = (node.time, np.random.uniform(0, 10))
                        self.nodesToAdd.append(node)

            if nodeToAdd != None and selectedTips != None:
                self.addNodeToGraph(nodeToAdd, selectedTips)

                if self.reattachment:
                    for node in ([n for n in oldNodesToAdd if n.traId != nodeToAdd.traId]):
                        node.time += 1
                        self.graph.node[node.traId]['pos'] = (node.time, np.random.uniform(0, 10))
                        self.nodesToAdd.append(node)
            
            lock.release()
    
        if selectedTips != None:
          #TODO: Eski isTip true olan hic falselanmiyo, hep tip kaliyo
            for tip in selectedTips:     
                if len([n for n in self.addedNodes if n.isTip]) > 3:
                    if self.reattachment:
                        tipNode = [n for n in self.nodes if n.traId == tip.traId][0]
                    else:
                        tipNode = [n for n in self.addedNodes if n.traId == tip.traId][0]
                    tipNode.isTip = False
                else: 
                    if self.reattachment:
                        tipNode = [n for n in self.nodes if n.traId == tip.traId][0]
                    else:
                        tipNode = [n for n in self.addedNodes if n.traId == tip.traId][0]
                    tipNode.isTip = True
        if self.reattachment:
            if nodeToAdd != None:
                self.nodes.append(nodeToAdd)
        else:
            for node in oldNodesToAdd:
                if node != None and node not in self.nodes:
                    self.nodes.append(node)
    
    def addNodeToGraph(self, node, tips):
        node.isTip = True
        self.addedNodes.append(node)
        user = [u for u in self.users if u.id == node.user.id][0]
        user.increaseMana()

        for tip in tips:
            if hasattr(self, 'graph'):
                self.graph.add_edges_from([(node.traId, tip.traId)], edge_color='r')
            self.addNeighbourToNode(tip, node)
    
    def addMaliciousNodeToGraph(self, userId, time, tips):
        global transactionCounter

        user = [u for u in self.users if u.id == userId][0]
        newNode = CacNode(self, traId=transactionCounter, nodeId=user.node_id_counter, time=time, user=user, malicious=True)
        transactionCounter += 1
        user.node_id_counter += 1
        user.increaseMana()
        self.nodes.append(newNode)

        for tip in tips:
            if hasattr(self, 'graph'):
                self.graph.add_edges_from([(newNode.traId, tip.traId)], edge_color='r')
            self.addNeighbourToNode(tip, newNode)

        # TODO: IsTip i false yap onceki tipler icin!!!!
        # TODO: IsTip i secmeyi duzelt eger attack basariliysa 
        # eskileri artik tip olmamali sadece bunlar olmali, basarisizsa bunlar tip olmamali

        newTips = []
        if len(tips) > 1:
            newTips.append(tips[1])
        else:
            newTips.append(tips[0])
        newTips.append(newNode)

        return newNode, newTips

    def addNeighbourToNode(self, node, newNode):
        node.add_neighbour(newNode)
        newNode.add_neighbour(node)

    def getTipNodes(self):
        tipNodes = [n for n in self.addedNodes if n.isTip]
        if len(tipNodes) > 2:
            selectedTips = random.sample(tipNodes, k=2)
        else:
            selectedTips = tipNodes
        return selectedTips

    def getCurrentDepthOfNode(self, nodeId):
        node = [n for n in self.addedNodes if n.traId == nodeId][0]
        nodePosition = self.addedNodes.index(node)
        length = len(self.addedNodes)
        return nodePosition - length

    def tips(self):
        return [n for n in self.addedNodes if n.isTip]

    def cac(self, nodesToAdd):
        selectedTipss = None

        if len(nodesToAdd) > 1:
            for node in reversed(nodesToAdd):
                selectedTips = self.getTipNodes()
                for tip in selectedTips:
                    if tip.vote == None:
                        tip.vote = node.traId
                        selectedTipss = selectedTips
                    else:
                        currentVoteMana = 0
                        if len([n.user.mana for n in self.nodesToAdd if n.traId == tip.vote]) > 0:
                            currentVoteMana = [n.user.mana for n in self.nodesToAdd if n.traId == tip.vote][0]
                        if currentVoteMana < node.user.mana:
                            tip.vote = node.traId
                            selectedTipss = selectedTips
        elif len(nodesToAdd) == 1:
            selectedTipss = self.getTipNodes()
            for tip in selectedTipss:
                tip.vote = nodesToAdd[0].traId

        else:
            return None, selectedTipss

        result = self.vote()
        # set all nodes votes to None after geting the final result
        for node in self.addedNodes:
            node.vote = None
        if result != None:
            if len([node for node in nodesToAdd if node.traId == result]) > 0:
                return [node for node in nodesToAdd if node.traId == result][0], selectedTipss
            return [node for node in self.nodes if node.traId == result][0], selectedTipss

        return None, selectedTipss
        
    def vote(self, counter=0):
        votes = []
        for node in self.addedNodes:
            votes.append(node.get_vote())
        if len(set(votes)) == 0:
            return self.nodesToAdd[0].traId
        if len(set(votes)) == 1 and votes[0] != None:
            return votes[0]
        if counter > 8:
            if votes[0] != None:
                return votes[0]
            else:
                return votes[len(votes)-1]
        return self.vote(counter+1)

    def plot(self):
        global transactionCounter
        global failedAttacks
        global succesfulAttacks

        transactionCounter = 0

        if hasattr(self, 'graph'):
            pos = nx.get_node_attributes(self.graph, 'pos')
            
            node_colors = ['#F7A81D', '#27ECEC','#8E8E8E', '#379716', '#7E27EC', '#ECE927', '#E413A8', '#2775EC']
            
            # malNodesLabels = dict(zip([int(node.traId) for node in self.maliciousNodes], [node.nodeId for node in self.maliciousNodes]))
            # honNodeLabels = dict(zip([int(node.traId) for node in self.honestNodes], [node.nodeId for node in self.honestNodes]))
            maliciousUsers = [u.id for u in self.users if u.malicious == True]
            maliciousNodes = []
            if len(maliciousUsers) > 0:
                maliciousNodes = [n for n in self.nodes if n.user.id in maliciousUsers]

            edge_colors = []
            for e in self.graph.edges():
                if e[0] in [n.traId for n in maliciousNodes]:
                    edge_colors.append('red')
                elif e[0] in [n.traId for n in self.unvalidatedNodes]:
                    edge_colors.append('gray')
                else:
                    edge_colors.append('black')

            # nodeLabels = dict(zip([int(node.traId) for node in self.nodes], [node.nodeId for node in self.nodes]))
            nodeLabels = dict(zip([int(node.traId) for node in self.nodes], [node.traId for node in self.nodes]))
            
            allNodes = []
            addedUserNodes = []
            discardedUserNodes = []
            allDiscardedNodes = [node for node in self.nodes if (node not in self.addedNodes)]

            for userId in [user.id for user in self.users]:
                addedUserNodes.append([int(node.traId) for node in self.addedNodes if node.user.id == userId])
                discardedUserNodes.append([int(node.traId) for node in allDiscardedNodes if node.user.id == userId])

            for idx, node in enumerate(addedUserNodes):
                nx.draw_networkx_nodes(self.graph, pos, nodelist=node, node_color=node_colors[idx % 8], node_size=600, alpha=0.65)

            for idx, node in enumerate(discardedUserNodes):
                nx.draw_networkx_nodes(self.graph, pos, nodelist=node, node_color=node_colors[idx % 8], node_size=500, alpha=0.25)

            nx.draw_networkx_labels(self.graph, pos, nodeLabels, font_size=20)
            nx.draw_networkx_edges(self.graph, pos, edgelist=self.graph.edges(), arrows=True, edge_color=edge_colors)

            largestTime = 0 
            for node in self.nodes:
                if node.time > largestTime:
                    largestTime = node.time

            print("Result: simTime:" + str(largestTime) + " runTime:" + str(timeee.time() - self.realtime) + " discardedNodes:" + str(len(allDiscardedNodes)) + " addedNodes:" + str(len(self.addedNodes)))
            if self.numMalUsers > 0:
                print("Attacks: succesful:" + str(succesfulAttacks) + " failed:" + str(failedAttacks))

            plt.xlabel('Time')
            plt.yticks([])
            return plt
