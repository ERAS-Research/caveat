// Copyright (C) 2025 ERAS Research Group
// Author(s): Murray Ferris, Torsten Reuschel

`default_nettype none

module axis_loopback #(
  parameter c_WIDTH = 8
) (
  input wire clk,

  input wire  [c_WIDTH-1:0] s_axis_tdata,
  input wire                s_axis_tvalid,
  output wire               s_axis_tready,
  input wire                s_axis_tlast,

  output wire [c_WIDTH-1:0] m_axis_tdata,
  output wire               m_axis_tvalid,
  input wire                m_axis_tready,
  output wire               m_axis_tlast
);

assign m_axis_tdata = s_axis_tdata;
assign m_axis_tvalid = s_axis_tvalid;
assign s_axis_tready = m_axis_tready;
assign m_axis_tlast = s_axis_tlast;

endmodule
