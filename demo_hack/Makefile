# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

all:
	@mkdir -p build
	iverilog -o build/trxpc1_core -c source_files.list -I ${SANIMUT_FPGA_SOURCEDIR}

clean:
	@rm -rf build
	@rm -f results.xml
	@rm -rf sim_build
	@rm -rf __pycache__
