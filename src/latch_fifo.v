/* Copyright (C) 2023 Michael Bell
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

module latch_fifo_entry #( parameter WIDTH = 6 ) (
    input clk,
    input reset_n,
    input write_in,
    input next_is_empty,
    input [WIDTH-1:0] data_in,
    output write_out,
    output empty_out,
    output [WIDTH-1:0] data_out
);
    reg empty;
    reg [WIDTH-1:0] data;
    wire [WIDTH-1:0] data_in_buf;

    // Write out if next entry wants data and we have or are getting data
    assign write_out = next_is_empty && (!empty || write_in);

    always @(posedge clk) begin
        if (!reset_n) begin
            empty <= 1;
        end else begin
            // Empty if writing or currently empty and not filling
            empty <= write_out || (empty && !write_in);
        end
    end

    // Delay input data to ensure we don't read the next data on the falling edge of empty
    delay input_buf[WIDTH-1:0] (.X(data_in_buf), .A(data_in));

    // Latch buffered data
`ifdef SIM
    always @(empty or reset_n or data_in_buf)
        if (!reset_n)
            data <= 0;
        else if (empty)
            data <= data_in_buf;
`else
    sky130_fd_sc_hd__dlrtp_1 latch[WIDTH-1:0] (
        .Q(data),
        .D(data_in_buf),
        .RESET_B(reset_n),
        .GATE(empty)
    );
`endif

    assign data_out = data;
    assign empty_out = empty;

endmodule

module latch_fifo #( parameter DEPTH = 4, parameter WIDTH = 6 ) (
    input clk,
    input reset_n,
    input write_en,
    input [WIDTH-1:0] data_in,
    input pop,
    output [WIDTH-1:0] data_out,
    output write_out,
    output ready,
    output ready_back
);

    wire pop_data [DEPTH:0];
    wire write_data [DEPTH:0];
    wire [WIDTH-1:0] data [DEPTH:0];

    assign pop_data[0] = pop;
    assign write_data[DEPTH] = write_en;
    assign data[DEPTH] = data_in;
    assign data_out = data[0];
    assign write_out = write_data[0];
    assign ready = pop_data[DEPTH-1] && reset_n;
    assign ready_back = pop_data[DEPTH];

    genvar i;
    generate
        for (i = 0; i < DEPTH; i = i + 1) begin
            latch_fifo_entry entry(
                .clk(clk),
                .reset_n(reset_n),
                .write_in(write_data[i+1]),
                .next_is_empty(pop_data[i]),
                .data_in(data[i+1]),
                .write_out(write_data[i]),
                .empty_out(pop_data[i+1]),
                .data_out(data[i])
            );
        end
    endgenerate
endmodule
