import hashlib
import memcache
from pywurfl.algorithms import TwoStepAnalysis

from ua_mapper import wurfl

class UAMapper(object):
    default = 'medium'

    def map(self, device):
        """
        Override this method to perform your own custom mapping.
        """
        if device.resolution_width < 240:
            return 'medium'
        else:
            return 'high'

    def __call__(self, environ, start_response):
        mc = memcache.Client([environ['MEMCACHED_SOCKET'],], debug=0)
        user_agent = unicode(environ['HTTP_USER_AGENT'])
        key = self.get_cache_key(user_agent)
        
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        
        output = mc.get(key)
        if not output:
            output = self.gen_output(user_agent, start_response)
            mc.set(key, output)
        
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
