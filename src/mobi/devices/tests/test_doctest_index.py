"""

  We have a list of movies.

  >>> len(movies)
  111
  >>> movies[0:3]
  ['The Adventures of Augie March', "All the King's Men", 'American Pastoral']

  We will index them into a radix tree.

  >>> from mobi.devices.index import RadixTree, NOTSET
  >>> tree = RadixTree()
  >>> for i, movie in enumerate(movies):
  ...     words = movie.lower().split(' ')
  ...     for word in words:
  ...         node = tree.add(word)
  ...         if node.value is NOTSET:
  ...             node.value = set()
  ...         node.value.add(movie)

  Let's have a look at the nodes just below the root node (i.e the tree).

  >>> [node.infix for node in tree.children]
  ['1984', '49', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
   'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's',
   't', 'u', 'volcano', 'w', 'you']

  >>> [node.infix for node in tree.children[2].children]
  ['dventures', 'l', 'merican', 'n', 'p', 'r', 's', 't', 'ug']

  Let's try a search.

  >>> node, match, matchlen = tree.search('american')
  >>> (match, matchlen)
  ('american', 8)
  >>> reduce(lambda a,b: a.union(b), node.values())
  set(['An American Tragedy', 'American Pastoral'])

  Search is about longest common prefix.

  >>> node, match, matchlen = tree.search('america')
  >>> (match, matchlen)
  ('america', 7)
  >>> reduce(lambda a,b: a.union(b), node.values())
  set(['An American Tragedy', 'American Pastoral'])

  >>> node, match, matchlen = tree.search('americana')
  >>> (match, matchlen)
  ('american', 8)
  >>> reduce(lambda a,b: a.union(b), node.values())
  set(['An American Tragedy', 'American Pastoral'])

  It matches common prefixes.

  >>> node, match, matchlen = tree.search('heart')
  >>> (match, matchlen)
  ('heart', 5)
  >>> reduce(lambda a,b: a.union(b), node.values())
  set(['Palomar: The Heartbreak Soup Stories',
    'The Heart is A Lonely Hunter',
    'The Heart of the Matter',
    'The Death of the Heart'])

"""

import os.path
import unittest
import doctest

def read_movies():
    movies = []
    file = open(os.path.join(os.path.dirname(__file__), 'movies.txt'), 'r')
    try:
        line = file.readline()
        while line:
            movies.append(line.rstrip())
            line = file.readline()
    finally:
        file.close()
    return movies

def test_suite():
    suite = unittest.TestSuite()
    test = doctest.DocTestSuite(__name__,
                                globs={'movies': read_movies()},
                                optionflags=doctest.NORMALIZE_WHITESPACE |
                                  doctest.ELLIPSIS)
    suite.addTest(test)
    return suite
