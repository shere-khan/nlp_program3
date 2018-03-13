import sys


class Data:
    def __init__(self, index, word, tag, parent):
        self.index = index
        self.word = word
        self.tag = tag
        self.parent = parent

class Tree:
    def __init__(self):
        self.root = None

class Node:
    def __init__(self, val=None):
        self.val = val
        self.children = list()

def createtrees(sentences):
    trees = list()
    for sent in sentences:
        trees.append(createtree(sent))

    return trees

def createtree(sent):
    sent.sort(key=lambda x: x.parent)
    top = sent.pop(0)
    children = [x for x in sent if x.parent == top.parent]
    top.children = children
    tovisit = children
    while tovisit:
        p = tovisit.pop()
        children = [x for x in sent if x.parent == p.parent]
        p.children = children
        tovisit.append(children)

    root = Node()
    root.children = [top]

    return root

def createsentences(filename):
    sentences = list()
    with open(filename, 'r') as f:
        sent = list()
        for line in f:
            if line != '\n':
                sentences.append(sent)
                sent = list()
            else:
                line = line.split()
                sent.append(line)

    return sentences

def main():
    filename = sys.argv[1]
    sentences = createsentences(filename)
    trees = createtrees(sentences)

if __name__ == '__main__':
    main()
