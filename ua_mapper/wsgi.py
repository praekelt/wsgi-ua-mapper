import hashlib
import memcache
from pywurfl.algorithms import TwoStepAnalysis

from ua_mapper import wurfl

class UAMapper(object):
    default = 'medium'
    default_user_agent = ''

    def __init__(self):
        self.mc = None

    def map(self, device):
        """
        Override this method to perform your own custom mapping.
        """
        if device.resolution_width < 240:
            return 'medium'
        else:
            return 'high'

    def __call__(self, environ, start_response):
        # Lazily setup memcache client
        if self.mc is None:
            self.mc = memcache.Client([environ['MEMCACHED_SOCKET'],], debug=0)

        # Resolve user agent. Fallback to default_user_agent member if
        # not present in environ.
        if 'HTTP_USER_AGENT' in environ:
            user_agent = unicode(environ['HTTP_USER_AGENT'])
        else:
            user_agent = unicode(self.default_user_agent)

        key = self.get_cache_key(user_agent)
        
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        
        output = self.mc.get(key)
        if not output:
            output = self.gen_output(user_agent, start_response)
            self.mc.set(key, output)
        
        return [output]
    
    def gen_output(self, user_agent, start_response):
        output = self.default
        devices = wurfl.devices
        search_algorithm = TwoStepAnalysis(devices)
        device = devices.select_ua(user_agent, search=search_algorithm)
        return self.map(device)

    def get_cache_key(self, user_agent):
        return hashlib.md5(user_agent).hexdigest()

application = UAMapper()
