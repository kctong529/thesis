#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0")
        self.cmd("sysctl -w net.ipv4.conf.default.rp_filter=0")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()

def disable_rpf(host):
    host.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0")
    host.cmd("sysctl -w net.ipv4.conf.default.rp_filter=0")

def setup():
    net = Mininet(controller=None, switch=OVSBridge, link=TCLink, build=False)

    info("*** Adding nodes\n")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    r1 = net.addHost("r1", cls=LinuxRouter)
    r2 = net.addHost("r2", cls=LinuxRouter)
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    # path A
    net.addLink(h1, r1, intfName1="h1-eth0", intfName2="r1-eth0",
                params1={"ip": "10.0.1.1/24"}, params2={"ip": "10.0.1.254/24"},
                bw=100, delay="10ms", loss=0)

    # path B
    net.addLink(h1, r2, intfName1="h1-eth1", intfName2="r2-eth0",
                params1={"ip": "10.0.2.1/24"}, params2={"ip": "10.0.2.254/24"},
                bw=100, delay="10ms", loss=0)

    # shared server-side subnet
    net.addLink(r1, s3, intfName1="r1-eth1", params1={"ip": "10.0.3.1/24"},
                bw=100, delay="5ms", loss=0)
    net.addLink(r2, s3, intfName1="r2-eth1", params1={"ip": "10.0.3.254/24"},
                bw=100, delay="5ms", loss=0)
    net.addLink(h2, s3, intfName1="h2-eth0", params1={"ip": "10.0.3.2/24"},
                bw=100, delay="1ms", loss=0)

    info("*** Building network\n")
    net.build()
    s3.start([])

    info("*** Disable reverse-path filtering\n")
    disable_rpf(h1)
    disable_rpf(h2)

    info("*** Configuring routes\n")
    # h1 initially uses path A
    h1.cmd("ip route add 10.0.3.0/24 via 10.0.1.254 dev h1-eth0 src 10.0.1.1")

    # h2 knows how to return to both client-side subnets
    h2.cmd("ip route add 10.0.1.0/24 via 10.0.3.1 dev h2-eth0")
    h2.cmd("ip route add 10.0.2.0/24 via 10.0.3.254 dev h2-eth0")

    info("*** Sanity checks\n")
    info(h1.cmd("ip route"))
    info(h2.cmd("ip route"))
    info("*** Ping server from h1\n")
    info(h1.cmd("ping -c 1 10.0.3.2"))

    info("\n*** Useful commands inside CLI:\n")
    info("h1 ip route replace 10.0.3.0/24 via 10.0.2.254 dev h1-eth1 src 10.0.2.1\n")
    info("h1 ip link set h1-eth0 down\n")
    info("h1 ip link set h1-eth0 up\n")
    info("h1 ip route replace 10.0.3.0/24 via 10.0.1.254 dev h1-eth0 src 10.0.1.1\n")
    info("h1 tc qdisc show dev h1-eth0\n")
    info("h1 tc qdisc show dev h1-eth1\n\n")

    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    setup()