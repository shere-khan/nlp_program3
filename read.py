import sys, copy


class Data:
    def __init__(self, index, word, tag, parent):
        self.index = index
        self.word = word
        self.tag = tag
        self.parent = parent

    def __repr__(self):
        return 'i: {0} word: {1} tag: {2} p: {3}'.format(self.index, self.word,
                                                         self.tag, self.parent)

class Tree:
    def __init__(self, root=None):
        self.root = root

class Node:
    def __init__(self, val=None):
        self.val = val
        self.children = list()

    def __repr__(self):
        return 'val: {0}'.format(self.val)

class Stats:
    def __init__(self):
        self.sentences = 0
        self.tokens = 0
        self.postags = 0
        self.larcs = 0
        self.rarcs = 0
        self.rootarcs = 0

class Oracle:
    def __init__(self):
        self.larcs = dict()
        self.rarcs = dict()
        self.rarcs_alt = dict()

    def initarcs(self, alltags):
        for t1 in sorted(alltags):
            self.larcs[t1] = {}
            self.rarcs[t1] = {}
            for t2 in sorted(alltags):
                self.larcs[t1][t2] = 0
                self.rarcs[t1][t2] = 0

def createtrees(sents):
    trees = list()
    for sent in sents:
        trees.append(createtree(sent))

    return trees

def createtree(sent):
    sent.sort(key=lambda x: x.parent)
    top = Node(sent.pop(0))
    children = [Node(x) for x in sent if x.parent == top.val.index]
    top.children = copy.copy(children)
    tovisit = children
    while tovisit:
        cur = tovisit.pop()
        curchildren = [Node(x) for x in sent if x.parent == cur.val.index]
        cur.children = copy.copy(curchildren)
        tovisit.extend(curchildren)

    root = Node()
    root.children = [top]

    t = Tree(root)

    return t

def createsentences(filename, stats):
    sents = list()
    alltags = set()
    with open(filename, 'r') as f:
        sent = list()
        lines = f.readlines()
        for i in range(len(lines)):
            line = lines[i]
            if line == '\n':
                sents.append(sent)
                sent = list()
                stats.sentences += 1
            else:
                data = line.split()
                stats.tokens += 1
                alltags.add(data[2])
                sent.append(Data(index=int(data[0]), word=data[1], tag=data[2],
                                 parent=int(data[3])))
                if i + 1 == len(lines):
                    sents.append(sent)
                    sent = list()
                    stats.sentences += 1

    stats.postags = len(alltags)

    return sents, alltags

def collect_probs(trees, stats, oracle):
    for t in trees:
        dfs_count_probs(t, stats, oracle)

def dfs_count_probs(tree, stats, oracle):
    top = tree.root.children[0]
    tv = [top]
    stats.rootarcs += 1
    while tv:
        cur = tv.pop()
        for child in cur.children:
            if cur.val.index == child.val.index:
                raise ValueError
            elif cur.val.index > child.val.index:
                # collect left-arc probs
                oracle.larcs[child.val.tag][cur.val.tag] += 1
                stats.larcs += 1
            else:
                # collect right-arc probs
                oracle.rarcs[child.val.tag][cur.val.tag] += 1
                stats.rarcs += 1
        tv.extend(cur.children)

def printarcs(arcs):
    toprint = ''
    for key1, val1 in sorted(arcs.items()):
        print('{0:>6}:'.format(key1), end=' ')
        for key2, val2 in sorted(val1.items()):
            if val2 > 0:
                print('[{0:>4}, {1:>4}]'.format(key2, val2), end=' ')
        print()

