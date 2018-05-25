import re
import sys
import os

from twisted.names import client, dns, server, hosts as hosts_module, root, cache, resolve
from twisted.internet import reactor
from twisted.python.runtime import platform
from twisted.python import log


def search_file_for_all(hosts_file, name):
    results = []
    try:
        lines = hosts_file.getContent().splitlines()
    except:
        return results

    name = name.lower()
    for line in lines:
        idx = line.find(b'#')
        if idx != -1:
            line = line[:idx]
        if not line:
            continue
        parts = line.split()
        for domain in [s.lower() for s in parts[1:]]:
            if (domain.startswith(b'/') and domain.endswith(b'/') and
                    re.search(domain.strip('/'), name.lower())) or name.lower() == domain.lower():
                results.append(hosts_module.nativeString(parts[0]))
    return results


class Resolver(hosts_module.Resolver):

    def _aRecords(self, name):
        return tuple([
            dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(addr, self.ttl))
            for addr in search_file_for_all(hosts_module.FilePath(self.file), name)
            if hosts_module.isIPAddress(addr)
        ])

def create_resolver(servers=None, resolvconf=None, hosts=None):
    if platform.getType() == 'posix':
        if resolvconf is None:
            resolvconf = b'/etc/resolv.conf'
        if hosts is None:
            hosts = b'/etc/hosts'
        the_resolver = client.Resolver(resolvconf, servers)
        host_resolver = Resolver(hosts)
    else:
        if hosts is None:
            hosts = r'c:\windows\hosts'
        from twisted.internet import reactor
        bootstrap = client._ThreadedResolverImpl(reactor)
        host_resolver = Resolver(hosts)
        the_resolver = root.bootstrap(bootstrap, resolverFactory=client.Resolver)

    return resolve.ResolverChain([host_resolver, cache.CacheResolver(), the_resolver])

class MyDNSServerFactory(server.DNSServerFactory):
    def sendReply(self, protocol, message, address):
        for a in message.answers:
            print("#" + str(a.payload) + str(message.queries))
        if address is None:
            protocol.writeMessage(message)
        else:
            protocol.writeMessage(message, address)

def main(port):
    CURRENT_PATH = os.path.realpath(os.path.dirname(__file__))
    LOG_DIR = os.path.join(CURRENT_PATH, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'super-puper.log')

    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    file = open(LOG_FILE, 'a')
    log.startLogging(file)


    factory = MyDNSServerFactory(
        clients=[create_resolver(servers=[('8.8.8.8', 53)], hosts='hosts')], verbose=0,
    )
    protocol = dns.DNSDatagramProtocol(controller=factory)


    reactor.listenUDP(port, protocol)
    reactor.listenTCP(port, factory)
    reactor.run()


if __name__ == '__main__':
    if len(sys.argv) < 2 or not sys.argv[1].isdigest():
        port = 53
    else:
        port = int(sys.argv[1])
    raise SystemExit(main(port))
