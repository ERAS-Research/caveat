# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory
import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys
# def sanimut_rfstream_sample(channel, sample, bitwidth_channel=8, bitwidth_sample=16):
#     """Build sanimut channel sample [source_channel, 16bit_I, 16bit_Q]
#     """
#     pass

# def GenerateSinWave(dut, clock=none, frequency=none, samples=none):
#     ##bare minimum you need a device.
#     if clock is none:
#         ##check for different clock names
#         clock=getattr(dut,"clk", "false")
#         if clock==false:
#             clock=getattr(dut,"clock", "false")
#             if clock==false:
#                 print("cannot find valid clock for device. please pass device")

def buildmessage(deviceid, messagearray, byte_len, message_size, cnt):

    count=(cnt-1)%5
    masked_device_id=int(deviceid)
    new_message=messagearray[0]
    print("new message is", new_message)
    #print("print integer version of real and imag:", int(new_message.real), int(new_message.imag))
    message_real=np.int16(new_message.real)
    message_imag=np.int16(new_message.imag) ###these are both scalars so should be good. Test sending real and imag simultaneously for now 


    #print("count is", count, cnt)
    #print("iteration #%i: device id is %i masked real is %i. masked imag is %i" %((22000-len(messagearray)),masked_device_id,masked_message_real,message_imag))
    if count==0:
        return masked_device_id
    elif count ==1:
        return ((message_real>>8)&0b11111111)
    elif count ==2:
        return ((message_real)&0b11111111)
    elif count==3:
        return ((message_imag>>8)&0b11111111)
    else:
        return ((message_imag)&0b11111111)
    
    




@cocotb.test(stage=3)
async def trxpc1_core_interface(dut):
    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


    #indicate ready to receive outputs to core AXIS
    dut.m_axis_sys_tready.value = int(1)

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 5
    for cnt in range(1000):
        await RisingEdge(dut.clk)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(100)
        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            n_sample = n_sample + 1
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(100 + n_sample)
        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_rfrx_tvalid.value = int(0)
            

        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []

    for ii, pkg in enumerate(data_buffer):
        print('Pkg#', ii, 'data:', pkg)
   





@cocotb.test(skip=True, stage=2) ##skips and stages for base case but not testfactory stage would have solved the pixellation case before though.
async def trxpc1_core_interface_Single_Transmission(dut, A=0):
    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


    

    #indicate ready to receive outputs to core AXIS
    dut.m_axis_sys_tready.value = int(1)

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 0
    for cnt in range(10000):
        await RisingEdge(dut.clk)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(A)


        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            n_sample = n_sample + 1
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(A)


        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_rfrx_tvalid.value = int(0)

        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []

    print("test", data_buffer)

    assert data_buffer[0][7]==A, print("data packet %i did not equal input %i", data_buffer[0][7], A)
# factory call

# # factory call

# # define factory as a test factory of the module example_tb
# factory = TestFactory(trxpc1_core_interface_Single_Transmission)

# # define possible options for the factory
# factory.add_option("A",[0,1,2,3,4,5,6,7])

# # run the tests!
# factory.generate_tests()



