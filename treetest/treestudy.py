#!/usr/bin/env python

from math import log

epsilon = 1e-6


class Node():
    def __init__(self, left=None, right=None, branches=None, name="", ent=0, p=None, depth=0, position="", accums=[]):
        # This might be a source of confusion:
        if branches:
            self.branches = branches
        else:
            self.branches = [left, right]
        self.name = name
        self.ent = ent
        self.prob = p
        self.depth = depth
        self.pos = position
        self.accums = accums

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
            # print("Leaf is ", self, self.ent - 1 + epsilon > 0)
            return self.ent - 1 + epsilon > 0
        oks = [br and br.complete() for br in self.branches]
        # print("Branches are ", oks)
        return all(oks)

    def isLeaf(self):
        return not any(self.branches)

    def forPlot(self):
        return [pos2coord(self.pos), self.ent, self.pos, self.accums]


def ent(p):
    assert 0 < p <= 1, "Bad probability"
    return -p*log(p, 2)

# There is a better way to do this without al the precalculated stuff in the node


def pos2coord(pos):
    path = pos.split()
    z = len(path)
    coord = [0, -z]
    for zl, pp in enumerate(path):
        iis, totis = pp.split('/')
        totx = int(totis)
        i = int(iis)
        coord[0] = coord[0] + 1.*(i-(totx-1)/2)/(totx)**zl
        assert totx > 0, "Total branches should be positive"
    return tuple(coord)


def addNext(node, probs):
    assert abs(1.-sum(probs)) < epsilon, "Incoherent probability"
    # assert node.isLeaf(), "Node should be leaf to insert next"
    if node.ent >= 1:
        return node
    if node.isLeaf() and node.ent < 1:
        node.branches = [Node(name=node.name+" "+str(pr), p=node.prob*pr,
                              ent=node.ent+ent(pr), depth=node.depth+1, position=f"{node.pos} {i}/{len(probs)}") for i, pr in enumerate(probs)]
    else:
        node.branches = [addNext(br, probs) for br in node.branches]
    return node


def tree2redundantArray(node, reslist=[]):
    # https://stackoverflow.com/questions/20406346/how-to-plot-tree-graph-web-data-on-gnuplot
    reslist.append(node.forPlot())
    if node.isLeaf():
        return reslist
    for br in node.branches:
        reslist = tree2redundantArray(br, reslist=reslist)
        # This line is required to return the same path for proper tree painting in GNUPlot
        reslist.append(node.forPlot())
    return reslist


def tree2GNUPlot(tree, noTitle=False):
    info = tree2redundantArray(tree)
    if noTitle:
        rets = ""
    else:
        rets = "x y ent name accumulators\n"
    for entry in info:
        accums = ' '.join(map(str, entry[3]))
        rets += "{0} {1} {2} \"{3}\" {4}\n".format(str(entry[0][0]), str(
            entry[0][1]), str(entry[1]), str(entry[2]), accums)
    return rets


if __name__ == "__main__":
    for deno in range(2, 10):
        p = 1./deno
        tree = Node(p=1)
        # for i in range(4):
        while not tree.complete():
            tree = addNext(tree, [p, 1-p])
            # print("Tree ", tree)
            # print("COmplete? ", tree.complete(), '\n')
            # break

        print(tree2GNUPlot(tree, noTitle=deno != 2))
        print()