def printarcconfusion(larcs, rarcs):
    num_conf_arcs = 0
    for item1, item2 in zip(sorted(rarcs.items()), sorted(larcs.items())):
        print('{0:>6}:'.format(item1[0]), end=' ')
        d1 = item1[1]
        d2 = item2[1]
        if d1 and d2:
            intersect = set(d1.keys()).intersection(set(d2.keys()))
            if intersect:
                for d in sorted(intersect):
                    if d2[d] > 0 and d1[d] > 0:
                        num_conf_arcs += 1
                        print('[{0:>4}, {1:>4}, {2:>4}]'.format(d, d2[d], d1[d]), end=' ')
        print()
    print('\n')
    print("\t\tNumber of confusing arcs = {0}".format(num_conf_arcs))

def printstats(stats):
    print('# sentences : {0}'.format(stats.sentences))
    print('# tokens : {0}'.format(stats.tokens))
    print('# POS tags : {0}'.format(stats.postags))
    print('# Left-Arcs : {0}'.format(stats.larcs))
    print('# Right-Arcs : {0}'.format(stats.rarcs))
    print('# Root-Arcs : {0}'.format(stats.rootarcs))

def parsesentence(sent, oracle):
    stck = list()
    print(stck, end=' ')
    print(sent, end=' ')
    shift(stck, sent)
    while stck:
        print(stck, end=' ')
        print(sent, end=' ')
        if len(sent) == 0 and len(stck) == 1:
            j = stck[-1]
            createarc('ROOT', j)
            break
        if len(stck) < 2:
            shift(stck, sent)
        else:
            i = stck[-2].split('/')
            j = stck[-1].split('/')
            itag = i[1]
            jtag = j[1]

            # Special cases
            if itag[0] == 'V' and (jtag[0] == '.' or jtag[0] == 'R'):
                fst = stck[-2]
                snd = stck.pop(-1)
                createrarc(fst, snd)
            elif len(stck) > 2 and itag[0] == 'I' and jtag[0] == '.':
                swap(stck, sent)
            elif len(sent) > 0 and (itag[0] == 'V' or itag[0] == 'I') and (
                    jtag[0] == 'D' or jtag[0] == 'I' or jtag[0] == 'J' or jtag[
                    0] == 'P' or jtag[0] == 'R'):
                shift(stck, sent)

            else:  # regular case
                larc = oracle.larcs[itag][jtag]
                rarc = oracle.rarcs[itag][jtag]
                if larc > rarc:
                    fst = stck.pop(-2)
                    snd = stck[-1]
                    createlarc(fst, snd)
                elif larc < rarc:
                    fst = stck[-2]
                    snd = stck.pop(-1)
                    createrarc(fst, snd)
                else:
                    print('larc and rarc are equal')
                    raise Exception

def swap(stck, buf):
    print('SWAP')
    buf.insert(0, stck.pop(-2))

def shift(stck, sent):
    print('SHIFT')
    stck.append(sent.pop(0))

def createlarc(fst, snd):
    print('Left-Arc:', end=' ')
    print('{0} <-- {1}'.format(fst, snd))

def createrarc(fst, snd):
    print('Right-Arc:', end=' ')
    print('{0} --> {1}'.format(fst, snd))

def createarc(fst, snd):
    print('{0} --> {1}'.format(fst, snd))


def createsent(file):
    sent = list()
    print('\nInput Sentence:')
    with open(file, 'r') as f:
        for line in f:
            wt = line.split()[0]
            sent.append(wt)
            print(wt, end=' ')

    print('\n')
    return sent

if __name__ == '__main__':
    stats = Stats()
    o = Oracle()
    sentences, alltags = createsentences('wsj-clean.txt', stats)
    o.initarcs(alltags)
    trees = createtrees(sentences)
    collect_probs(trees, stats, o)
    print('\nCorpus Statistics:\n')
    printstats(stats)
    print('\nLeft Arc Array Nonzero Counts\n')
    printarcs(o.larcs)
    print('\nRight Arc ARray Nonzero Counts\n')
    printarcs(o.rarcs)
    print('\nArc Confusion Array:\n')
    printarcconfusion(o.larcs, o.rarcs)
    sent = createsent(sys.argv[1])
    print('\nParsing Actions and Transitions\n')
    parsesentence(sent, o)
