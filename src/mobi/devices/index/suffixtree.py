def common_start(str, str_cmp):
    i = -1
    min_len = min(len(str), len(str_cmp)) - 1
    while i < min_len:
        if str[i + 1] != str_cmp[i + 1]:
            break
        i += 1
    return str[0:i+1]


class Node(object):
    children = None
    parent = None
    value = None
    id = None

    def add_child(self, child_node):
        if self.children is None:
            self.children = []
        self.children.append(child_node)
        child_node.parent = self

    def remove_child(self, child_node):
        index = self.children.index(child_node)
        child_node.parent = None
        del self.children[index]

    def is_leaf(self):
        return bool(self.children)


class Tree(object):

    def __init__(self):
        self.index = 0
        self.root = Node()
        self.index = []

    def display(self, io, indent=0, node=None):
        cur = node or self.root
        print "%s|" % (" " * (indent))
        print "%s+--+ %s" % (" " * indent, cur.value)
        for child in (cur.children or []):
            self.display(io, indent=indent + 3, node=child)

    def _add_string_to_index(self, string):
        try:
            return self.index.index(string)
        except ValueError:
            self.index.append(string)
            return len(self.index)

    def _build_and_attach_new_node(self, parent_node, string, suffix):
        new_node = Node()
        new_node.value = suffix
        new_node.id = self._add_string_to_index(string)
        parent_node.add_child(new_node)

    def add_string(self, string):
        node = self.root
        cursor = 0
        stop = len(string) - 1

        while cursor <= stop:
            suffix = string[cursor:]
            match_node = None
            match_len = 0

            for child in node.children or []:
                if child.value == suffix:
                    match_node = child
                    match_len = len(suffix)
                    break

                common_suffix = common_start(child.value, suffix)
                if common_suffix:
                    common_len = len(common_suffix)
                    if common_len == len(child.value):
                        match_node = child
                        match_len = common_len
                        break
                    node.remove_child(child)
                    child.value = child.value[common_len:]
                    # build new parent node
                    new_base = Node()
                    new_base.value = common_suffix
                    # attach old parent
                    new_base.add_child(child)
                    node.add_child(new_base)
                    match_node = new_base
                    match_len = common_len

            if match_node is None:
                # no node found create leaf
                self._build_and_attach_new_node(node, string, suffix)
                return

            # continue with matching node
            cursor += match_len
            node = match_node


if __name__ == '__main__':
    import os
    import sys
    import pdb

    path = os.path.dirname(__file__) + '../data/WURFL/useragents.txt'
    tree = Tree()
    with open(path, 'r') as f:
        line = f.readline().rstrip()
        while line:
            try:
                tree.add_string(line)
            except Exception:
                pdb.post_mortem(sys.exc_info()[2])
            line = f.readline().rstrip()

    tree.display(sys.stdout)