@cocotb.test(stage=1, skip=True)
async def trxpc1_core_interface_Simulated_Data_Transmission(dut):
    
    with h5py.File('sanimut_20250505T221141Z.h5', "r") as f:
        dset = f.get('rx')
        complex_list=[]
        arr=np.array((dset['seq00_00000_000000'])) ##start with one sequence, can be generalized
        for i in range(len(arr)):
            index=arr[i][0]#this gives you an indexable tuple of the real and imaginary. It's actually a numpy void but whatever
            x=complex(index[0],index[1])
            complex_list.append(x)
        complex_list=np.array(complex_list)

    input_ready="m_axis_sys_tready"
    


    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


  

    #indicate ready to receive outputs to core AXIS
    getattr(dut,input_ready).value = int(1)

    # run for 22000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    
    byte_len=5
    samples=22000
    dummy_ID=77
    n_sample_max = samples*byte_len
    message_size=2
    copy_complex_list=complex_list.copy()

    for cnt in range(600000):
        await RisingEdge(dut.clk)
        #print("count is", cnt)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(0)


        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            n_sample = n_sample + 1
            dut.s_axis_rfrx_tvalid.value = int(1)
            
            dut.s_axis_rfrx_tdata.value = int(buildmessage(dummy_ID,copy_complex_list,byte_len, message_size, n_sample))
            if ((n_sample-1)%5==4):
                copy_complex_list=copy_complex_list[1:]
            
        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_rfrx_tvalid.value = int(0)
            
        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []

    ##1 dimenionalize the data into a pattern of I,Q,I,Q
   
    print(dut.s_axis_rfrx_tvalid.value)
    attribute="s_axis_rfrx_tvalid"
    print(getattr(dut, attribute).value)
    all_data=[]
    for chunk in data_buffer:
        counter=0
        for chunklet in chunk:
            if (counter>2):
                all_data.append(chunklet)
            counter+=1
    all_data=all_data[9:]
    print("alldata size", len(all_data))
  
    all_data_scrubbed=[]
    for i in range(len(all_data)):
        if ((i%5==0)&(i%25!=0)): 
            all_data_scrubbed.append(all_data[i])
        if (i%25==0)&(all_data[i]!=77):
            assert 1==2, print("missed bit somewhere")
    #print(all_data_scrubbed)
    print(len(all_data_scrubbed))
    #okay. now you just have 2 bytes for real and 2 for imag, the entire way through
    real_numbers=[]
    imag_numbers=[]

    while (len(all_data_scrubbed)>3):
        real_number=((all_data_scrubbed[0]<<8)|all_data_scrubbed[1])
        if real_number & 0x8000:  
            real_number -= 0x10000  
        real_numbers.append(real_number)
        imag_number=((all_data_scrubbed[2]<<8)|all_data_scrubbed[3])
        if imag_number & 0x8000:  
            imag_number -= 0x10000  
        imag_numbers.append(imag_number)
        all_data_scrubbed.pop(0)
        all_data_scrubbed.pop(0)
        all_data_scrubbed.pop(0)
        all_data_scrubbed.pop(0)

    print(len(real_numbers))
    print(len(imag_numbers))

  

    complex_list_copy=complex_list.copy()
    x=len(complex_list_copy)
    while (len(complex_list_copy)>1):
        index=x-len(complex_list_copy)
        real=complex_list_copy[0].real
        imag=complex_list_copy[0].imag
        # print("real: %i,%i"%(real,real_numbers[index]))
        # print("imag: %i,%i"%(imag, imag_numbers[index]))
        # print("index is",index)
        if(real_numbers[index]!=real):
            assert 1==2, print("real numbers dont match at index %i with actual number %i and returned number %i" %(index, real, real_numbers[index]))
        if(imag_numbers[index]!=imag):
            assert 1==2, print("imag numbers dont match at index %i with actual number %i and returned number %i" %(index, imag, imag_numbers[index]))
        complex_list_copy=complex_list_copy[1:]
    # plt.figure()
    # plt.plot(data_buffer)
    # plt.show()
    
    #now split the data into parts divsible by 1100
    segregated_samples_real=[]
    segregated_samples_imag=[]
    for i in range(int(samples/1100)):
        segregated_samples_real.append(real_numbers[i*1100:((i+1)*1100)-1])
        segregated_samples_imag.append(imag_numbers[i*1100:((i+1)*1100)-1])


    print("lens are %i %i" %(len(segregated_samples_imag), len(segregated_samples_real)))
    assert data_buffer[3]!=1, print("data packet:",data_buffer[3]," did not equal input"  , 0 )

    #plot output waveform
    fig, axs = plt.subplots(10, 1, figsize=(20,25))

    for i in range(10):

        axs[i].plot(segregated_samples_real[i], label='Real', lw=2.5)
        axs[i].plot(segregated_samples_imag[i], label='Im', lw=1.5)
        axs[i].set_xlim([0,len(segregated_samples_real[i])])
        axs[i].set_xlabel("distance (km)")
        





    plt.suptitle('received Ionosonde data')
 

    plt.tight_layout()
    plt.show()
    # plt.savefig("outwave.pdf")
    plt.close()
    





@cocotb.test(stage=3)
async def trxpc1_core_interface_reversed(dut):
    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


    #indicate ready to receive outputs to core AXIS
    dut.m_axis_rftx_tready.value = int(1)

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 21
    handshake_count=0
    handshake=[0,32,0]
    for cnt in range(2000):
        await RisingEdge(dut.clk)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_sys_tvalid.value = int(1)
            dut.s_axis_sys_tdata.value = (handshake[handshake_count])
           
        elif (dut.s_axis_sys_tready.value) and (dut.s_axis_sys_tvalid.value) and (n_sample < n_sample_max):
            handshake_count+=1
            if (handshake_count<3):
                dut.s_axis_sys_tvalid.value = int(1)
                dut.s_axis_sys_tdata.value = (handshake[handshake_count])
                print(int(handshake[handshake_count]))
                
            else:
                dut.m_axis_rftx_tready.value=int(1)
                n_sample = n_sample + 1
               
                dut.s_axis_sys_tvalid.value = int(1)
                dut.s_axis_sys_tdata.value = int(100 + n_sample)
                print("test")
        elif (dut.s_axis_sys_tready.value) and (dut.s_axis_sys_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_sys_tvalid.value = int(0)
            dut.s_axis_sys_tlast.value=int(1)
            
        
        if (dut.m_axis_rftx_tvalid.value):
            data_buffer.append(int(dut.m_axis_rftx_tdata.value))
            print("test")
           
    integer_list=[]
    #need to translate 8 bit messages back to readable numbers
    for value in data_buffer:
        ##all messages are going to be 3 bytes long.
        print(value)
        number1=value&0xff
        print(number1)
        if number1 & 0x00080:  
            number1 -= 0x10 
        print(number1)
        number2=(value>>8)&0xff
        if number2 & 0x0080:  
            number2 -= 0x10 
        number3=(value>>16)&0xff
        if number3 & 0x00080:  
            number3 -= 0x10 
        number4=(value>>24)&0xff
        if number4 & 0x00080:  
            number4 -= 0x10 
        integer_list.append(number1)
        integer_list.append(number2)
        integer_list.append(number3)
        integer_list.append(number4)
        
    print(integer_list)
    






@cocotb.test(skip=True) ##skips and stages for base case but not testfactory stage would have solved the pixellation case before though.
async def trxpc1_core_interface_Sin_Example(dut, A=0):
    # generate a clock

    Generate_sin()

    ##define bit position for the 

    #indicate ready to receive outputs to core AXIS
    dut.m_axis_sys_tready.value = int(1)

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 0
    for cnt in range(10000):
        await RisingEdge(dut.clk)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(A)


        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            n_sample = n_sample + 1
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(A)


        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_rfrx_tvalid.value = int(0)

        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []

    print("test", data_buffer)

    assert data_buffer[0][7]==A, print("data packet %i did not equal input %i", data_buffer[0][7], A)