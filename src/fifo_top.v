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

module MichaelBell_6bit_fifo (
  input [7:0] io_in,
  output [7:0] io_out
);

    // Name the inputs
    wire clk = io_in[0];
    wire mode = io_in[1];
    wire reset_n = io_in[1] || io_in[2];  // Reset if in[1] and in[2] both low
    wire pop = (mode == 0) && io_in[3];
    wire [3:0] peek = mode ? 0 : io_in[7:4];
    wire write_en = mode;
    wire [5:0] data_in = io_in[7:2];

    // Fifo data
    reg [5:0] data[0:15];
    reg [3:0] write_addr;
    reg [3:0] read_addr;
    wire [3:0] next_read_addr = read_addr + 1;
    reg empty_n;

    // Simple outputs
    assign io_out[0] = !clk;
    assign io_out[1] = empty_n;

    // Data out, registered so that popped value
    // is presented on outputs when pop occurs.
    reg [5:0] data_out;
    assign io_out[7:2] = data_out;
    wire [3:0] peek_addr = read_addr + peek;

    // Implement the FIFO
    always @(posedge clk)
    begin
        if (!reset_n) begin
            integer i;
            for (i = 0; i < 16; i = i + 1)
                data[i] <= 0;
            write_addr <= 0;
            read_addr <= 0;
            empty_n <= 0;
            data_out <= 0;
        end
        else begin
            if (write_en) begin
                // Only actually write if FIFO not full
                if (!empty_n || read_addr != write_addr) begin
                    data[write_addr] <= data_in;
                    empty_n <= 1;
                    write_addr <= write_addr + 1;
                end
            end
            else if (pop && empty_n) begin
                if (next_read_addr == write_addr) begin
                    empty_n <= 0;
                    data[write_addr] <= 0;
                end
                read_addr <= next_read_addr;
            end

            data_out <= data[peek_addr];
        end
    end

endmodule
