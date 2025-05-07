# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Generic socket
"""

import queue
import socket
import threading
import time


class SocketInterface():
    def __init__(self, remote_address: str, remote_port: int, local_port: int):
      """Initialize emulator interface via socket
      """
      self.params = {
          'UDPSocket': None,
          'bufferSize': 8192,
          'threads': {},
          'stop': False,
          'queues': {},
          }
      self.remote_address = remote_address
      self.remote_port = remote_port
      self.local_port = local_port
      self.comms_init_func()

    def forward_packet_emulator_to_socket(self, message=None):
        """Place packet/payload on sending queue
        """
        if message:
            print('DEV>SOCK', message)
            self.params['queues']['send_queue'].put(message)


    def comms_init_func(self):
        """This function initializes the socket and queues
        """
        #create required queues
        self.params['stop'] = False
        self.params['queues']['send_queue'] = queue.Queue()
        self.params['queues']['recv_queue'] = queue.Queue()

        #create UDP socket
        if self.params['UDPSocket'] is not None:
            print('UDP Socket already in use')
            return

        #initialize communication
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.bind(('', self.local_port))
        #UDPSocket.setblocking(0)
        self.params['UDPSocket'] = udp_socket
        print('UDP server up and listening')

        #thread for handling incoming and outgoing packets
        self.params['threads']['comms'] = threading.Thread(target=self.comms_operation_func,
                                                      args=())
        self.params['threads']['comms'].start()

    def comms_stop_func(self):
        """Callback to shutdown everything
        """
        if self.params['UDPSocket'] is not None:
            #update log and status
            print('Shutting down... ')

            #shut communication down at host
            self.params['stop'] = True
            for curr_thread in self.params['threads'].values():
                print('joing thread {}'.format(curr_thread))
                curr_thread.join()
            print('Closing socket')
            self.params['UDPSocket'].close()
            self.params['UDPSocket'] = None

            #update log and status
            print('Shutdown complete')

    def comms_operation_func(self, logfilename=None, verbosity=0, timeout=0.01):
        """Main thread to manage sending and receiving packets
        """
        pkg_counter = 0

        #output status to log
        print('Starting comms_func')

        #communications loop
        while not self.params['stop']:
            #timeout to reduce CPU load
            time.sleep(timeout)

            # Regular operation: check for send (emulator to interface) packet
            try:
                send_message = self.params['queues']['send_queue'].get_nowait()
                if verbosity > 0:
                    print('Sending - {}'.format(send_message))
                if logfilename is not None:
                    file_desc = open(logfilename, mode='a')
                    file_desc.write('{} : S : {}\n'.format(time.time(), send_message))
                    file_desc.close()
                self.params['UDPSocket'].sendto(send_message, (self.remote_address, self.remote_port))
            except queue.Empty:
                pass

            # Regular operation: check for receive (interface to emulator) packet
            try:
                self.params['UDPSocket'].settimeout(0) #timeout for blocking loop in case of no incoming packets
                recv_message = self.params['UDPSocket'].recv(self.params['bufferSize'])
                print('SOCK>DEV', recv_message)

                #optional logging of raw packet data
                if logfilename is not None:
                    file_desc = open(logfilename, mode='a')
                    file_desc.write('{} : R : {}\n'.format(time.time(), recv_message))
                    file_desc.close()
                # for name,val in COMM_PACKET.items():
                    # if val == recv_message[0:3]:
                        # if verbosity > 0:
                            # print('{} - {}'.format(name, recv_message[4:]))
                        # break

                #process packet
                #process FPGA response in main thread, may start separate thread if deemed necessary
                self.params['queues']['recv_queue'].put(recv_message)
            except Exception as err:
                if verbosity > 0:
                    print('Exception: {}'.format(err))
                    print('Nothing received')
                pass

        #output status to log
        print('Stopping COMMS Loop')
