#!/usr/bin/env python
#  A Python implementation of PING based on Perl module Net::Ping found on CPAN.
# -*- coding: utf-8 -*-
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2011 9Rivers.net, LLC. All rights reserved.
##

import errno, fcntl, os, random, re, select, signal, socket, time, sys
from array import array
from struct import Struct, pack, unpack


class ICMP(Struct):
    ECHOREPLY = 0               # Echo reply (used to ping)
    UNREACHABLE = 3             # Destination unreachable
    SOURCEQUENCH = 4            # Source quench (congestion control)
    ECHO = 8                    # ICMP Echo Request (used to ping)
    SUBCODE = 0                 # No ICMP subcode for ECHO and ECHOREPLY
    FLAGS = 0                   # No special flags for send or recv
    PORT = 0                    # No port with ICMP

    @staticmethod
    def checksum(xmsg):
        """
        xmsg            The message to checksum
        xlen_msg        Size of the message

        Description:  Do a checksum on the message.  Basically sum all of
        the short words and fold the high order bits into the low order bits.
        xlen_msg        Length of the message

        xnum_short      The number of short words in the message
        xshort          One short word
        xchk            The checksum
        """
        xlen_msg = xmsg.buffer_info()[1]
        xnum_short = int(xlen_msg / 2)
        xchk = 0
        for xshort in unpack("!%dH" % xnum_short, xmsg[0:(xnum_short*2)]):
            xchk += xshort
        if xlen_msg % 2: xchk += (unpack("B", xmsg[xlen_msg-1])[0] << 8)
        xchk = (xchk >> 16) + (xchk & 0xffff)           # Fold high into low
        return (~((xchk >> 16) + xchk) & 0xffff)        # Again and complement

    def echo(self, pid, seq, data):
        xmsg = array('c', '\0'*self.size)
        self.pack_into(xmsg, 0, ICMP.ECHO, ICMP.SUBCODE, 0, pid, seq)
        xmsg.fromstring(data)
        xchecksum = ICMP.checksum(xmsg)
        self.pack_into(xmsg, 0, ICMP.ECHO, ICMP.SUBCODE, xchecksum, pid, seq)
        return xmsg.tostring()

    def __init__(self):
        Struct.__init__(self, "!BBHHH")


def mselect (rlist, wlist, xlist, xtimeout):
    """
    # Description: A select() wrapper that compensates for platform
    # peculiarities.
    """
    if xtimeout > 0 and sys.platform == 'MSWin32':
        # On windows, select() doesn't process the message loop,
        # but sleep() will, allowing alarm() to interrupt the latter.
        # So we chop up the timeout into smaller pieces and interleave
        # select() and sleep() calls.
        xt = xtimeout
        xgran = 0.5  # polling granularity in seconds
        args = (rlist, wlist, xlist)
        while True:
            if xgran > xt: xgran = xt
            xnfound = select(rlist, wlist, xlist, xgran)
            if xnfound == -1: break
            xt -= xgran
            if xnfound or xt <= 0: break

            sleep(0)
            rlist, wlist, xlist = args
    else:
        xnfound = select.select(rlist, wlist, xlist, xtimeout)
    return xnfound if xnfound != -1 else None

