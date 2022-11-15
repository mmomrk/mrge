#!/usr/bin/env python

from math import log

epsilon = 1e-6


class Node():
    def __init__(self, left=None, right=None, branches=None, name="", ent=0, p=None, depth=0):
        # This might be a source of confusion:
        if branches:
            self.branches = branches
        else:
            self.branches = [left, right]
        self.name = name
        self.ent = ent
        self.prob = p
        self.depth = depth

    def __repr__(self):
        if any(self.branches):
            iden = "Node"
            branches = ",branches:\n"+str(list(self.branches))
        else:
            iden = "Leaf"
            branches = ""
        return (iden+" "+self.name+", entropy="+str(self.ent)+", prob="+str(self.prob)+branches)

    def complete(self):
        if self.isLeaf():
            #print("Leaf is ", self, self.ent - 1 + epsilon > 0)
            return self.ent - 1 + epsilon > 0
        oks = [br and br.complete() for br in self.branches]
        #print("Branches are ", oks)
        return all(oks)

    def isLeaf(self):
        return not any(self.branches)


def ent(p):
    assert 0 < p <= 1, "Bad probability"
    return -p*log(p, 2)


def addNext(node, probs):
    assert abs(1.-sum(probs)) < epsilon, "Incoherent probability"
    #assert node.isLeaf(), "Node should be leaf to insert next"
    if node.ent >= 1:
        return node
    if node.isLeaf() and node.ent < 1:
        node.branches = [Node(name=node.name+" "+str(pr), p=node.prob*pr,
                              ent=node.ent+ent(pr), depth=node.depth+1) for pr in probs]
    else:
        node.branches = [addNext(br, probs) for br in node.branches]
    return node


def getPrintable(tree):
    # https://stackoverflow.com/questions/20406346/how-to-plot-tree-graph-web-data-on-gnuplot
    depth = 0
    return ""


if __name__ == "__main__":
    p = 1/4.
    tree = Node(p=1)
    print("Tree ", tree)
    # for i in range(4):
    while not tree.complete():
        tree = addNext(tree, [p, 1-p])
        #print("Tree ", tree)
        #print("COmplete? ", tree.complete(), '\n')
        # break

    print("Tree ", tree)
