"""

Router middleware.

Its aims is to redirect mobile clients to a different hostname.

ex: infrae.com => m.infrae.com

It has to be below device detection middleware in the wsgy stack.

>>> from mobi.devices.wsgi.router import RouterMiddleware
>>> app = TestApp()
>>> stack = RouterMiddleware(app, {'infrae.com': 'm.infrae.com'})

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

With the configured host it does not redirects because it is not marked as
a mobile device.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])

If it is marked as a mobile devices then it redirects to mobile site.

>>> request = Request.blank('/')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['mobi.devices.is_mobile'] = 'yes'
>>> request.call_application(stack)
('302 Redirect', [('Location', 'http://m.infrae.com/')], [])

We can force no redirect with a GET param and it will prevent from redirecting
and add a cookie for future requests.

>>> request = Request.blank('/?__no_redirect=yes')
>>> request.environ['HTTP_HOST'] = 'infrae.com:80'
>>> request.environ['mobi.devices.is_mobile'] = 'yes'
>>> request.call_application(stack) # doctest: +NORMALIZE_WHITESPACE
('200 Ok', [('Content-Type', 'text/plain'),
  ('Set-Cookie', '__no_redirect=on; Path=/')], ['hello!'])

The future requests to the site with the cookie will not redirect.

>>> request = Request.blank('/')
>>> request.headers['Cookie'] = '__no_redirect=on'
>>> request.environ['mobi.devices.is_mobile'] = 'yes'
>>> request.call_application(stack)
('200 Ok', [('Content-Type', 'text/plain')], ['hello!'])


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