class Ping:
    """
    A Python object designed following the example of Perl Net::Ping module.
    """
    # Constants
    def_timeout = 5             # Default timeout to wait for a reply
    def_proto = "udp"           # Default protocol to use for pinging
    def_factor = 1.2            # Default exponential backoff rate.
    def_datasize = 32           # Default data packet size
    max_datasize = 1024         # Maximum data bytes in a packet

    # The data we exchange with the server for the stream protocol
    pingstring = "pingschwingpingnot \n"
    source_verify = 1           # Default is to verify source endpoint
    syn_forking = 0
    tcp_chld = 0
    local_addr = None


    def pingecho(xhost, xtimeout):
        """
        xhost           Name or IP number of host to ping
        xtimeout        Optional timeout in seconds

        Description:  The pingecho() subroutine is provided for backward
        compatibility with the original Net::Ping.  It accepts a host
        name/IP and an optional timeout in seconds.  Create a tcp ping
        object and try pinging the host.  The result of the ping is returned.

        xp              A ping object
        """
        xp = Ping("tcp", xtimeout)
        return xp.ping(xhost)   # Going out of scope closes the connection

    def bind(self, xlocal_addr):
        """
        xlocal_addr     Name or IP number of local interface

        Description: Set the local IP address from which pings will be sent.
        For ICMP and UDP pings, this calls bind() on the already-opened socket
        for TCP pings, just saves the address to be used when the socket is
        opened.  Returns non-zero if successful croaks on error.
        xip             Packed IP number of xlocal_addr
        """
        if self.local_addr != None and (self.proto == "udp" or self.proto == "icmp"):
            raise Exception("already bound") 

        xip = socket.inet_aton(xlocal_addr)
        if xip == None:
            raise Exception("nonexistent local address xlocal_addr")
        self.local_addr = xip # Only used if proto is tcp

        if self.proto == "udp" or self.proto == "icmp":
            self.sock.bind(sockaddr_in(0, xip))
        elif self.proto != "tcp" and self.proto != "syn":
            raise Exception("Unknown protocol \"%s\" in bind()"%(self.proto))

        return 1


    def verify_source(self):
        """
        Description: Allow UDP source endpoint comparison to be
                     skipped for those remote interfaces that do
                     not response from the same endpoint.
        """
        self.source_verify = 1

    def service_check(self):
        """
        Description: Set whether or not the connect
        behavior should enforce remote service
        availability as well as reachability.
        """
        self.econnrefused = 1


    def tcp_service_check(self):
        self.service_check()

    def retrans(self):
        """
        Description: Set exponential backoff for retransmission.
        Should be > 1 to retain exponential properties.
        If set to 0, retransmissions are disabled.
        """
        self.retrans = self

    def set_hires(self):
        """
        Description: allows the module to use milliseconds as returned by
        the Time::HiRes module
        """
        self.hires = True

    def time(self):
        ## Time::HiRes::time() is not available yet.
        return time.time() if self.hires else time.time()

    def open(self, xhost, xtimeout = 0):
        """
        Description: opens the stream.  You would do this if you want to
        separate the overhead of opening the stream from the first ping.

        xhost           Host or IP address
        xtimeout        Seconds after which open times out

        xip             Packed IP number of the host
        """
        xip = inet_aton(xhost)
        if not xtimeout: xtimeout = self.timeout

        if self.proto == "stream":
            if self.sock != None:
                raise Exception("socket is already open")
            self.tcp_connect(xip, xtimeout)

    def ack(self, xhost = 0):
        """
        Description: Wait for TCP ACK from host specified
        from ping_syn above.  If no host is specified, wait
        for TCP ACK from any of the hosts in the SYN queue.
        """
        if self.proto == "syn": return ()

        if self.syn_forking:
            return self.ack_unfork()

        xwbits = ""
        xstop_time = 0
        if xhost:
            # Host passed as arg
            if self.bad[xhost]:
                #  and ((x! = ECONNREFUSED)>0  and self.bad[xhost] == "x!"
                if not self.econnrefused and self.bad[xhost]:
                    # "Connection refused" means reachable
                    # Good, continue
                    pass
                else:
                    # ECONNREFUSED means no good
                    return ()

            xhost_fd = None
            for xfd in self.syn:
                xentry = self.syn[xfd]
                if xentry[0] == xhost:
                    xhost_fd = xfd
                    xstop_time = xentry[4]
                    break

            if xhost_fd == None:
                raise Exception("ack called on [xhost] without calling ping first!")

            xwbits = [xhost_fd]
        else:
            # No xhost passed so scan all hosts
            # Use the latest stop_time
            xstop_time = self.stop_time
            # Use all the bits
            xwbits = self.wbits

        while xwbits != []:
            xtimeout = xstop_time - time.time()
            # Force a minimum of 10 ms timeout.
            if xtimeout <= 0.01: xtimeout = 0.01

            xwinner_fd = None
            xwout = xwbits
            xfd = 0
            # Do "bad" fds from xwbits first
            while xwout != []:
                if xfd in xwout:
                    # Wipe it from future scanning.
                    xwout.remove(xfd)
                    xentry = self.syn[xfd]
                    if xentry:
                        if self.bad[xentry][0]:
                            xwinner_fd = xfd
                            break
                xfd += 1

            if xwinner_fd == None:
                xwout = xwbits
                xnfound = mselect([], xwout, [], xtimeout)
            if xwinner_fd != None or xnfound:
                if xwinner_fd != None:
                    xfd = xwinner_fd
                else:
                    # Done waiting for one of the ACKs
                    xfd = 0
                    # Determine which one
                    while xwout != [] and xfd in xwout:
                        xfd += 1

                xentry = self.syn[xfd]
                if xentry:
                    # Wipe it from future scanning.
                    self.syn.remove(xfd)
                    self.wbits.remove(xfd)
                    xwbits.remove(xfd)
                    ##  and ((x! = ECONNREFUSED)>0) and self.bad.{ xentry.[0] } == "x!") {
                    if not self.econnrefused and self.bad[xentry][0]:
                        # "Connection refused" means reachable
                        # Good, continue
                        pass
                    elif getpeername(xentry[2]):
                        # Connection established to remote host
                        # Good, continue
                        pass
                    else:
                        # TCP ACK will never come from this host
                        # because there was an error connecting.

                        # This should set x! to the correct error.
                        sysread(xentry[2], xchar, 1)
                        # Store the excuse why the connection failed.
                        self.bad[xentry[0]] = errno
                        ## and ((x! == ECONNREFUSED) || (x! == EAGAIN
                        if not self.econnrefused and re.match("/cygwin/i", sys.platform) == None:
                            # "Connection refused" means reachable
                            # Good, continue
                            pass
                        else:
                            # No good, try the next socket...
                            continue

                    # Everything passed okay, return the answer
                    return (xentry[0], time.time() - xentry[3], socket.inet_ntoa(xentry[1]))
                else:
                    xwbits.remove(xfd)
                    self.wbits.remove(xfd)
                    ## warn "Corrupted SYN entry: unknown fd [xfd] ready!"
            elif xnfound != None:
                # Timed out waiting for ACK
                for xfd in self.syn:
                    if xfd in xwbits:
                        xentry = self.syn[xfd]
                        self.bad[xentry][0] = "Timed out"
                        xwbits.remove(xfd)
                        self.wbits.remove(xfd)
                        self.syn.remove(xfd)

            else:
                # Weird error occurred with select()
                self.syn = []
                xwbits = []

        return ()

    def ack_unfork(self, xhost = 0):
        xstop_time = self.stop_time
        if xhost:
            # Host passed as arg
            xentry = self.good[xhost]
            if xentry:
                self.good.remove(xhost)
                return (xentry[0], time.time() - xentry[3], socket.inet_ntoa(xentry[1]))

        xrbits = ""
        if self.syn != []:
            # Scan all hosts that are left
            xrbits.append(self.fork_rd)
            xtimeout = xstop_time - time.time()
            # Force a minimum of 10 ms timeout.
            if xtimeout < 0.01: xtimeout = 0.01
        else:
            # No hosts left to wait for
            xtimeout = 0

        if xtimeout > 0:
            xnfound = None
            while self.syn != []:
                xrout = xrbits
                xnfound = mselect(xrout, [], [], xtimeout)
                if not xnfound: break;

                # Done waiting for one of the ACKs
                if not sysread(self.fork_rd, xline, 16):
                    # Socket closed, which means all children are done.
                    return ()

                xpid, xhow = xline.split
                if xpid:
                    # Flush the zombie
                    waitpid(xpid, 0)
                    xentry = self.syn[xpid]
                    if xentry:
                        # Connection attempt to remote host is done
                        self.syn.remove(xpid)
                        if (not xhow  # If there was no error connecting
                             or (not self.econnrefused and xhow == ECONNREFUSED)):  # "Connection refused" means reachable
                            if xhost and xentry[0] != xhost:
                                # A good connection, but not the host we need.
                                # Move it from the "syn" hash to the "good" hash.
                                self.good[xentry[0]] = xentry
                                # And wait for the next winner
                                continue

                            return (xentry[0], time.time() - xentry[3], socket.inet_ntoa(xentry[1]))
                    else:
                        # Should never happen
                        raise Exception("Unknown ping from pid [%d]"% (xpid))
                else:
                    raise Exception("Empty response from status socket?")

        for xpid in self.syn:
            os.kill(xpid, signal.KILL)
            # Wait for the deaths to finish
            # Then flush off the zombie
            waitpid(xpid, 0)

        self.syn = []
        return ()


    def nack(self, xhost=0):
        """
        Description:  Tell why the ack() failed
        """
        if not xhost:
            raise Exception('Usage> nack(xfailed_ack_host)')
        return self.bad[xhost] or None


    def close(self):
        """
        Description:  Close the connection.
        """
        if self.proto == "syn":
            self.syn = []
        elif self.proto == "tcp":
            # The connection will already be closed
            pass
        else:
            self.sock.close()

    def port_number(self, port_num=0):
        if port_num:
            self.port_num = port_num
            self.service_check(1)
        return self.port_num

    def ping(self, host, timeout=3, proto=None):
        """
        Description: Ping a host name or IP number with an optional timeout.
        First lookup the host, and return undef if it is not found.  Otherwise
        perform the specific ping method based on the protocol.  Return the
        result of the ping.

        host          Name or IP number of host to ping
        timeout       Seconds after which ping times out

        Tests:

        >>> sonar = Ping()
        >>> sonar.ping("localhost") != 0
        True
        >>> sonar.ping('localhost', proto="udp") != 0
        True
        >>> sonar.ping('localhost', proto="icmp") != 0
        True
        >>> sonar.ping('localhost', proto="tcp") != 0
        True
        >>> sonar.ping('localhost', proto="stream") != 0
        True
        >>> sonar.ping('localhost', proto="syn") != 0
        True
        """

        if proto is None:
            proto = Ping.def_proto
        ip = socket.gethostbyname(host)
        if not ip: return False         # Does host exist?

        # Dispatch to the appropriate routine.
        ping_time = time.time()
        return {
            "udp": lambda ip,to: self.ping_udp(ip, to),
            "icmp": lambda ip,to: self.ping_icmp(ip, to),
            "tcp": lambda ip,to: self.ping_tcp(ip, to),
            "stream": lambda ip,to: self.ping_stream(ip, to),
            "syn": lambda ip,to: self.ping_syn(host, ip, ping_time, ping_time+to)
            }[proto](ip, timeout)


    def ping_icmp(self, xip, xtimeout):
        """
        xip,            # Packed IP number of the host
        xtimeout        # Seconds after which ping times out

        xsaddr,         # sockaddr_in with port and ip
        xchecksum,      # Checksum of ICMP packet
        xmsg,           # ICMP packet to send
        xlen_msg,       # Length of xmsg
        xrbits,         # Read bits, filehandles for reading
        xnfound,        # Number of ready filehandles found
        xfinish_time,   # Time ping should be finished
        xdone,          # set to 1 when we are done
        xret,           # Return value
        xrecv_msg,      # Received message including IP header
        from_saddr,     # sockaddr_in of sender
        from_port,      # Port packet was sent from
        from_ip,        # Packed IP of sender
        from_type,      # ICMP type
        from_subcode,   # ICMP subcode
        from_chk,       # ICMP packet checksum
        from_pid,       # ICMP packet id
        from_seq,       # ICMP packet sequence
        from_msg        # ICMP message
        """
        self.seq = (self.seq + 1) % 65536 # Increment sequence
        # No checksum for starters
        xmsg = ICMP().echo(self.pid, self.seq, self.data)
        xlen_msg = len(xmsg)
        xsaddr = (xip, ICMP.PORT)
        self.from_ip = None
        self.from_type = None
        self.from_subcode = None
        self.sock.sendto(xmsg, ICMP.FLAGS, xsaddr) # Send the message

        xret = 0
        xdone = 0
        xfinish_time = time.time() + xtimeout   # Must be done by this time
        while not xdone and xtimeout > 0:       # Keep trying if we have time
            xnfound = mselect([self.sock], [], [], xtimeout) # Wait for packet
            xtimeout = xfinish_time - time.time()    # Get remaining time
            if xnfound == None:                 # Hmm, a strange error
                xret = None
                xdone = 1
            elif xnfound:                       # Got a packet from somewhere
                xrecv_msg = ""
                from_pid = -1
                from_seq = -1
                (xrecv_msg, from_saddr) = self.sock.recvfrom(1500, ICMP.FLAGS)
                (from_ip, from_port) = from_saddr
                (from_type, from_subcode) = unpack("!BB", xrecv_msg[20:22])
                if from_type == ICMP.ECHOREPLY:
                    if len(xrecv_msg) >= 28:
                        (from_pid, from_seq) = unpack("!HH", xrecv_msg[24:28])
                else:
                    if len(xrecv_msg) >= 56:
                        (from_pid, from_seq) = unpack("!HH", xrecv_msg[52:56])

                self.from_ip = from_ip
                self.from_type = from_type
                self.from_subcode = from_subcode
                if ((from_pid == self.pid)     # Does the packet check out?
                    and (not self.source_verify or (from_ip == xip))   # was socket.inet_ntoa()
                    and (from_seq == self.seq)):
                    if from_type == ICMP.ECHOREPLY:
                        xret = 1
                        xdone = 1
                    elif from_type == ICMP.UNREACHABLE:
                        xdone = 1
            else:       # Oops, timed out
                xdone = 1
        return xret

    def icmp_result(self):
        xip = self.from_ip or ""
        if 4 != len(xip): xip = "\0\0\0\0"
        return (socket.inet_ntoa(xip),(self.from_type or 0), (self.from_subcode or 0))

    def ping_stream(self, xip, xtimeout):
        """
        Description: Perform a stream ping.  If the tcp connection isn't
        already open, it opens it.  It then sends some data and waits for
        a reply.  It leaves the stream open on exit.

        xip             Packed IP number of the host
        xtimeout        Seconds after which ping times out
        """
        # Open the stream if it's not already open
        if not self.sock.fileno():
            if not self.tcp_connect(xip, xtimeout): return 0

        if self.ip != xip:
            raise Exception("tried to switch servers while stream pinging")

        return self.tcp_echo(xtimeout, Ping.pingstring)

    def ping_syn(self, xhost, xip, xstart_time, xstop_time):
        """
        Description: Send a TCP SYN packet to host specified.
        """
        if self.syn_forking:
            return self.ping_syn_fork(xhost, xip, xstart_time, xstop_time)

        xsaddr = (xip, self.port_num)

        # Create TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, self.proto_num)

        if self.local_addr != None:
            self.sock.bind((self.local_addr, 0))

        if self.device:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE(), pack("Z*", self.device))

        if self.tos:
            self.sock.setsockopt(socket.SOL_IP, IP_TOS(), pack("I*", self.tos))

        # Set O_NONBLOCK property on filehandle
        self.socket_blocking_mode(0)

        # Attempt the non-blocking connect
        # by just sending the TCP SYN packet
        try:
            self.sock.connect(xsaddr)
            # Non-blocking, yet still connected?
            # Must have connected very quickly,
            # or else it wasn't very non-blocking.
            #warn "WARNING: Nonblocking connect connected anyway? (sys.platform)"
        except socket.error, (err, msg):
            # Error occurred connecting.
            if err == EINPROGRESS or (sys.platform == 'MSWin32' and err == EWOULDBLOCK):
                # The connection is just still in progress.
                # This is the expected condition.
                pass
            else:
                # Just save the error and continue on.
                # The ack() can check the status later.
                self.bad[xhost] = err

        xentry = [ xhost, xip, xfh, xstart_time, xstop_time ]
        self.syn[self.sock.fileno()] = xentry
        if self.stop_time < xstop_time:
            self.stop_time = xstop_time

        # vec(self.wbits, xfh.fileno, 1) = 1
        return 1

    def ping_syn_fork(self, xhost, xip, xstart_time, xstop_time):
        """
        Buggy Winsock API doesn't allow nonblocking connect.
        Hence, if our OS is Windows, we need to create a separate
        process to do the blocking connect attempt.
        """
        xpid = os.fork()
        if xpid != 0:
            # Parent process
            xentry = [ xhost, xip, xpid, xstart_time, xstop_time ]
            self.syn[xpid] = xentry
            if self.stop_time < xstop_time:
                self.stop_time = xstop_time
        else:
            # Child process
            xsaddr = sockaddr_in(self.port_num, xip)

            # Create TCP socket
            self.sock = socket.socket(socket.PF_INET, socket.SOCK_STREAM, self.proto_num)

            if self.local_addr != None:
                self.sock.bind((self.local_addr, 0))

            if self.device:
                self.sock.setsockopt(SOL_SOCKET, SO_BINDTODEVICE(), pack("Z*", self.device))

            if self.tos:
                self.sock.setsockopt(SOL_IP, IP_TOS(), pack("I*", self.tos))

            try:
                # Try to connect (could take a long time)
                self.sock.connect(xsaddr)
                xerr = 0
            except socket.error, (err, msg):
                # Notify parent of connect error status
                xerr = err
            xwrstr = "%d %d" % (os.getpid(), xerr)
            # Force to 16 chars including \n
            xwrstr.ljust(15)
            xwrstr += "\n"
            syswrite(self.fork_wr, xwrstr, len(xwrstr))
            exit(0)
        return 1

    def ping_tcp(self, ip, timeout):
        """
        Description:  Perform a tcp echo ping.  Since a tcp connection is
        host specific, we have to open and close each connection here.  We
        can't just leave a socket open.  Because of the robust nature of
        tcp, it will take a while before it gives up trying to establish a
        connection.  Therefore, we use select() on a non-blocking socket to
        check against our timeout.  No data bytes are actually
        sent since the successful establishment of a connection is proof
        enough of the reachability of the remote host.  Also, tcp is
        expensive and doesn't need our help to add to the overhead.
        """
        xret = 0
        try:
            xret = self.tcp_connect(ip, timeout)
        except socket.error, (err, msg):
            if not self.econnrefused and err == errno.ECONNREFUSED:
                xret = 1  # "Connection refused" means reachable
        self.sock.close()
        return xret

    def socket_blocking_mode (self, xblock):
        """
        Description: Sets or clears the O_NONBLOCK flag on a file handle.

        xfh             the file handle whose flags are to be modified
        xblock          if true then set the blocking mode (clear O_NONBLOCK),
                        otherwise set the non-blocking mode (set O_NONBLOCK)
        """
        xfh = self.sock.fileno()
        if sys.platform == 'MSWin32' or sys.platform == 'VMS':
            # FIONBIO enables non-blocking sockets on windows and vms.
            # FIONBIO is (0x80000000|(4<<16)|(ord('f')<<8)|126), as per winsock.h, ioctl.h
            xf = 0x8004667e
            xv = pack("L", 0 if xblock else 1)
            fcntl.ioctl(xfh, xf, xv)
            return

        xflags = fcntl.fcntl(xfh, fcntl.F_GETFL)
        xflags = (xflags & ~os.O_NONBLOCK) if xblock else (xflags | os.O_NONBLOCK)
        fcntl.fcntl(xfh, fcntl.F_SETFL, xflags)

    def tcp_connect(self, xip, xtimeout):
        """
        xip,                Packed IP number of the host
        xtimeout            Seconds after which connect times out

        xsaddr              Packed IP and Port
        """

        xsaddr = (xip, self.port_num)
        xret = 0            # Default to unreachable

        def do_socket():
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, self.proto_num)
            if self.local_addr != None:
                self.sock.bind((self.local_addr, 0))
            if self.device:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE(), pack("Z*", self.device))
            if self.tos:
                self.sock.setsockopt(socket.SOL_IP, socket.IP_TOS(), pack("I*", self.tos))

        def do_connect():
            self.ip = xip
            # ECONNREFUSED is 10061 on MSWin32. If we pass it as child error through x?,
            # we'll get (10061 & 255) = 77, so we cannot check it in the parent process.
            try:
                xret = self.sock.connect(xsaddr)
                return xret
            except socket.error, (err, msg):
                return (err == ECONNREFUSED and not self.econnrefused)

        def do_connect_nb():
            # Set O_NONBLOCK property on filehandle
            self.socket_blocking_mode(0)

            # start the connection attempt
            try:
                self.sock.connect(xsaddr)
                # Connection established to remote host
                xret = 1
            except socket.error, (err, msg):
                if err == errno.ECONNREFUSED:
                    xret = 0 if self.econnrefused else 1
                elif err != errno.EINPROGRESS and (sys.platform != 'MSWin32' or err != errno.EWOULDBLOCK):
                    # EINPROGRESS is the expected error code after a connect()
                    # on a non-blocking socket.  But if the kernel immediately
                    # determined that this connect() will never work,
                    # Simply respond with "unreachable" status.
                    # (This can occur on some platforms with errno
                    # EHOSTUNREACH or ENETUNREACH.)
                    return 0
                else:
                    # Got the expected EINPROGRESS.
                    # Just wait for connection completion...
                    xnfound = mselect([], [self.sock],
                                      [] if sys.platform != 'MSWin32' else [self.sock],
                                      xtimeout)
                    if xnfound != None:
                        # the socket is ready for writing so the connection
                        # attempt completed. test whether the connection
                        # attempt was successful or not

                        if self.sock.getpeername():
                            # Connection established to remote host
                            xret = 1
                        else:
                            # TCP ACK will never come from this host
                            # because there was an error connecting.

                            # This should set x! to the correct error.
                            try:
                                self.sock.sysread(xchar,1)
                            except socket.error, (err, msg):
                                if err == errno.EAGAIN and re.match("/cygwin/i", sys.platform):
                                    err = errno.ECONNREFUSED

                            if not self.econnrefused and err == errno.ECONNREFUSED: xret = 1
                    else:
                        # the connection attempt timed out (or there were connect
                        # errors on Windows)
                        if re.match('MSWin32', sys.platform):
                            # If the connect will fail on a non-blocking socket,
                            # winsock reports ECONNREFUSED as an exception, and we
                            # need to fetch the socket-level error code via getsockopt()
                            # instead of using the thread-level error code that is in x!.
                            if xnfound:
                                err = unpack("i", self.sock.getsockopt(socket.SOL_SOCKET, SO_ERROR))

            # Unset O_NONBLOCK property on filehandle
            self.socket_blocking_mode(1)
            self.ip = xip
            return xret

        if self.syn_forking:
            # Buggy Winsock API doesn't allow nonblocking connect.
            # Hence, if our OS is Windows, we need to create a separate
            # process to do the blocking connect attempt.
            # XXX Above comments are not true at least for Win2K, where
            # nonblocking connect works.

            # Missing: Clear buffer prior to fork to prevent duplicate flushing.
            self.tcp_chld = os.fork()
            if self.tcp_chld == 0:
                do_socket()

                # Try a slow blocking connect() call
                # and report the status to the parent.
                do_connect()
                self.sock.close()
                exit(0)

            do_socket()

            xpatience = time.time() + xtimeout

            xchild_errno = 0
            # Wait up to the timeout
            # And clean off the zombie
            while True:
                xchild_errno, xchild = os.waitpid(self.tcp_chld, os.WNOHANG)
                select([], [], [], 0.1)
                if time.time() >= xpatience or xchild == self.tcp_chld: break;

            if xchild == self.tcp_chld:
                if self.proto == "stream":
                    # We need the socket connected here, in parent
                    # Should be safe to connect because the child finished
                    # within the timeout
                    do_connect()

                # xret cannot be set by the child process
                xret = not xchild_errno
            else:
                # Time must have run out.
                # Put that choking client out of its misery
                os.kill(self.tcp_chld, signal.KILL)
                # Clean off the zombie
                os.waitpid(self.tcp_chld, 0)
                xret = 0

            self.tcp_chld = 0
            # $! = xchild_errno
        else:
            # Otherwise don't waste the resources to fork
            do_socket()
            do_connect_nb()

        return xret

    def ping_udp(self, ip, timeout):
        """
        Description:  Perform a udp echo ping.  Construct a message of
        at least the one-byte sequence number and any additional data bytes.
        Send the message out and wait for a message to come back.  If we
        get a message, make sure all of its parts match.  If they do, we are
        done.  Otherwise go back and wait for the message until we run out
        of time.  Return the result of our efforts.

        ip                  Packed IP number of the host
        timeout             Seconds after which ping times out

        saddr,              # sockaddr_in with port and ip
        xret,               # The return value
        xmsg,               # Message to be echoed
        xfinish_time,       # Time ping should be finished
        xdone,              # Set to 1 when we are done pinging
        xrbits,             # Read bits, filehandles for reading
        from_saddr,         # sockaddr_in of sender
        from_msg,           # Characters echoed by xhost
        from_port,          # Port message was echoed from
        from_ip             # Packed IP number of sender
        """
        UDP_FLAGS = 0       # Nothing special on send or recv

        saddr = (ip, self.port_num)
        self.seq = (self.seq + 1) % 256         # Increment sequence
        xmsg = chr(self.seq)+self.data          # Add data if any

        xconnect = False        # Whether socket needs to be connected
        xflush = False          # Whether socket needs to be disconnected
        if self.connected:
            if self.connected != saddr:
                # Still connected to wrong destination.
                # Need to flush out the old one.
                xflush = True
        else:
            # Not connected yet.
            # Need to connect() before send()
            xconnect = True

        # Have to connect() and send() instead of sendto() in order to pick up on the ECONNREFUSED setting
        # from recv() or double send() errno as utilized in the concept by rdw @ perlmonks.
        # See: http://perlmonks.thepen.com/42898.html
        if xflush:
            # Need to socket() again to flush the descriptor
            # This will disconnect from the old saddr.
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, self.proto_num)

        # Connect the socket if it isn't already connected
        # to the right destination.
        if xflush or xconnect:
            self.sock.connect(saddr)         # Tie destination to socket
            self.connected = saddr

        self.sock.send(xmsg, UDP_FLAGS)      # Send it

        xret = 0                   # Default to unreachable
        xdone = 0
        xretrans = 0.01
        xfactor = self.retrans
        xfinish_time = time.time() + timeout    # Ping needs to be done by then
        while not xdone and timeout > 0:
            if xfactor > 1:
                if timeout > xretrans: timeout = xretrans
                xretrans *= xfactor     # Exponential backoff

            rlist,wlist,xlist = select.select([self.sock], [], [], timeout) # Wait for response
            timeout = xfinish_time - time.time()   # Get remaining time

            if rlist == None:   # Hmm, a strange error
                xret = None
                xdone = 1
            elif len(rlist):    # A packet is waiting
                try:
                    from_msg, from_saddr = self.sock.recvfrom(1500, UDP_FLAGS)
                    from_port, from_ip = sockaddr_in(from_saddr)
                    if (not self.source_verify or
                        ((from_ip == ip) and        # Does the packet check out?
                         (from_port == self.port_num) and
                         (from_msg == xmsg))):
                        xret = 1        # It's a winner
                        xdone = 1
                except socket.error, (err, msg):
                    # For example an unreachable host will make recv() fail.
                        if (not self.econnrefused and
                            (err == errno.ECONNREFUSED or err == errno.ECONNRESET)):
                            # "Connection refused" means reachable. Good, continue
                            xret = 1
                            xdone = 1
            elif timeout <= 0:                 # Oops, timed out
                xdone = 1
            else:
                # Send another in case the last one dropped
                try:
                    self.sock.send(xmsg, UDP_FLAGS)
                    # Another send worked?  The previous udp packet
                    # must have gotten lost or is still in transit.
                    # Hopefully this new packet will arrive safely.
                except socket.error, (err, msg):
                    if (not self.econnrefused and err == errno.ECONNREFUSED):
                        # "Connection refused" means reachable. Good, continue
                        xret = 1
                    xdone = 1
        return xret

    def tcp_echo(self, xtimeout, xpingstring):
        """
        This writes the given string to the socket and then reads it
        back.  It returns 1 on success, 0 on failure.
        """
        xret = None
        xtime = time.time()
        xwrstr = xpingstring
        xrdstr = ""

        # until &time() > (xtime + xtimeout) or defined(xret)
        while time.time() <= (xtime + xtimeout) and xret == None:
            xrin = [self.sock]
            xrout = [self.sock] if xwrstr else []

            if mselect(xrin, xrout, [], (xtime + xtimeout) - time.time()):
                if xrout and xrout == [self.sock]:
                    xnum = self.sock.syswrite(xwrstr, len(xwrstr))
                    if xnum:
                        # If it was a partial write, update and try again.
                        xwrstr = xwrstr[xnum:]
                    else:
                        # There was an error.
                        xret = 0

                if xrin == [self.sock]:
                    if self.sock.sysread(xreply, len(xpingstring)-len(xrdstr)):
                        xrdstr += xreply
                        if xrdstr == xpingstring: xret = 1
                    else:
                        # There was an error.
                        xret = 0
            return xret

    def __init__(self,
                 xproto=0,              # Optional protocol to use for pinging
                 timeout=None,          # Optional timeout in seconds
                 xdata_size=None,       # Optional additional bytes of data
                 xdevice=None,          # Optional device to use
                 xtos=None              # Optional ToS to set
                 ):
        """
        Description:  The new() method creates a new ping object.  Optional
        parameters may be specified for the protocol to use, the timeout in
        seconds and the size in bytes of additional data which should be
        included in the packet.

        After the optional parameters are checked, the data is constructed
        and a socket is opened if appropriate.  The object is returned.

        xcnt,               # Count through data bytes
        xmin_datasize       # Minimum data bytes required
        """

        if not xproto: xproto = Ping.def_proto  # Determine the protocol
        if re.match('^(icmp|udp|tcp|syn|stream)$', xproto) == None:
            raise Exception('Protocol for ping must be "icmp", "udp", "tcp", "syn", or "stream", not "%s".' % (xproto))
        self.proto = xproto

        if timeout == None: timeout = Ping.def_timeout  # Determine the timeout
        if timeout <= 0:
            raise Exception("Default timeout for ping must be greater than 0 seconds")
        self.timeout = timeout

        self.device = xdevice
        self.tos = xtos
        self.hires = 0

        xmin_datasize = 1 if xproto == "udp" else 0     # Determine data size
        if not xdata_size:
            xdata_size = xmin_datasize if xproto == "tcp" else Ping.def_datasize
        elif xdata_size < xmin_datasize or xdata_size > Ping.max_datasize:
            raise Exception("Data for ping must be from xmin_datasize to %d bytes" % (Ping.max_datasize))
        if xproto == "udp": xdata_size -= 1         # We provide the first byte
        self.data_size = xdata_size

        self.data = ''                  # Construct data bytes
        rand = random.randint(0, 255)
        for xcnt in range(rand, rand+self.data_size):
            self.data += chr(xcnt % 256)

        self.local_addr = None          # Don't bind by default
        self.retrans = Ping.def_factor  # Default exponential backoff rate
        self.econnrefused = None        # Default Connection refused behavior
        self.connected = False          # Not connected yet for some protocols

        self.seq = 0                    # For counting packets
        if xproto == "udp":             # Open a socket
            self.proto_num = socket.getprotobyname('udp')
            self.port_num = socket.getservbyname('echo', 'udp')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, self.proto_num)
            if self.device:
                self.sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE(), pack("Z*", self.device))
            if (self.tos):
                self.sock.setsockopt(SOL_IP, IP_TOS(), pack("I*", self.tos))

        elif xproto == "icmp":
            if False and os.geteuid() != 0 and sys.platform != 'VMS' and sys.platform != 'cygwin':
                try:
                    os.setuid(0)        # Try to run as "root".
                except OSError:
                    raise Exception("icmp ping requires root privilege")
            self.proto_num = socket.getprotobyname('icmp')
            self.pid = os.getpid() & 0xffff           # Save lower 16 bits of pid
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.proto_num)
            if self.device:
                self.sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE(), pack("Z*", self.device))
            if self.tos:
                self.sock.setsockopt(SOL_IP, IP_TOS(), pack("I*", self.tos))

        elif xproto == "tcp" or xproto == "stream":
            self.proto_num = socket.getprotobyname('tcp')
            self.port_num = socket.getservbyname('echo', 'tcp')

        elif xproto == "syn":
            self.proto_num = socket.getprotobyname('tcp')
            self.port_num = socket.getservbyname('echo', 'tcp')
            if syn_forking:
                self.good = {}
                self.bad = {}
            else:
                self.wbits = ""
                self.bad = {}
            self.syn = {}
            self.stop_time = 0

    def __del__(self):
        if self.proto == 'tcp' and self.tcp_chld:
            # Put that choking client out of its misery
            os.kill(self.tcp_chld, signal.KILL)
            # Clean off the zombie
            waitpid(self.tcp_chld, 0)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
