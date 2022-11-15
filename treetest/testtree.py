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

    def testPrint4Chart(self):
        tree = tr.Node(p=1, name="0")
        p = 1./4
        tree = tr.addNext(tree, [p, 1-p])
        s = tr.getPrintable(tree)
        firstLine = s.split('\n')[0]
        assert "0.5" in firstLine and " 0 " in firstLine, "Bad coordinates of first line"
        secondLine = s.split('\n')[1]
        assert "0.3" in secondLine and " 1 " in secondLine, "Bad second line"


if __name__ == "__main__":
    unittest.main()
