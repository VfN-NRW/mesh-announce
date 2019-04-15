import providers
import socket

class Source(providers.DataSource):
    def required_args(self):
        return ['batadv_dev', 'batadv_bridge']

    def call(self, batadv_dev, batadv_bridge):
        batadv_dev = batadv_bridge or batadv_dev
        return open('/sys/class/net/' + batadv_dev + '/address').read().strip().replace(':', '')
