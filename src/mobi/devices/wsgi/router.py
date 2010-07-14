from webob import Request, Response
import logging


logger = logging.getLogger('playmobile.devices.wsgi.router')


class RouterMiddleware(object):
    """ Middleware to redirect mobile devices to mobile sites

    RouterMiddleWare(app, config_map)

    config_map is a dict where keys are computer site hostnames and values
    mobile site hostnames or urls.
    """
    no_redirect_param_name = '__no_redirect'

    def __init__(self, app, config_map):
        self.app = app
        self._config = self._parse_config(config_map)
        logger.info("playmobile.devices router config :\n %s" %
                    str(self._config))

    def _parse_config(self, config_map):
        config = {}
        for normal_host, mobile_host in config_map.iteritems():
            if mobile_host.startswith('http://')\
                    or mobile_host.startswith('https://'):
                config[normal_host] = mobile_host
            else:
                config[normal_host] = "http://%s/" % mobile_host
        return config

    def __call__(self, environ, start_response):
        port = 80
        hostname = environ.get('HTTP_HOST', '')
        if ":" in hostname:
            hostname, port = hostname.split(':', 1)

        # nothing configure for this host bail out
        if hostname not in self._config:
            return self.app(environ, start_response)

        request = Request(environ)
        no_redirect_param = request.GET.get(self.no_redirect_param_name)
        no_redirect_cookie = request.cookies.get(self.no_redirect_param_name)

        force_no_redirect = no_redirect_param or no_redirect_cookie

        # playmobile.devices middleware has tagged it as mobile
        if request.environ.get('playmobile.devices.is_mobile'):
            if force_no_redirect:
                response = request.get_response(self.app)
                if not no_redirect_cookie:
                    response.set_cookie(
                        self.no_redirect_param_name, 'on', path="/")
                return response(environ, start_response)

            target = self._config[hostname]
            start_response('302 Redirect', [('Location', target,)])
            return []

        return self.app(environ, start_response)


# paste deploy entry point
def router_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        return RouterMiddleware(app, local_conf)

    return filter
