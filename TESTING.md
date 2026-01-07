# Testing Generated Verilog

## Quick Verification

The generated Verilog modules are syntactically correct and can be simulated or synthesized.

## Simulation with Icarus Verilog

If you have Icarus Verilog installed:

```bash
# Generate a sorting network
python -c "
from sorting_network import find_optimal_network
net = find_optimal_network(4)
with open('sorter_4.v', 'w') as f:
    f.write(net.to_verilog('sorter_4'))
"

# Compile and simulate
iverilog -o sorter_sim sorter_4.v tb_sorter_4.v
vvp sorter_sim
```

Expected output:
```
========================================
  4-Element Sorting Network Testbench
========================================

Test 1: [4, 3, 2, 1] -> [1, 2, 3, 4]
  PASSED
Test 2: [1, 2, 3, 4] -> [1, 2, 3, 4]
  PASSED
Test 3: [2, 4, 1, 3] -> [1, 2, 3, 4]
  PASSED
...
========================================
  ALL TESTS PASSED!
========================================
```

## Synthesis for FPGA

### Using Xilinx Vivado

1. Create a new Vivado project
2. Add the generated `.v` file to your project
3. Set top module to your sorter
4. Run synthesis

```tcl
# Vivado TCL commands
read_verilog sorter_4.v
synth_design -top sorter_4 -part xc7a35tcpg236-1
report_utilization
report_timing
```

### Using Intel Quartus

1. Create a new Quartus project
2. Add the `.v` file to the project
3. Compile the design

```
quartus_map sorter_4
quartus_fit sorter_4
quartus_asm sorter_4
quartus_sta sorter_4
```

### Using Lattice Diamond

1. Create new project
2. Add source files
3. Synthesize and implement

## Creating a Pipelined Version

The generated Verilog is combinational. To create a pipelined version:

```verilog
module sorter_4_pipelined #(
    parameter WIDTH = 32
) (
    input wire clk,
    input wire rst_n,
    input wire [WIDTH-1:0] in_0,
    input wire [WIDTH-1:0] in_1,
    input wire [WIDTH-1:0] in_2,
    input wire [WIDTH-1:0] in_3,
    output reg [WIDTH-1:0] out_0,
    output reg [WIDTH-1:0] out_1,
    output reg [WIDTH-1:0] out_2,
    output reg [WIDTH-1:0] out_3
);

    wire [WIDTH-1:0] stage0_0, stage0_1, stage0_2, stage0_3;
    reg [WIDTH-1:0] stage0_0_r, stage0_1_r, stage0_2_r, stage0_3_r;
    
    wire [WIDTH-1:0] stage1_0, stage1_1, stage1_2, stage1_3;
    reg [WIDTH-1:0] stage1_0_r, stage1_1_r, stage1_2_r, stage1_3_r;
    
    wire [WIDTH-1:0] stage2_0, stage2_1, stage2_2, stage2_3;
    
    // Layer 0 (combinational)
    assign stage0_0 = (in_0 < in_1) ? in_0 : in_1;
    assign stage0_1 = (in_0 < in_1) ? in_1 : in_0;
    assign stage0_2 = (in_2 < in_3) ? in_2 : in_3;
    assign stage0_3 = (in_2 < in_3) ? in_3 : in_2;
    
    // Pipeline register after Layer 0
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            stage0_0_r <= 0;
            stage0_1_r <= 0;
            stage0_2_r <= 0;
            stage0_3_r <= 0;
        end else begin
            stage0_0_r <= stage0_0;
            stage0_1_r <= stage0_1;
            stage0_2_r <= stage0_2;
            stage0_3_r <= stage0_3;
        end
    end
    
    // Layer 1 (combinational)
    assign stage1_0 = (stage0_0_r < stage0_2_r) ? stage0_0_r : stage0_2_r;
    assign stage1_2 = (stage0_0_r < stage0_2_r) ? stage0_2_r : stage0_0_r;
    assign stage1_1 = (stage0_1_r < stage0_3_r) ? stage0_1_r : stage0_3_r;
    assign stage1_3 = (stage0_1_r < stage0_3_r) ? stage0_3_r : stage0_1_r;
    
    // Pipeline register after Layer 1
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            stage1_0_r <= 0;
            stage1_1_r <= 0;
            stage1_2_r <= 0;
            stage1_3_r <= 0;
        end else begin
            stage1_0_r <= stage1_0;
            stage1_1_r <= stage1_1;
            stage1_2_r <= stage1_2;
            stage1_3_r <= stage1_3;
        end
    end
    
    // Layer 2 (combinational)
    assign stage2_0 = stage1_0_r;
    assign stage2_3 = stage1_3_r;
    assign stage2_1 = (stage1_1_r < stage1_2_r) ? stage1_1_r : stage1_2_r;
    assign stage2_2 = (stage1_1_r < stage1_2_r) ? stage1_2_r : stage1_1_r;
    
    // Output register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_0 <= 0;
            out_1 <= 0;
            out_2 <= 0;
            out_3 <= 0;
        end else begin
            out_0 <= stage2_0;
            out_1 <= stage2_1;
            out_2 <= stage2_2;
            out_3 <= stage2_3;
        end
    end

endmodule
```

## Performance Estimation

For a 4-element sorting network on typical FPGAs:

### Combinational (no pipeline)
- **Xilinx 7-Series**: ~150-200 MHz
- **Intel Cyclone V**: ~120-150 MHz
- **Lattice ECP5**: ~100-130 MHz

### Pipelined (3 stages)
- **Xilinx 7-Series**: ~300-400 MHz
- **Intel Cyclone V**: ~250-350 MHz
- **Lattice ECP5**: ~200-250 MHz

### Resource Usage (32-bit, Xilinx 7-Series)
- LUTs: ~320 (5 comparators × 64 LUTs/comparator)
- Registers (pipelined): ~384 (32 bits × 4 elements × 3 pipeline stages)
- Latency: 3 clock cycles (pipelined)
- Throughput: 1 sort per clock cycle (pipelined)

## Verification Strategy

1. **Simulation**: Test with testbench (provided)
2. **Formal Verification**: Use tools like Yosys+SymbiYosys
3. **FPGA Testing**: Deploy to hardware, test with real data

## Common Issues

### Timing Violations
- Add pipeline registers between layers
- Reduce clock frequency
- Use faster speed grade FPGA

### Resource Constraints
- Reduce bit width (WIDTH parameter)
- Use smaller network size (fewer elements)
- Share comparators across time (slower but smaller)

### Incorrect Results
- Check bit width matches data range
- Verify signed vs unsigned comparison
- Check for synthesis tool optimizations removing logic
