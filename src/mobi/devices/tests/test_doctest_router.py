# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
"""

Router middleware.

Its aims is to redirect mobile clients to a different hostname.

ex: infrae.com => m.infrae.com

It has to be below device detection middleware in the wsgy stack.
>>> from mobi.devices.wsgi.router import RouterMiddleware
>>> app = TestApp()
>>> stack = RouterMiddleware(app, {'infrae.com': 'm.infrae.com',
...     'next.infrae.com': 'm.next.infrae.com'})

With a other host it does nothing.

>>> from webob import Request
>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'python.org:80'
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])

With the mobile host it does nothing as well.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'm.infrae.com:80'
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])


>>> iphone_ua = \\
...   u'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_1 like Mac OS X; en-us) ' \\
...   u'AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 ' \\
...   u'Mobile/8B5097d Safari/6531.22.7'


>>> firefox_ua = \\
... u"Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.1) " \\
... u"Gecko/20090624 Firefox/3.5 (.NET CLR 3.5.30729)"


With the configured host it does not redirects because it is not detected as
a mobile device.
>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = firefox_ua
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])

If it is marked as a mobile devices then it redirects to mobile site.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack)
('302 Redirect', [('Location', 'http://m.infrae.com/')], [])

it should work for the other host as well.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'next.infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack) # doctest: +NORMALIZE_WHITESPACE
('302 Redirect', [('Location', 'http://m.next.infrae.com/')], [])

We can force no redirect with a GET param and it will prevent from redirecting
and add a cookie for future requests.
>>> request = Request.blank('/?__no_redirect=yes')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack) # doctest: +NORMALIZE_WHITESPACE
('200 Ok', [('Content-Type', 'text/plain'),
  ('Set-Cookie', '__no_redirect=on; Path=/')], ['hello!'])

The future requests to the site with the cookie will not redirect.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.headers['Cookie'] = '__no_redirect=on'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])

A request without a user agent does nothing as well.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])


If the follow_path option is activated it should keep the path when it
redirects to the mobile site.

>>> stack = RouterMiddleware(app, {
...     'infrae.com': 'm.infrae.com',
...     'next.infrae.com': 'm.next.infrae.com'}, follow_path=True)

>>> request = Request.blank('/path/to/something?param1=joe&name=doe')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack) #doctest: +NORMALIZE_WHITESPACE
('302 Redirect',
[('Location',
  'http://m.infrae.com/path/to/something?param1=joe&name=doe')],
[])

If server use rewrite rules, it can provide X-Original-Path header to allow
to redirect to the original path.

>>> request = Request.blank('/path/to/rewritten_path?param1=joe&name=doe')
>>> request.environ['HTTP_X_ORIGINAL_PATH'] = '/originalpath'
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['HTTP_USER_AGENT'] = iphone_ua
>>> request.call_application(stack) #doctest: +NORMALIZE_WHITESPACE
('302 Redirect',
[('Location',
  'http://m.infrae.com/originalpath?param1=joe&name=doe')],
[])


"""

class TestApp(object):
    """ it only sets the environ attribute. So we can verify some expectations
    on it.
    """
    environ = {}

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response('200 Ok', [('Content-Type', 'text/plain')])
        return ['hello!']


def test_suite():
    import unittest
    import doctest
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(__name__))
    return suite

if __name__ == '__main__':
    import doctest
    doctest.testmod()

