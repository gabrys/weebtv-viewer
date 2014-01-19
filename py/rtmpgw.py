#!/usr/bin/env python

import subprocess as sp
import random
import sys
import time
import threading as th

READSIZE = 100
PORT_MIN = 10000
PORT_MAX = 60000
CONNECT_TIMEOUT = 10


class RtmpgwException(Exception):
    def __init__(self, output, returncode):
        self.output = output
        self.returncode = returncode


class RtmpgwWaitForEndThread(th.Thread):
    def run(self):
        cmd = self.cmd

        # Read the rtmpgw output until it says 'Closing connection'.
        # Then send 'q' to the command so it ends.

        while cmd.returncode is None:
            line = cmd.stderr.readline(READSIZE)
            cmd.poll()
            if line:
                cmd.active = True
            if 'Closing connection' in line:
                cmd.stdin.write('q\n')
                cmd.wait()


class RtmpgwWatchdogThread(th.Thread):
    def run(self):
        time.sleep(CONNECT_TIMEOUT)

        cmd = self.cmd
        if cmd.returncode is None and not cmd.active:
            cmd.stdin.write('q\n')
            cmd.wait()


def start(cmd, params):
    # Call rtmpgw
    cmd = sp.Popen([cmd] + params, stdin=sp.PIPE, stderr=sp.PIPE)

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
    waitForEnd = RtmpgwWaitForEndThread()
    waitForEnd.cmd = cmd
    waitForEnd.start()

    # But if no-one connects to the port within some time, kill the process
    cmd.active = False
    watchdog = RtmpgwWatchdogThread()
    watchdog.cmd = cmd
    watchdog.start()

def startOnRandomPort(cmd, params):
    port = random.randrange(PORT_MIN, PORT_MAX)
    params = params[:] + ['--sport', str(port)]
    start(cmd, params)
    return port

