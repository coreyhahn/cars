`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// Testbench for sorter_4 module
// Tests the 4-element sorting network
//////////////////////////////////////////////////////////////////////////////////

module tb_sorter_4;
    parameter WIDTH = 8;  // Use 8-bit for easier visualization
    
    // Inputs
    reg [WIDTH-1:0] in_0;
    reg [WIDTH-1:0] in_1;
    reg [WIDTH-1:0] in_2;
    reg [WIDTH-1:0] in_3;
    
    // Outputs
    wire [WIDTH-1:0] out_0;
    wire [WIDTH-1:0] out_1;
    wire [WIDTH-1:0] out_2;
    wire [WIDTH-1:0] out_3;
    
    // Instantiate the Unit Under Test (UUT)
    sorter_4 #(.WIDTH(WIDTH)) uut (
        .in_0(in_0),
        .in_1(in_1),
        .in_2(in_2),
        .in_3(in_3),
        .out_0(out_0),
        .out_1(out_1),
        .out_2(out_2),
        .out_3(out_3)
    );
    
    integer i, errors;
    
    initial begin
        $display("========================================");
        $display("  4-Element Sorting Network Testbench");
        $display("========================================");
        $display("");
        
        errors = 0;
        
        // Test case 1: Reverse sorted
        in_0 = 4; in_1 = 3; in_2 = 2; in_3 = 1;
        #10;
        $display("Test 1: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 1 || out_1 != 2 || out_2 != 3 || out_3 != 4) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        // Test case 2: Already sorted
        in_0 = 1; in_1 = 2; in_2 = 3; in_3 = 4;
        #10;
        $display("Test 2: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 1 || out_1 != 2 || out_2 != 3 || out_3 != 4) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        // Test case 3: Random order
        in_0 = 2; in_1 = 4; in_2 = 1; in_3 = 3;
        #10;
        $display("Test 3: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 1 || out_1 != 2 || out_2 != 3 || out_3 != 4) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        // Test case 4: Another random order
        in_0 = 3; in_1 = 1; in_2 = 4; in_3 = 2;
        #10;
        $display("Test 4: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 1 || out_1 != 2 || out_2 != 3 || out_3 != 4) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        // Test case 5: Duplicates
        in_0 = 2; in_1 = 2; in_2 = 1; in_3 = 3;
        #10;
        $display("Test 5: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 1 || out_1 != 2 || out_2 != 2 || out_3 != 3) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        // Test case 6: Large numbers
        in_0 = 200; in_1 = 150; in_2 = 175; in_3 = 225;
        #10;
        $display("Test 6: [%0d, %0d, %0d, %0d] -> [%0d, %0d, %0d, %0d]", 
                 in_0, in_1, in_2, in_3, out_0, out_1, out_2, out_3);
        if (out_0 != 150 || out_1 != 175 || out_2 != 200 || out_3 != 225) begin
            $display("  FAILED!");
            errors = errors + 1;
        end else begin
            $display("  PASSED");
        end
        
        $display("");
        $display("========================================");
        if (errors == 0) begin
            $display("  ALL TESTS PASSED!");
        end else begin
            $display("  %0d TESTS FAILED!", errors);
        end
        $display("========================================");
        
        $finish;
    end
      
endmodule
