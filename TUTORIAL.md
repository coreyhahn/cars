# FPGA Sorting Networks Tutorial

## What is a Sorting Network?

A sorting network is a special type of sorting algorithm that uses a fixed sequence of compare-and-swap operations. Unlike traditional sorting algorithms (quicksort, mergesort, etc.), sorting networks have **data-independent control flow** - the same comparisons happen regardless of the input values.

This makes them ideal for hardware implementation, especially FPGAs, because:
- All operations can be parallelized in hardware
- No branch prediction needed
- Predictable timing and latency
- Fixed routing in the FPGA fabric

## How It Works

A sorting network consists of:
1. **Comparators**: Each comparator takes two inputs (i, j) and outputs min and max
2. **Layers**: Comparators arranged in parallel stages
3. **Depth**: Number of sequential layers (= pipeline stages)

Example 4-element network:
```
Inputs:  [3, 1, 4, 2]
Layer 0: Compare (0,1) and (2,3) -> [1, 3, 2, 4]
Layer 1: Compare (0,2) and (1,3) -> [1, 2, 3, 4]
Layer 2: Compare (1,2) -> [1, 2, 3, 4]
Output:  [1, 2, 3, 4]
```

## Why Optimize for FPGAs?

### 1. Depth Optimization
- **Depth** = number of sequential comparator stages
- Lower depth = shorter critical path = higher clock frequency
- Each layer can be a pipeline stage in hardware
- Goal: Minimize depth for maximum throughput

### 2. Size Optimization
- **Size** = total number of comparators
- Each comparator uses FPGA resources (LUTs, registers)
- Lower size = less area = more room for other logic
- Trade-off: Sometimes accepting higher depth can reduce size

### 3. Pipelining
Sorting networks are naturally pipelined:
```verilog
// Each layer becomes a pipeline stage
always @(posedge clk) begin
    stage1_data <= layer0_output;  // Pipeline register
    stage2_data <= layer1_output;
    // ...
end
```

## Using This Tool

### Basic Usage
```python
from sorting_network import find_optimal_network

# Get the best network for your size
network = find_optimal_network(8, verbose=True)

# Check metrics
print(f"Depth: {network.depth()}")  # Pipeline stages
print(f"Size: {network.size()}")    # Comparators (area)
print(f"Valid: {network.is_valid()}")  # Correctness check

# Test it
result = network.sort([8, 3, 5, 1, 9, 2, 7, 4])
print(result)  # [1, 2, 3, 4, 5, 7, 8, 9]
```

### Generate Verilog for FPGA
```python
# Create Verilog module
verilog_code = network.to_verilog("my_sorter")

# Save to file
with open("my_sorter.v", "w") as f:
    f.write(verilog_code)

# Now synthesize with Vivado, Quartus, or your FPGA tool
```

The generated Verilog:
- Has parameterized bit width (default 32-bit)
- Uses pure combinational logic (easy to pipeline)
- Includes proper stage separation for pipelining
- Can be directly synthesized

### Comparing Algorithms
```python
from sorting_network import (
    bubble_sort_network,
    get_optimal_small_network,
    optimize_network_depth
)

# Try different approaches
bubble = bubble_sort_network(8)
optimal = get_optimal_small_network(8)

# Optimize for depth
optimized = optimize_network_depth(bubble)
```

## Common Network Sizes

### Small Networks (n ≤ 6)
- Use known optimal networks (hardcoded)
- These are provably optimal
- Best depth and size for FPGA implementation

### Medium Networks (n = 8-16)
- Bubble sort network works but not optimal
- Bitonic sort good for powers of 2
- Trade-offs between depth and size

### Large Networks (n > 16)
- Bubble sort provides valid solution
- Consider multiple smaller networks in parallel
- Or use hybrid hardware/software approach

## Resource Estimation

For a 32-bit sorting network:
- Each comparator ≈ 64 LUTs (min + max logic)
- Example: 8-element network with 28 comparators ≈ 1,792 LUTs
- Pipeline registers: 32 bits × n × (depth-1) flip-flops

For 16-bit data, divide LUT estimate by ~2.
For 64-bit data, multiply LUT estimate by ~2.

## FPGA Synthesis Tips

1. **Add Pipeline Registers**: Insert registers between layers
2. **Timing Constraints**: Set clock period based on depth
3. **Area Constraints**: Choose network size based on available resources
4. **Bit Width**: Parameterize for flexibility
5. **Comparator Type**: Use `<` for ascending, `>` for descending

## Examples

See `example.py` for:
- Generating networks of different sizes
- Testing with various inputs
- Creating Verilog output files
- Comparing different algorithms
- Estimating FPGA resources

## Advanced Topics

### Custom Networks
```python
from sorting_network import SortingNetwork, Comparator

net = SortingNetwork(4)
net.add_layer([Comparator(0, 1), Comparator(2, 3)])
net.add_layer([Comparator(0, 2), Comparator(1, 3)])
net.add_layer([Comparator(1, 2)])

if net.is_valid():
    print("Custom network works!")
```

### Optimization Strategies
- **Depth-first**: Minimize latency, maximize Fmax
- **Size-first**: Minimize area, fit more logic
- **Balanced**: Trade-off between depth and size

### Power Considerations
- Fewer comparators = less switching = lower dynamic power
- Shorter depth = lower latency = can use clock gating
- Pipeline registers add static power but enable higher throughput

## References

- [Sorting Networks (Wikipedia)](https://en.wikipedia.org/wiki/Sorting_network)
- Knuth, "The Art of Computer Programming, Vol 3"
- Batcher, "Sorting networks and their applications" (1968)
- [Optimal Sorting Networks](http://users.telenet.be/bertdobbelaere/SorterHunter/sorting_networks.html)
