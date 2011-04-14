============
mobi.devices
============

See documentation at http://mobi.infrae.com/.

``mobi.devices`` is a set of tools that detect mobile user agents. It uses
the `WURFL database <http://wurfl.sourceforce.net>`_ as well as data from
the `MIT mobile project <http://m.mit.edu>`_.

It provides WSGI middleware that can tag a request with information about
the device performing the request.

For best performance, please install **pytc**. It is not a package requirement
since it is not available on all platforms.

Paster example configuration::


    [app:yourapp]
    # This part describes your application
    # use = ...

    [filter:mobidevicedetection]
    # The entry point to use the classifier
    use = egg:mobi.devices#classifier
    # cache the classification on a client side cookie (default: true)
    cookie_cache = true
    # Configure caching (see beaker documentation)
    cache.type = ext:memcached
    cache.url = 127.0.0.1:11211
    cache.lock_dir = /tmp/mobicache
    # Data directory *required*. make sure directory is writable
    # by the user that run the webserver
    var = /var/mobi/db
    # Path to wurfl file. by default it uses the one shipped with
    # this package. however you should use the latest one.
    wurfl_file = /var/mobi/wurfl.xml.gz

    [filter:mobirouter]
    use = egg:mobi.devices#router
    # Redirect mobile devices that connect to infrae.com hostname
    # to m.infrae.com
    infrae.com = http://m.infrae.com/

    [pipeline:main]
    # This part configures the actual WSGI stack
    pipeline = mobidevicedetection mobirouter yourapp

    [server:main]
    # This is the configuration for the paster web server.
    # It must have the same name as the pipeline.
    use = egg:Paste#http
    host = 0.0.0.0
    port = 8080
    threadpool_workers = 7

If you are using Apache with rewrite rules that modify the path and
you want the router to route on the original path, please add the
following rule before any rewrite rule ::

    RewriteRule ^(.*)$ - [E=ORIGINAL_PATH:$1]
    RequestHeader set X_ORIGINAL_PATH %{ORIGINAL_PATH}e

