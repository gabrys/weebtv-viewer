#!/usr/bin/env python

import subprocess as sp
import random
import sys
import threading as th

READSIZE = 100
PORT_MIN = 10000
PORT_MAX = 60000


class RtmpgwException(Exception):
    def __init__(self, output, returncode):
        self.output = output
        self.returncode = returncode


class RtmpgwThread(th.Thread):
    def run(self):
        cmd = self.cmd

        # Read the rtmpgw output until it says 'Closing connection'.
        # Then send 'q' to the command so it ends.

        while cmd.returncode is None:
            line = cmd.stderr.readline(READSIZE)
            if 'Closing connection' in line:
                cmd.stdin.write('q\n')
                cmd.wait()


def start(cmd, port):
    # Call rtmpgw
    cmd = sp.Popen([cmd, '--sport', str(port)], stdin=sp.PIPE, stderr=sp.PIPE)

    # Read until 'Streaming on' is displayed or until the command exits
    error = False
    error_out = []
    while cmd.returncode is None:
        line = cmd.stderr.readline(READSIZE)
        error_out.append(line)
        cmd.poll()
        if 'Streaming on' in line:
            break

    # If command exited, raise an exception along with its output and exit code
    if cmd.returncode is not None:
        raise RtmpgwException(output=''.join(error_out), returncode=cmd.returncode)

    # All good, let's do the rest in the background
    bg = RtmpgwThread()
    bg.cmd = cmd
    bg.start()


def startOnRandomPort(cmd):
    port = random.randrange(PORT_MIN, PORT_MAX)
    start(cmd, port)
    return port

