# Provider for Kea DHCP statistics
import providers
import requests


class Source(providers.DataSource):
    def call(self):
        payload = {'service': ['dhcp4'],
                   'command': 'statistic-get-all',
                   'arguments': {}}

        r = requests.post("http://localhost:8080/", json=payload)
        json = r.json()

        default_dict = [[0]]

        response = {
            'dhcp_decline': json[0]['arguments'].get('declined-addresses', default_dict)[0][0] or 0,
            'dhcp_offer': json[0]['arguments'].get('pkt4-offer-sent', default_dict)[0][0] or 0,
            'dhcp_ack': json[0]['arguments'].get('pkt4-ack-sent', default_dict)[0][0] or 0,
            'dhcp_nak': json[0]['arguments'].get('pkt4-nak-sent', default_dict)[0][0] or 0,
            'dhcp_request':
                json[0]['arguments'].get('pkt4-request-received', default_dict)[0][0] or 0,
            'dhcp_discover':
                json[0]['arguments'].get('pkt4-discover-received', default_dict)[0][0] or 0,
            'dhcp_inform': json[0]['arguments'].get('pkt4-inform-received', default_dict)[0][0] or 0,
            'dhcp_release':
                json[0]['arguments'].get('pkt4-release-received', default_dict)[0][0] or 0,
            'leases_allocated_4':
                json[0]['arguments'].get('subnet[1].assigned-addresses', default_dict)[0][0] or 0,
            'leases_pruned_4': json[0]['arguments'].get('reclaimed-leases', default_dict)[0][0] or 0
        }

        return response


def get_source():
    return Source()
