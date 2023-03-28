`default_nettype none
`timescale 1ns/1ps

/*
this testbench just instantiates the module and makes some convenient wires
that can be driven / tested by the cocotb test.py
*/

module tb (
    // testbench is controlled by test.py
    input clk,
    input write_en,
    input [5:0] data_in,
    input reset_n,
    input pop,
    input [3:0] peek,
    output inv_clk,
    output empty_n,
    output [5:0] data_out
   );

    // this part dumps the trace to a vcd file that can be viewed with GTKWave
    initial begin
        $dumpfile ("tb.vcd");
        $dumpvars (0, tb);
        #1;
    end

    // wire up the inputs and outputs
    wire [5:0] muxed_in = write_en ? data_in : {peek, pop, reset_n};
    wire [7:0] inputs = {muxed_in, write_en, clk};
    wire [7:0] outputs;
    assign data_out = outputs[7:2];
    assign empty_n = outputs[1];
    assign inv_clk = outputs[0];

    // instantiate the DUT
    MichaelBell_6bit_fifo fifo(
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        .io_in  (inputs),
        .io_out (outputs)
        );

endmodule
