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

module ff_fifo #( parameter DEPTH_BITS = 4, parameter WIDTH = 6 ) (
    input clk,
    input reset_n,
    input write_en,
    input [WIDTH-1:0] data_in,
    input [DEPTH_BITS-1:0] peek,
    input pop,
    output [WIDTH-1:0] data_out,
    output reg empty_n,
    output full_n
);

    // Fifo data
    reg [WIDTH-1:0] fifo_data[0:(1 << DEPTH_BITS) - 1];
    reg [DEPTH_BITS-1:0] write_addr;
    reg [DEPTH_BITS-1:0] read_addr;
    wire [DEPTH_BITS-1:0] next_read_addr = read_addr + 1;

    wire [DEPTH_BITS-1:0] peek_addr = read_addr + peek;

    // Generate all writes to the FIFO data.
    genvar i;
    generate
        for (i = 0; i < (1 << DEPTH_BITS); i = i+1) begin
            always @(posedge clk)
            begin
                if (!reset_n) begin
                    fifo_data[i] <= 0;
                end else begin
                    if (write_addr == i) begin
                        if (write_en) begin
                            // Only actually write if FIFO not full
                            if (full_n || pop) begin
                                fifo_data[i] <= data_in;
                            end
                        end
                        else if (pop && empty_n) begin
                            if (next_read_addr == write_addr) begin
                                fifo_data[i] <= 0;
                            end
                        end
                    end
                end
            end
        end
    endgenerate

    // State tracking and output
    always @(posedge clk)
    begin
        if (!reset_n) begin
            write_addr <= 0;
            read_addr <= 0;
            empty_n <= 0;
            //data_out <= 0;
        end
        else begin
            if (write_en) begin
                // Only actually write if FIFO not full
                if (full_n || pop) begin
                    empty_n <= 1;
                    write_addr <= write_addr + 1;
                end
            end
            else if (pop && empty_n) begin
                if (next_read_addr == write_addr) begin
                    empty_n <= 0;
                end
            end

            if (pop && empty_n) begin
                read_addr <= next_read_addr;
            end

            //data_out <= fifo_data[peek_addr];
        end
    end

    assign data_out = fifo_data[peek_addr];
    assign full_n = !empty_n || read_addr != write_addr;

endmodule