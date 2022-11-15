#!/usr/bin/env python3

import unittest
import treestudy as tr


class testMRGE(unittest.TestCase):
    def testDummy(self):
        assert True, "Congratulations"

    def testNodeBasic(self):
        tree = tr.Node(name="_", p=1)
        p = 1./4
        tree.branches = [tr.Node(p=pr, name=tree.name+str(pr))
                         for pr in [p, 1-p]]
        assert not tree.complete(), "bad complete"
        assert not tree.isLeaf(), "bad isleaf"

    # Incomplete test
    def testAddNext(self):
        tree = tr.Node(p=1)
        tree = tr.addNext(tree, [1./2, 1./2])
        assert all(tree.branches), "bad population"
        assert tree.ent == 0, "bad init entropy"
        assert abs(sum([br.ent for br in tree.branches]) -
                   1) < tr.epsilon, "bad entropy of leaf"
        assert all(
            br.complete for br in tree.branches), "bad complete calculation"

    def testPos2coord(self):
        pos = ""
        assert tr.pos2coord(pos) == (0, 0), "Bad coord 2 pos for init"
        pos = " "
        assert tr.pos2coord(pos) == (0, 0), "Bad coord 2 pos for init with WS"
        # 0 1 2<- / total=3
        pos = "2/3"
        assert tr.pos2coord(pos) == (1, -1), "Bad coord for first pos"
        pos = "1/3"
        assert tr.pos2coord(pos) == (0, -1), "Bad coord for first pos mid"
        pos = "0/3"
        assert tr.pos2coord(pos) == (-1, -1), "Bad coord for first pos left"
        pos = "0/2 0/2"
        assert tr.pos2coord(
            pos) == (-0.75, -2), "Bad coord for second pos left left"
        pos = "1/2 0/2"
        assert tr.pos2coord(pos) == (
            0.25, -2), "Bad coord for second pos left left"
        pos = "2/3 1/2"
        assert tr.pos2coord(pos) == (
            1.25, -2), "Bad coord for second mid/3, right"
        pos = "1/3 1/2"
        assert tr.pos2coord(pos) == (
            0.25, -2), "Bad coord for second mid/3, right"
        pos = "2/3 0/2"
        assert tr.pos2coord(pos) == (
            0.75, -2), "Bad coord for second mid/3, right"

    def testTree2GNUPlot(self):
        tree = tr.Node(p=1)
        tree = tr.addNext(tree, [1./3, 1./3, 1./3])
        stree = tr.tree2GNUPlot(tree)
        print("!!!", stree)
        splitStrings = stree.split('\n')
        assert 'x y' in splitStrings[0], "bad headers line"
        assert '0 0' in splitStrings[1][:5], "tree root not in 0,0"
        assert '-1' in splitStrings[2][:5], "no negative coordinates of first leaf"
        assert '0 0' in splitStrings[3][:5], "no return to first node for proper drawing purposes"


if __name__ == "__main__":
    unittest.main()
