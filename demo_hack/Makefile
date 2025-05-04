# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

all:
	iverilog -o trxpc1_core -c source_files.list -I ${SANIMUT_FPGA_SOURCEDIR}

clean:
	@rm -f trxpc1_core
	@rm -f results.xml
	@rm -rf sim_build
	@rm -rf __pycache__
