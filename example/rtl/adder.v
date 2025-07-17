// Copyright (C) 2025 ERAS Research Group
// Author(s): Torsten Reuschel

`default_nettype none

module adder #(
  parameter c_WIDTH = 4
) (
  input wire clk,
  input wire [c_WIDTH-1:0] value_a,
  input wire [c_WIDTH-1:0] value_b,
  output reg [c_WIDTH:0]   result
);

always @(posedge clk) begin
  result <= value_a + value_b;
end

endmodule
