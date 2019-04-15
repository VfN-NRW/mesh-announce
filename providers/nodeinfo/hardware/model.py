import providers
from providers.util import call

class Source(providers.DataSource):
    def call(self):
        return call(['dmidecode', '-s', 'system-manufacturer'])[0] + " " + call(['dmidecode', '-s', 'system-product-name'])[0]
