# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
import bisect


class Marker(type):
    pass

class NOTSET(Marker):
    pass


def common_start(str, str_cmp):
    i = 0
    min_len = min(len(str), len(str_cmp))
    while i < min_len:
        if str[i] != str_cmp[i]:
            break
        i += 1
    return (i, str[0:i])


class Node(object):
    children = None
    infix = None # wikipedia!
    value = None

    def __init__(self, infix, value=NOTSET):
        self.infix = infix
        self.value = value

    def add_child(self, child_node):
        if self.children is None:
            self.children = []
        bisect.insort_right(self.children, child_node)

    def remove_child(self, child_node):
        index = self.children.index(child_node)
        del self.children[index]

    def is_leaf(self):
        return bool(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def __lt__(self, other):
        return self.infix < other.infix

    def display(self, indent=0):
        print "%s|" % (" " * (indent))
        print "%s+--+ '%s' | %s" % (" " * indent, self.infix, str(self.value))
        for child in (self.children or []):
            child.display(indent=indent + 3)

    def search_stackless(self, string):
        stop = len(string) - 1
        node = self
        cursor = 0
        value = None
        value_index = -1

        while cursor <= stop:
            suffix = string[cursor:]
            match_len = 0
            match_node = None
            for child in node.children or []:
                if suffix.startswith(child.infix):
                    match_node = child
                    match_len = len(child.infix)
                    if child.value:
                        value = child
                        value_index = cursor + match_len
                    break

            if match_node is None:
                return value_index, value

            node = match_node
            cursor += match_len

        return value_index, value

    def values(self):
        if self.value is not NOTSET:
            yield self.value
        if self.children:
            for child in self.children:
                for value in child.values():
                    yield value
 
    def search(self, string, buf='', pos=0):
        if string == '':
            return (self, buf + self.infix, pos + len(self.infix))

        for child in self.children or []:
            common_len, common_string = common_start(string, child.infix)
            if common_len:
                if common_len == len(child.infix):
                    return child.search(string[common_len:],
                                         buf + self.infix,
                                         pos + len(self.infix))
                return (child,
                        buf + self.infix + child.infix[:common_len],
                        pos + len(self.infix) + common_len)

        return (self, buf + self.infix, pos + len(self.infix))

    def add(self, string, value=NOTSET):
        if string == '':
            if value is not NOTSET:
                self.value = value
            return self

        for child in self.children or []:
            if child.infix == string:
                return child.add('', value=value)
            common_len, common_suffix = common_start(child.infix, string)
            if common_len:
                if common_len == len(child.infix):
                    return child.add(
                        string[common_len:], value=value)

                self.remove_child(child)
                child.infix = child.infix[common_len:]
                new_base = Node(common_suffix)
                new_base.add_child(child)
                self.add_child(new_base)
                return new_base.add(string[common_len:], value=value)

        node = Node(string, value)
        self.add_child(node)
        return node

    def add_stackless(self, string, value=None):
        """
        A little bit faster but more complicated...
        """
        if not string:
            return

        node = self
        cursor = 0
        stop = len(string)

        while cursor < stop:
            suffix = string[cursor:]
            match_node = None
            match_len = 0

            for child in node.children or []:
                if child.infix == suffix:
                    match_node = child
                    match_len = len(suffix)
                    break
                common_len, common_suffix = common_start(child.infix, suffix)
                if common_len:
                    if common_len == len(child.infix):
                        match_node = child
                        match_len = common_len
                        break
                    node.remove_child(child)
                    child.infix = child.infix[common_len:]
                    new_base = Node(common_suffix)
                    new_base.add_child(child)
                    node.add_child(new_base)
                    match_node = new_base
                    match_len = common_len

            if match_node is None:
                # no node found create leaf
                new_node = Node(suffix, value or string)
                node.add_child(new_node)
                return

            # continue with matching node
            cursor += match_len
            node = match_node
            if cursor == stop:
                match_node.value = value or string


class RadixTree(Node):

    def __init__(self):
        super(RadixTree, self).__init__('')
