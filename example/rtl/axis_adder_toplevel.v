/*

Copyright (c) 2013-2021 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

FIXME: UPDATE COPYRIGHT

*/

// Language: Verilog 2001

`resetall
`timescale 1ns / 1ps
`default_nettype none

/*
 * AXI4-Stream FIFO
 */
module axis_adder_toplevel #(
    parameter DEPTH                = 4096,
    parameter DATA_WIDTH           = 8,
    parameter KEEP_ENABLE          = 1,
    parameter KEEP_WIDTH           = 1,
    parameter LAST_ENABLE          = 1,
    parameter USER_ENABLE          = 1,
    parameter ID_ENABLE            = 0,
    parameter ID_WIDTH             = 8,
    parameter DEST_ENABLE          = 0,
    parameter USER_WIDTH           = 1,
    parameter PIPELINE_OUTPUT      = 2,
    parameter FRAME_FIFO           = 0,
    parameter USER_BAD_FRAME_VALUE = 1'b1,
    parameter USER_BAD_FRAME_MASK  = 1'b1,
    parameter DROP_OVERSIZE_FRAME  = 0,
    parameter DROP_BAD_FRAME       = 0,
    parameter DROP_WHEN_FULL       = 0,
    parameter c_WIDTH              = 4
)

(
    input  wire                   clk,
    input  wire                   rst,

    /*
     * AXI input
     */
    input  wire [DATA_WIDTH-1:0]  s_axis_tdata,
    input  wire [KEEP_WIDTH-1:0]  s_axis_tkeep,
    input  wire                   s_axis_tvalid,
    output wire                   s_axis_tready,
    input  wire                   s_axis_tlast,
    input  wire [ID_WIDTH-1:0]    s_axis_tid,
    input  wire [DEST_WIDTH-1:0]  s_axis_tdest,
    input  wire [USER_WIDTH-1:0]  s_axis_tuser,

    /*
     * AXI output
     */
    output wire [DATA_WIDTH-1:0]  m_axis_tdata,
    output wire [KEEP_WIDTH-1:0]  m_axis_tkeep,
    output wire                   m_axis_tvalid,
    input  wire                   m_axis_tready,
    output wire                   m_axis_tlast,
    output wire [ID_WIDTH-1:0]    m_axis_tid,
    output wire [DEST_WIDTH-1:0]  m_axis_tdest,
    output wire [USER_WIDTH-1:0]  m_axis_tuser,

    /*
     * Status
     */
    output wire                   status_overflow,
    output wire                   status_bad_frame,
    output wire                   status_good_frame,
    
    /*
     * Adder wires
     */
    input wire [c_WIDTH-1:0] value_a,
    input wire [c_WIDTH-1:0] value_b,
    output reg [c_WIDTH:0] result
    
);





axis_fifo #(
        .DEPTH                (DEPTH),
        .DATA_WIDTH           (DATA_WIDTH),
        .KEEP_ENABLE          (KEEP_ENABLE),
        .KEEP_WIDTH           (KEEP_WIDTH),
        .LAST_ENABLE          (LAST_ENABLE),
        .USER_ENABLE          (USER_ENABLE),
        .ID_ENABLE            (ID_ENABLE),
        .ID_WIDTH             (ID_WIDTH),
        .DEST_ENABLE          (DEST_ENABLE),
        .USER_WIDTH           (USER_WIDTH),
        .PIPELINE_OUTPUT      (PIPELINE_OUTPUT),
        .FRAME_FIFO           (FRAME_FIFO),
        .USER_BAD_FRAME_VALUE (USER_BAD_FRAME_VALUE),
        .USER_BAD_FRAME_MASK  (USER_BAD_FRAME_MASK),
        .DROP_OVERSIZE_FRAME  (DROP_OVERSIZE_FRAME),
        .DROP_BAD_FRAME       (DROP_BAD_FRAME),
        .DROP_WHEN_FULL       (DROP_WHEN_FULL),
  
) axis_fifo_inst (
  //input
  .s_axis_tdata(s_axis_tdata),
  .s_axis_tkeep(s_axis_tkeep,
  .s_axis_tvalid(s_axis_tvalid),
  .s_axis_tready(s_axis_tready),
  .s_axis_tlast(s_axis_tlast),
  .s_axis_tid(s_axis_tid),
  .s_axis_tdest(s_axis_tdest),
  .s_axis_tuser(s_axis_tuser),

  //output
  .m_axis_tdata(m_axis_tdata),
  .m_axis_tkeep(m_axis_tkeep),
  .m_axis_tvalid(m_axis_tvalid),
  .m_axis_tready(m_axis_tready),
  .m_axis_tlast(m_axis_tlast),
  .m_axis_tid(m_axis_tid),
  .m_axis_tdest(m_axis_tdest),
  .m_axis_tuser(m_axis_tuser),
  
  //status outputs
  .status_overflow  (status_overflow),
  .status_bad_frame (status_bad_frame),
  .status_good_frame(status_good_frame),

);

adder #(
      .DEPTH                (DEPTH),
      
      
) adder_inst {
  .clk(clk),
  .value_a(value_a),
  .value_b(value_b),
  .result(result),
);

endmodule

`resetall
