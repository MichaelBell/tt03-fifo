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

// Due to Tiny Tapeout and OpenROAD limitations, using the delay gate primitves
// from the sky130 library doesn't work.  This module allows a configurable number
// of inverters to be used to introduce a delay that the synthesis tools don't remove

module delay #( parameter DELAY = 1 ) (
    input A,
    output X
);

`ifdef SIM
    assign #(DELAY*2) X = A;
`else
    wire b[DELAY-1];

    genvar i;
    generate
    for (i = 0; i < DELAY; i = i + 1) begin
        wire mid;

        // Do two inversions to create a delay
        if (i == 0)
            sky130_fd_sc_hd__inv_1 inv_first (
                .Y(mid),
                .A(A)
            );
        else
            sky130_fd_sc_hd__inv_1 inv1 (
                .Y(mid),
                .A(b[i-1])
            );

        if (i == DELAY-1)
            sky130_fd_sc_hd__inv_2 inv_last (
                .Y(X),
                .A(mid)
            );
        else
            sky130_fd_sc_hd__inv_1 inv2 (
                .Y(b[i]),
                .A(mid)
            );
    end
    endgenerate
`endif

endmodule