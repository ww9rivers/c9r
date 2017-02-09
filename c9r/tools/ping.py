#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##

import getopt, sys
sys.path.append('./')

from net.ping import Ping

def usage():
    """
    Usage:  %s  [options]  [<device> | ...]

    Options:  -h | --help               Print this help message.
              -f | --file=<device-file> Specify a file containing list of devices
                                        Default is STDIN.
              -p | --protocol=<proto>   Specify the protocol to use: icmp, stream,
                                        syn, tcp, udp, or any. Default is %s.
              -s | --size=<integer>     Protocol data size. Maximum is %d.
                                        Default is %d.
              -t | --timeout=<seconds>  Number of seconds for protocol timeout.
                                        Default = %d.
              -u | --unreachable        Report on unreachable hosts.
              -v | --verbose            Print all results.
    """
    sys.stderr.write(usage.__doc__ % (sys.argv[0], Ping.def_proto, Ping.max_datasize, Ping.def_datasize, Ping.def_timeout)+"\n")

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "f:hp:t:uv",
                                   ["file=", "help", "protocol=", "timeout=", "unreachable", "verbose"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(1)

devlist = sys.stdin
proto = Ping.def_proto
timeout = Ping.def_timeout
unreachable = False
verbose = False
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-f", "--file"):
        devlist = os.open(a)
    elif o in ("-p", "--protocol"):
        proto = a
    elif o in ("-t", "--timeout"):
        timeout = a
    elif o in ("-u", "--unreachable"):
        unreachable = True
    elif o in ("-v", "--verbose"):
        verbose = True
    else:
        assert False, "unhandled option"

sonar = Ping(proto)

def ping_host(host):
    echo = sonar.ping(host, timeout, proto)
    if verbose:
        print("Pinging %s ...\t%s"%(host, "OK" if echo else "unreachable"))
    elif echo != unreachable:
        print(host)

if args:
    for host in args:
        ping_host(host)
else:
    for line in devlist:
        ping_host(line.strip())
exit(0)
