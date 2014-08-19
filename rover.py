import sys
import operator
import copy
import itertools
# from collections import namedtuple

# Pair = namedtuple("Pair", ["first", "last"])
class Rover(object):
    """Organize convience functions and algorithms"""
    def __init__(self):
        """collect the stdin and split it into parts"""
        inp = sys.stdin.read().split()
        self.numb_bytes = int(inp[0])
        self.latency = int(inp[1])
        self.bandwidth = float(inp[2])
        self.total_chunks = int(inp[3])
        pairs = inp[4:(self.total_chunks + 4)]

        # modify into list of pairs(also a list)
        # stacked listcomps a bit cleaner than another map/lambda
        self.pairs = [[int(n) for n in x.split(",")] for x in pairs]
        self.possible_solutions = []
        self.soln = False

    def time(self, bytez):
        """time to move a chunk, bytes is a reserved word."""
        return 2*self.latency + (bytez/self.bandwidth)

    def out(self):
        """trigger output"""
        print '{0:.3f}'.format(self.soln)

    def compute(self, dl_pairs):
        """calculate time to transfer selected pairs"""
        # print "compute",dl_pairs
        return reduce(operator.add,
                        map(lambda p: self.time(p[1]-p[0]), dl_pairs))

    def is_fullset(self, dl_pairs):
        """do the pairs contain the original file?"""
        self.current_match = 0
        self.used_pairs = []
        s = sorted(dl_pairs)

        def findcontiguous(s):
            for i, p in enumerate(s):
                # print p[1]
                if p[0] == self.current_match or p[1] == self.numb_bytes:
                    self.current_match = p[1]
                    # print s[i]
                    self.used_pairs.append(s[i])
                    s.pop(i)
                    findcontiguous(s)

        findcontiguous(s)
        # print self.used_pairs
        self.soln = self.compute(self.used_pairs)
        x = {"total": self.compute(self.used_pairs), "pairs": self.used_pairs}
        # print x
        self.possible_solutions.append(x)

    def union_solved(self, pairs):
        sets = [set(xrange(x[0], x[1])) for x in pairs]
        combined = reduce(lambda x,y : x.union(y) ,sets)
        if set(xrange(0, self.numb_bytes)).issubset(combined):
            return True

    def reverse_full(self):
        """Reversed procedure sorting in reverse finding the shortest path"""
        self.current_match = self.numb_bytes
        self.used_pairs = []
        s = sorted(self.pairs, key=lambda x: -x[1])
        self.processed_sets = []
        def test_sets(permutations, sets):
            """take permutations and sets and combine them
            test for coverage (e.g. 0 - N within the combined set."""
            for i in permutations:
                # unpack
                # print sets[i[0]] ^ sets[i[1]]
                x, y = sets[i[0]] , sets[i[1]]
                # print i
                # union of the two sets
                f = sets[i[0]] | sets[i[1]]
                # print 0 in f
                # print (0, self.numb_bytes)
                if set(xrange(0, self.numb_bytes)).issubset(f):
                    a,b = min(x), max(x)+1
                    c,d = min(y), max(y)+1
                    yield {"total": self.compute([[a,b], [c,d]]), 
                            "pairs": [[a,b], [c,d]],
                            "group": i}

        def mk_set(l):
            """process a list of pairs into sets for analysis"""
            sets = {}
            for item, x in enumerate(l):
                sets[item] = set(xrange(x[0], x[1]))
            permutations = itertools.permutations(sets, 2)
            results = [x for x in test_sets(permutations, sets)]
            self.possible_solutions += results
            # print "hello", results
            # self.soln = min(, key=lambda x: x['total'] )
            # print self.soln
            # self.soln = min([x for x in test_sets(permutations, sets)], key=lambda x: x['total'] )
            # self.compute()

        def findoverlap(s):
            """only looks for one level."""
            for i, p in enumerate(s):
                # print p
                if p[1] == self.current_match or p[0] == 0:
                    self.current_match = p[0]
                    # print s[i]
                    self.used_pairs.append(s[i])
                    s.pop(i)
                    findoverlap(s)
        findoverlap(s)
        # print self.used_pairs
        contains_0 = [x for x in self.used_pairs if 0 in x]
        if len(contains_0) > 1:
            self.used_pairs.append([0,0])
            mk_set(self.used_pairs)
            # pick a proposed solution based on time
            fastest = min(self.possible_solutions, key= lambda x: x['total'])
            self.soln = fastest['total']
        else:
            self.soln = self.compute(self.used_pairs)

    def naive_method(self):
        self.soln = self.compute(self.pairs)
    def try_both(self):
        """Run both algorithms (forwards and reverse with sets)"""
        self.reverse_full()
        self.is_fullset(self.pairs)
        # print self.possible_solutions
        fastest = min(self.possible_solutions, key=lambda x: x['total'])
        self.soln = fastest['total']
        self.out()

if __name__ == '__main__':
    r = Rover()
    # print r.pairs
    # result, used_pairs = r.is_fullset(r.pairs)
    # print result, used_pairs
    # print r.compute(r.used_pairs)
    # r.out()
    # r.is_fullset(r.pairs)
    r.try_both()
