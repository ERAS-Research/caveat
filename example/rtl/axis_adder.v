`default_nettype none

module axis_adder #(
  parameter c_WIDTH = 8
) (
  input wire clk,
  input wire rst,

  input  wire [2*c_WIDTH-1:0] s_axis_tdata,
  input  wire                 s_axis_tvalid,
  output reg                  s_axis_tready = 1,

  output reg [2*c_WIDTH-1:0] m_axis_tdata,
  output reg                 m_axis_tvalid = 0,
  input  wire                m_axis_tready
);

always @(posedge clk) begin
  if (m_axis_tvalid && m_axis_tready) begin
    m_axis_tvalid <= 0;
    s_axis_tready <= 1;
  end

  if (s_axis_tvalid && s_axis_tready) begin
    m_axis_tdata <= s_axis_tdata[2*c_WIDTH-1:c_WIDTH]+s_axis_tdata[c_WIDTH-1:0];
    m_axis_tvalid <= 1;
    s_axis_tready <= 0;
  end
end

endmodule
