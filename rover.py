import sys
import operator
import copy
import itertools

# There are three algorithms in this file.
# searched_sets() a giant brute force search.
# contiguous_search() a search for contiguous pairs.
# reverse_full() a search that built most of the utility functions
# for searched_sets() with a limitation of depth of 2.
# it only does union checking when there's multiple choices.
# which should be generalizable.
#
# searched_sets() is exponential time with heavy memory use.
#
# Are these two methods comparable to a CS theory type solution?
#
# Potential Improvements.
# -----------------------
# The ideal would be to run all of the fast searches first and throw away
# items in the brute force search that were slower (transfer time)
# than the times computed cheaply.
#
# in likely polynomial time with speedups possible based on memory consumption.
# If I restarted this problem I would have started with clojure because
# it would have let me use lazy sequences to search the full problem space
# simply. potentially optimizing by grouping/sorting some of the pairs
#
# also scipy.kd-tree looks relevant.


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
        if self.soln:
            print '{0:.3f}'.format(self.soln)
        else:
            # If it is impossible to reconstruct the file
            # do not output anything.
            pass

    def compute(self, dl_pairs):
        """calculate time to transfer selected pairs"""
        return reduce(operator.add,
                      map(lambda p: self.time(p[1]-p[0]), dl_pairs))

    def contiguous_search(self, dl_pairs):
        """find potential solution by matching pairs.
         (biased entirely to small transfer size outcomes"""
        self.current_match = 0
        self.used_pairs = []
        s = sorted(dl_pairs)

        def findcontiguous(s):
            for i, p in enumerate(s):
                if p[0] == self.current_match or p[1] == self.numb_bytes:
                    self.current_match = p[1]
                    self.used_pairs.append(s[i])
                    s.pop(i)
                    findcontiguous(s)

        findcontiguous(s)
        self.soln = self.compute(self.used_pairs)
        x = {"total": self.compute(self.used_pairs), "pairs": self.used_pairs}
        return x

    def union_solved(self, pairs):
        """does the list of pairs contain 0-N?"""
        sets = [set(xrange(x[0], x[1])) for x in pairs]
        combined = reduce(lambda x, y: x.union(y), sets)
        if set(xrange(0, self.numb_bytes)).issubset(combined):
            return True
            del combined

    def slow_search(self):
        """get all combinations of all pairs"""
        for group in xrange(1, self.total_chunks+1):
            yield itertools.combinations(self.pairs, group)

    def searched_sets(self):
        """absolutely slow way to ensure an answer"""
        for i in self.slow_search():
            for l in itertools.imap(self.compute,
                                    itertools.ifilter(self.union_solved, i)):
                yield l

    def test_sets(self, permutations, sets):
        """take permutations and sets and combine them
        test for coverage (e.g. 0 - N within the combined set."""
        for i in permutations:
            # unpack
            x, y = sets[i[0]], sets[i[1]]
            if self.union_solved((x, y)):
                yield {"total": self.compute([x, y]),
                       "pairs": [x, y],
                       "group": i}

    def reverse_full(self):
        """Reversed procedure sorting in reverse finding the shortest path"""
        self.current_match = self.numb_bytes
        self.used_pairs = []
        s = sorted(self.pairs, key=lambda x: -x[1])
        self.processed_sets = []

        def mk_set(l):
            """process a list of pairs into sets for analysis"""
            sets = {}
            for item, x in enumerate(l):
                sets[item] = set(xrange(x[0], x[1]))
            permutations = itertools.permutations(sets, 2)
            results = [x for x in test_sets(permutations, l)]

        def findoverlap(s):
            """only looks for one level."""
            for i, p in enumerate(s):
                if p[1] == self.current_match or p[0] == 0:
                    self.current_match = p[0]
                    self.used_pairs.append(s[i])
                    s.pop(i)
                    findoverlap(s)

        findoverlap(s)
        contains_0 = [x for x in self.used_pairs if 0 in x]
        if len(contains_0) > 1:
            self.used_pairs.append([0, 0])
            mk_set(self.used_pairs)
            # pick a proposed solution based on time
            try:
                fastest = min(self.possible_solutions,
                              key=lambda x: x['total'])
                self.soln = fastest['total']
            except ValueError:
                # for non-solvables. apparently not a testcase :(
                sys.exit()
        else:
            self.soln = self.compute(self.used_pairs)

    def naive_method(self):
        self.soln = self.compute(self.pairs)

    def try_both(self):
        """Run both algorithms (forwards and reverse with sets)"""
        self.reverse_full()
        self.possible_solutions.append(self.contiguous_search(self.pairs))
        fastest = min(self.possible_solutions, key=lambda x: x['total'])
        self.soln = fastest['total']
        self.out()

if __name__ == '__main__':
    r = Rover()
    # at what point does engineering become cheating?
    # could send debug info to a HTTP server :P
    # do brute force for kicks
    r.soln = min([x for x in r.searched_sets()])
    r.out()
