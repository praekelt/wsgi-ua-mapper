import unittest
import httplib
from threading import Thread
from wsgiref.simple_server import make_server, demo_app

from wsgi import UAMapper


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
        self.mapper = UAMapper()
        self.extra_environ = dict(
            MEMCACHED_SOCKET='127.0.0.1:11211',
            HTTP_USER_AGENT=''
        )

    def test_responses(self):

        def app(environ, start_response):
            environ.update(self.extra_environ)
            result = self.mapper(environ, start_response)
            return result

        thread = HttpdThread(make_server('', 8080, app))
        thread.start()

        # Make HTTP request for levels of devices
        conn = httplib.HTTPConnection('127.0.0.1', 8080)
    
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
        thread.terminate()

        # Warning - lameness alert. WSGI server wants to log all requests and 
        # we cannot yank stdout from underneath it. There must be a better way.
        from time import sleep
        sleep(1)


if __name__ == '__main__':
    unittest.main()
