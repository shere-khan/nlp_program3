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
    oracle.rarcs['root'] = {top.val.tag: 1}
    stats.rootarcs += 1

    tv = [top]
    while tv:
        cur = tv.pop()
        for child in cur.children:
            if cur.val.index == child.val.index:
                raise ValueError
            elif cur.val.index > child.val.index:
                # collect left-arc probs
                insert_prob_into_dict(oracle.larcs, child.val.tag, cur.val.tag)
                stats.larcs += 1
            else:
                # collect right-arc probs
                insert_prob_into_dict(oracle.rarcs, child.val.tag, cur.val.tag)
                insert_prob_into_dict(oracle.rarcs_alt, cur.val.tag, child.val.tag)
                stats.rarcs += 1
        tv.extend(cur.children)

def insert_prob_into_dict(probs, key1, key2):
    if key1 not in probs:
        probs[key1] = {key2: 1}
    elif key2 not in probs[key1]:
        probs[key1][key2] = 1
    else:
        probs[key1][key2] += 1

def printarcs(arcs):
    for key1 in sorted(arcs.keys()):
        print('{0:>6}:'.format(key1), end=' ')
        val1 = arcs[key1]
        for key2, val2 in sorted(val1.items()):
            print('[{0:>4}, {1:>4}]'.format(key2, val2), end=' ')
        print()

def printarcconfusion(larcs, rarcs):
    for item1, item2 in zip(sorted(rarcs.items()), sorted(larcs.items())):
        print('{0:>6}:'.format(item1[0]), end=' ')
        d1 = item1[1]
        d2 = item2[1]
        if d1 and d2:
            intersect = set(d1.keys()).intersection(set(d2.keys()))
            if intersect:
                for d in sorted(intersect):
                    print('[{0:>4}, {1:>4}, {2:>4}]'.format(d, d2[d], d1[d]), end=' ')
        print()

def paddict(dstar, d):
    diff = list(dstar.difference(set(d.keys())))
    for k in diff:
        if k in d:
            print('how')
            raise Exception
        else:
            d[k] = None

    return d

def printstats(stats):
    print('# sentences : {0}'.format(stats.sentences))
    print('# tokens : {0}'.format(stats.tokens))
    print('# POS tags : {0}'.format(stats.postags))
    print('# Left-Arcs : {0}'.format(stats.larcs))
    print('# Right-Arcs : {0}'.format(stats.rarcs))
    print('# Root-Arcs : {0}'.format(stats.rootarcs))

def parsesentence(sent, oracle):
    stck = list()
    while sent:
        if len(stck) < 2:
            shift(stck, sent)
        else:
            i = stck[-2].split('/')
            j = stck[-1].split('/')
            larc = oracle.larcs[i[1]][j[1]]
            rarc = oracle.rarcs[i[1]][j[1]]
            if (larc and rarc) and larc > rarc:
                fst = stck.pop(-2)
                snd = stck[-1]
                createlarc(fst, snd)
            elif rarc and not larc:
                fst = stck[-2]
                snd = stck.pop(-1)
                createrarc(fst, snd)
            elif larc and not rarc:
                fst = stck.pop(-2)
                snd = stck[-1]
                createlarc(fst, snd)
            else:
                shift(stck, sent)
    # createarc('ROOT', '-->', stck.pop(0))

def shift(stck, sent):
    print('SHIFT')
    stck.append(sent.pop(0))


def createlarc(fst, snd):
    print('Left-Arc:', end=' ')
    print('{0} <-- {1}'.format(fst, snd))

def createrarc(fst, snd):
    print('Right-Arc:', end=' ')
    print('{0} --> {1}'.format(fst, snd))

def createsent(file):
    sent = list()
    with open(file, 'r') as f:
        for line in f:
            sent.append(line.split()[0])

    return sent

if __name__ == '__main__':
    filename = sys.argv[1]
    stats = Stats()
    o = Oracle()
    sentences, alltags = createsentences(filename, stats)
    trees = createtrees(sentences)
    collect_probs(trees, stats, o)
    print('\nCorpus Statistics:\n')
    printstats(stats)
    print('\nLeft Arc Array Nonzero Counts\n')
    printarcs(o.larcs)
    print('\nRight Arc ARray Nonzero Counts\n')
    printarcs(o.rarcs)
    pad_larc = paddict(alltags, o.larcs)
    pad_rarc = paddict(alltags, o.rarcs)
    print('\nArc Confusion Array:\n')
    printarcconfusion(o.larcs, o.rarcs)
    sent = createsent(sys.argv[2])
    print('\nParsing Actions and Transitions\n')
    parsesentence(sent, o)
