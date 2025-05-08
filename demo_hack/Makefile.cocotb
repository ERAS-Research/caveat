# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

#include sources
VERILOG_SOURCES += $(SANIMUT_FPGA_SOURCEDIR)/trxpc1_core.v
VERILOG_SOURCES += def_sanimut_deployment_configuration.vh

VERILOG_INCLUDE_DIRS += $(SANIMUT_FPGA_SOURCEDIR)
VERILOG_SOURCES += $(SANIMUT_FPGA_SOURCEDIR)/../../../ip_repo/verilog-ethernet/lib/axis/rtl/axis_fifo.v

# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = trxpc1_core

# MODULE is the basename of the Python test file
MODULE = cocotb_tb

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
