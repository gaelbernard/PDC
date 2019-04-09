from anytree import Node, PreOrderIter, LevelOrderIter, findall, RenderTree
import xml.etree.ElementTree as ET

class Tree:
    '''
    The goal is to produce a tree like this:
    Node('/XorLoop', shortname='[XorLoop0]', type='XorLoop')
    ├── Node('/XorLoop/Seq', shortname='[Seq1]', type='Seq')
    │   ├── Node('/XorLoop/Seq/a', shortname='a', type='task')
    │   └── Node('/XorLoop/Seq/Xor', shortname='[Xor3]', type='Xor')
    │       ├── Node('/XorLoop/Seq/Xor/b', shortname='b', type='task')
    │       └── Node('/XorLoop/Seq/Xor/tau', shortname='[tau5]', type='tau')
    ├── Node('/XorLoop/And', shortname='[And6]', type='And')
    │   ├── Node('/XorLoop/And/u', shortname='u', type='task')
    │   └── Node('/XorLoop/And/i', shortname='i', type='task')
    └── Node('/XorLoop/Xor', shortname='[Xor9]', type='Xor')
        ├── Node('/XorLoop/Xor/x', shortname='x', type='task')
        └── Node('/XorLoop/Xor/ tau', shortname=' tau', type='task')
    '''
    def __init__(self):
        self.root = None

    def read_ptml(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        nodes = {}
        for e in root.iter('manualTask'):
            nodes[e.attrib['id']] = Node(e.attrib['name'], id=e.attrib['id'], type='task', shortname=e.attrib['name'])

        i = 0
        for s, t in (('xor', 'Xor'), ('and', 'And'), ('automaticTask', 'tau'), ('xorLoop', 'XorLoop'), ('sequence', 'Seq')):
            for e in root.iter(s):
                nodes[e.attrib['id']] = Node(t, id=e.attrib['id'], type=t, shortname='[{}{}]'.format(t,i))
                i+=1
        for e in root.iter('or'):
            raise ValueError('Or not managed yet...')
        for e in root.iter('parentsNode'):
            parent = nodes[e.attrib['sourceId']]
            child = nodes[e.attrib['targetId']]
            child.parent = parent
            self.root = nodes[root.find('processTree').attrib['root']]
        print (RenderTree(self.root))

