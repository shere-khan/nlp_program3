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

def createtree(sent):
    sent.sort(key=lambda x: x.parent)
    p = sent.pop(0)
    children = [x for x in sent if x.parent == p.parent]
    p.children = children
    tovisit = children
    while tovisit:
        p = tovisit.pop()
        children = [x for x in sent if x.parent == p.parent]
        p.children = children
        tovisit.append(children)

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        sent = list()
        for line in f:
            if line != '\n':
                createtree(sent)
                sent = list()
            else:
                line = line.split()
                sent.append(line)

if __name__ == '__main__':
    main()
