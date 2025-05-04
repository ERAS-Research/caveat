# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Hacky demonstration for emulating the sanimut system
"""

import queue
import signal
import socket
import threading
import time

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

#== Helper variables and functions
#-- Miscellaneous application controls
params = {
    'UDPSocket'            : None,
    'bufferSize'           : 8192,
    'threads'              : {},
    'stop'                 : False,
    'queues'               : {},
    }


def read_queue(q):
    """Pop elements off of a queue until nothing remains
    """
    while True:
        try:
            yield q.get_nowait()
        except queue.Empty:
            break

class SocketInterface(object):
    def __init__(self, device_port: int, host_address: str = '127.0.0.1', host_port: int = 20000):
      """Initialize emulator interface via socket
      """
      self.device_port = device_port
      self.host_address = host_address
      self.host_port = host_port
      self.comms_init_func()

    def forward_packet_emulator_to_socket(self, message=None):
        """Place packet/payload on sending queue
        """
        if message:
            print('DEV>SOCK', message)
            params['queues']['send_queue'].put(message)


    def comms_init_func(self):
        """This function initializes the socket and queues
        """
        #create required queues
        params['stop'] = False
        params['queues']['send_queue'] = queue.Queue()
        params['queues']['recv_queue'] = queue.Queue()

        # Create a UDP socket at client side
        if params['UDPSocket'] is not None:
            print('UDP Socket already in use')
            return

        #initialize communication
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.bind(('', self.device_port))
        #UDPSocket.setblocking(0)
        params['UDPSocket'] = udp_socket
        print('UDP server up and listening')

        #thread for handling incoming and outgoing packets
        params['threads']['comms'] = threading.Thread(target=self.comms_operation_func,
                                                      args=())
        params['threads']['comms'].start()

    def comms_stop_func(self):
        """Callback to shutdown everything
        """
        if params['UDPSocket'] is not None:
            #update log and status
            print('Shutting down... ')

            #shut communication down at host
            params['stop'] = True
            for curr_thread in params['threads'].values():
                print('joing thread {}'.format(curr_thread))
                curr_thread.join()
            print('Closing socket')
            params['UDPSocket'].close()
            params['UDPSocket'] = None

            #update log and status
            print('Shutdown complete')

    def comms_operation_func(self, logfilename=None, verbosity=0, timeout=0.01):
        """Main thread to manage sending and receiving packets
        """
        pkg_counter = 0

        #output status to log
        print('Starting comms_func')

        #communications loop
        while not params['stop']:
            #timeout to reduce CPU load
            time.sleep(timeout)

            # Regular operation: check for send (emulator to interface) packet
            try:
                send_message = params['queues']['send_queue'].get_nowait()
                if verbosity > 0:
                    print('Sending - {}'.format(send_message))
                if logfilename is not None:
                    file_desc = open(logfilename, mode='a')
                    file_desc.write('{} : S : {}\n'.format(time.time(), send_message))
                    file_desc.close()
                params['UDPSocket'].sendto(send_message, (self.host_address, self.host_port))
            except queue.Empty:
                pass

            # Regular operation: check for receive (interface to emulator) packet
            try:
                params['UDPSocket'].settimeout(0) #timeout for blocking loop in case of no incoming packets
                recv_message = params['UDPSocket'].recv(params['bufferSize'])

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
                params['queues']['recv_queue'].put(recv_message)
            except Exception as err:
                if verbosity > 0:
                    print('Exception: {}'.format(err))
                    print('Nothing received')
                pass

        #output status to log
        print('Stopping COMMS Loop')


@cocotb.test()
async def trxpc1_core_interface(dut):
    message = None
    #FIXME: add signal_handler

    #create socket interface
    if_socket = SocketInterface(20002)

    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


    #indicate ready to receive outputs to core AXIS
    dut.m_axis_sys_tready.value = int(1)

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 5
    # for cnt in range(1000):
    while not params['stop']:
        #timeout to reduce CPU load
        time.sleep(.001) #FIXME: magic number, slows down emulator processing speed

        await RisingEdge(dut.clk)
        # #place up to three data samples on RF-Rx sampling port
        # #..first transfer
        # # OR
        # #..transfer complete, place new sample
        # if n_sample == 0:
            # n_sample = n_sample + 1
            # dut.s_axis_rfrx_tvalid.value = int(1)
            # dut.s_axis_rfrx_tdata.value = int(100)
        # elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            # n_sample = n_sample + 1
            # dut.s_axis_rfrx_tvalid.value = int(1)
            # dut.s_axis_rfrx_tdata.value = int(100 + n_sample)
        # elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            # dut.s_axis_rfrx_tvalid.value = int(0)


        #check for UDP packets to be forwarded to device, if no active transfer
        if not message:
            try:
                message = params['queues']['recv_queue'].get_nowait()
                print('SOCK>DEV', message)
                print("  sending: ", end="")
            except queue.Empty:
                pass

        #AXI input to device
        #..transfer complete
        if (dut.s_axis_sys_tready.value) and (dut.s_axis_sys_tvalid.value):
            dut.s_axis_sys_tvalid.value = int(0)
            dut.s_axis_sys_tlast.value = int(0)
        #..place new data on interface
        if (message \
        and (dut.s_axis_sys_tready.value or (dut.s_axis_sys_tvalid.value == 0))):
            dut.s_axis_sys_tdata.value = message[0]
            print(message[0], end='..')
            dut.s_axis_sys_tvalid.value = int(1)
            message = message[1:]
            if not message:
                dut.s_axis_sys_tlast.value = int(1)
                print('(done)')

        #receive UDP output from device and forward to interface
        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []
        for pkg in data_buffer:
            if_socket.forward_packet_emulator_to_socket(bytearray(pkg))
        data_buffer = []

    # for ii, pkg in enumerate(data_buffer):
        # print('Pkg#', ii, 'data:', pkg)

    if_socket.comms_stop_func()
