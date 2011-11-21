import os
import unittest
import httplib
from threading import Thread
from wsgiref.simple_server import make_server, demo_app

import wsgi

_COUNTER = 0


class HttpdThread(Thread):
    """Threading class so WSGI server can run in background"""

    def __init__(self, httpd, *args, **kwargs):
        self.httpd = httpd
        self._terminated = False
        super(HttpdThread, self).__init__(*args, **kwargs)
   
    def run(self):
        while not self._terminated:
            self.httpd.handle_request()

    def terminate(self):
        self._terminated = True


class TestWSGI(unittest.TestCase):

    def setUp(self):
        global _COUNTER
        self.port = 8080 + _COUNTER
        _COUNTER += 1

        self.mapper = wsgi.UAMapper()
        self.extra_environ = dict(
            MEMCACHED_SOCKET='127.0.0.1:11211',
            HTTP_USER_AGENT=''
        )
        def app(environ, start_response):
            environ.update(self.extra_environ)
            result = self.mapper(environ, start_response)
            return result

        # WSGI server takes some time to die, so start each test on a new port.
        self.httpd_thread = HttpdThread(make_server('', self.port, app))
        self.httpd_thread.start()

    def tearDown(self):
        self.httpd_thread.terminate()

        # Lame hack required since WSGI server does not like stdout being
        # yanked from underneath it.
        from time import sleep
        sleep(1)

    def test_responses(self):

        # Make HTTP request for levels of devices
        conn = httplib.HTTPConnection('127.0.0.1', self.port)
    
        # Medium
        self.extra_environ['HTTP_USER_AGENT'] = 'Nokia3100/1.0 (02.70) Profile/MIDP-1.0 Configuration/CLDC-1.0'
        conn.request('GET', '/some/url')
        result = conn.getresponse().read()
        self.assertEquals(result, 'medium')

        # High
        self.extra_environ['HTTP_USER_AGENT'] = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20'
        conn.request('GET', '/some/url')
        result = conn.getresponse().read()
        self.assertEquals(result, 'high')

        # Clean up
        conn.close()

    def test_user_agents(self):

        pth = os.path.split(wsgi.__file__)[0]
        fp = open(pth + '/useragents.txt', 'r')
        try:
            lines = fp.readlines()
        finally:
            fp.close()

        conn = httplib.HTTPConnection('127.0.0.1', self.port)
        for line in lines:
            self.extra_environ['HTTP_USER_AGENT'] = line.strip()
            conn.request('GET', '/some/url')
            result = conn.getresponse().read()
            self.assertEquals(result, 'high')

        conn.close()

if __name__ == '__main__':
    unittest.main()
