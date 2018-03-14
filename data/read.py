import sys, copy


class Data:
    def __init__(self, index, word, tag, parent):
        self.index = index
        self.word = word
        self.tag = tag
        self.parent = parent

    # def __str__(self):
    #     return 'i: {0} word: {1} tag: {2} p: {3}'.format(self.index, self.word,
    #                                                       self.tag, self.parent)

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
        return 'data: {0}'.format(self.val)

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

def createsentences(filename):
    sents = list()
    with open(filename, 'r') as f:
        sent = list()
        for line in f:
            if line == '\n':
                sents.append(sent)
                sent = list()
            else:
                data = line.split()
                sent.append(Data(index=int(data[0]), word=data[1], tag=data[2],
                                 parent=int(data[3])))

    return sents

if __name__ == '__main__':
    filename = sys.argv[1]
    sentences = createsentences(filename)
    trees = createtrees(sentences)
    # todo search over trees and build arc probabilites
