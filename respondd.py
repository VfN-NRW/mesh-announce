#!/usr/bin/env python3

import socketserver
import argparse
import socket
import struct
import json
import os
from zlib import compress

from providers import get_providers


def get_handler(providers, env):
    class ResponddUDPHandler(socketserver.BaseRequestHandler):
        def multi_request(self, providernames):
            ret = {}
            for name in providernames:
                try:
                    provider = providers[name]
                    ret[provider.name] = provider.call(env)
                except:
                    pass
            return compress(str.encode(json.dumps(ret)))[2:-4]

        def handle(self):
            data = self.request[0].decode('UTF-8').strip()
            socket = self.request[1]
            response = None

            if data.startswith("GET "):
                response = self.multi_request(data.split(" ")[1:])
            else:
                answer = providers[data].call(env)
                if answer:
                    response = str.encode(json.dumps(answer))

            if response:
                socket.sendto(response, self.client_address)

    return ResponddUDPHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="""
      %(prog)s -h
      %(prog)s [-p <port>] [-g <group>] [-i [<group>%]<if0>] [-i [<group>%]<if1> ..] [-d <dir>]""")
    parser.add_argument('-p', dest='port',
                        default=1001, type=int, metavar='<port>',
                        help='port number to listen on (default 1001)')
    parser.add_argument('-g', dest='group',
                        default='ff05::2:1001', metavar='<group>',
                        help='multicast group (default ff05::2:1001)')
    parser.add_argument('-i', dest='mcast_ifaces',
                        action='append', metavar='<iface>',
                        help='interface on which the group is joined')
    parser.add_argument('-d', dest='directory',
                        default='./providers', metavar='<dir>',
                        help='data provider directory (default: $PWD/providers)')
    parser.add_argument('-b', dest='batadv_iface',
                        default='bat0', metavar='<iface>',
                        help='batman-adv interface (default: bat0)')
    parser.add_argument('-m', dest='mesh_ipv4',
                        metavar='<mesh_ipv4>',
                        help='mesh ipv4 address')
    parser.add_argument('-B', dest='batadv_bridge', metavar='<iface>',
                        help='batman-adv bridge')
    args = parser.parse_args()

    socketserver.ThreadingUDPServer.address_family = socket.AF_INET6
    server = socketserver.ThreadingUDPServer(
        ("", args.port),
        get_handler(get_providers(args.directory), {'batadv_dev': args.batadv_iface, 'mesh_ipv4': args.mesh_ipv4, 'batadv_bridge': args.batadv_bridge})
    )

    if args.mcast_ifaces:
        mcast_ifaces = { ifname: group for ifname, group, *_
                        in [ reversed([ args.group ] + ifspec.split('%')) for ifspec
                         in args.mcast_ifaces ] }

        for (inf_id, inf_name) in socket.if_nameindex():
            if inf_name in mcast_ifaces:
                group_bin = socket.inet_pton(socket.AF_INET6, mcast_ifaces[inf_name])
                mreq = group_bin + struct.pack('@I', inf_id)
                server.socket.setsockopt(
                    socket.IPPROTO_IPV6,
                    socket.IPV6_JOIN_GROUP,
                    mreq
                )

    server.serve_forever()
