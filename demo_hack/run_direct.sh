#call directly without recompile, cf. https://docs.cocotb.org/en/stable/custom_flows.html
#$(shell cocotb-config --makefiles)/Makefile.sim
#MODULE=cocotb_tb vvp -M $(cocotb-config --lib-dir) -m $(cocotb-config --lib-name vpi icarus) $SANIMUT_FPGA_SOURCEDIR/trxpc1_core.v
MODULE=cocotb_tb vvp -M $(cocotb-config --lib-dir) -m $(cocotb-config --lib-name vpi icarus) trxpc1_core.v
