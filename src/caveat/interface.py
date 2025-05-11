# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Maps between socket and AXI-Stream
"""

import cocotb
import socket
import threading
import time

from cocotbext.axi import AxiStreamSource, AxiStreamSink, AxiStreamFrame


class SocketAXIS():
    def __init__(self, remote_address: str, remote_port: int, local_port: int,
            axis_sink: AxiStreamSink, axis_source: AxiStreamSource):
        """Initialize socket interface
        """
        self.socket = None
        self.threads = {}
        self.buffer_size = 8192
        self.stop = False

        self.remote_address = remote_address
        self.remote_port = remote_port
        self.local_port = local_port

        self.axis_sink = axis_sink
        self.axis_source = axis_source

        #initiate communications
        self.communication_start()

    def __del__(self):
        """Destructor
        """
        self.communication_stop()

    def communication_start(self):
        """Callback to start communications between interfaces
        """
        #create UDP socket
        if self.socket is not None:
            print('Socket already in use')
            return

        #initialize communication
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', self.local_port))

        #thread for forwarding packets between interfaces
        self.threads['comms'] = threading.Thread(target=self.communication_operation,
                                                      args=())
        self.threads['comms'].start()

        #print status
        print('Socket<>AXIS active')

    def communication_stop(self):
        """Callback to shut communications down
        """
        if self.socket is not None:
            self.stop = True
            for curr_thread in self.threads.values():
                print('joing thread {}'.format(curr_thread), flush=True)
                curr_thread.join()
            self.socket.close()
            self.socket = None
            print('Shutdown complete', flush=True)

    def communication_operation(self):
        """Main thread to pass packets between interfaces
        """
        #set timeout for blocking loop in case of no incoming packets
        self.socket.settimeout(0)

        while not self.stop:
            #forward packets from socket to AXIS
            message = None
            try:
                message = self.socket.recv(self.buffer_size)
                print('SOCK>DEV', list(message), flush=True)
                self.axis_source.send_nowait(message)
            except:
                pass

            #foward packets from AXIS to socket
            try:
                message = self.axis_sink.recv_nowait(compact=True)
                if message:
                    print('DEV>SOCK', list(message), flush=True)
                    self.socket.sendto(bytearray(message), (self.remote_address, self.remote_port))
            except cocotb.queue.QueueEmpty:
                pass
