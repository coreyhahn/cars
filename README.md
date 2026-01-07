# FPGA Sorting Network Optimizer

A Python tool for generating and optimizing sorting networks specifically designed for FPGA implementation.

## Overview

Sorting networks are comparison networks that sort their inputs using a fixed sequence of compare-and-swap operations. Unlike traditional sorting algorithms, sorting networks have **data-independent control flow**, making them ideal for hardware implementation on FPGAs where:

- Parallel execution is native
- Fixed routing is efficient
- Predictable timing is critical
- No branch prediction is needed

## Features

- **Multiple Algorithms**: Implements bubble sort, bitonic sort, and Batcher's odd-even merge sort networks
- **Automatic Optimization**: Minimizes network depth for better FPGA timing
- **Validation**: Automatically verifies network correctness
- **FPGA Metrics**: Reports depth (pipeline stages), size (comparators/LUTs), and estimated resource usage
- **Verilog Generation**: Exports sorting networks as synthesizable Verilog code
- **Optimal Network Selection**: Compares multiple algorithms and selects the best for your constraints

## Quick Start

```bash
python sorting_network.py
```

This will generate optimal sorting networks for 4, 8, and 16 elements, showing metrics and example Verilog code.

## Usage

### As a Library

```python
from sorting_network import find_optimal_network, print_network_metrics

# Find the best sorting network for 8 elements
network = find_optimal_network(8, verbose=True)

# Display FPGA-relevant metrics
print_network_metrics(network)

# Test the network
input_data = [8, 3, 5, 1, 9, 2, 7, 4]
output_data = network.sort(input_data)
print(f"Sorted: {output_data}")

# Generate Verilog code
verilog_code = network.to_verilog("my_sorter")
with open("my_sorter.v", "w") as f:
    f.write(verilog_code)
```

### Specific Algorithms

```python
from sorting_network import (
    bubble_sort_network,
    bitonic_sort_network,
    odd_even_merge_sort_network,
    optimize_network_depth
)

# Generate a specific type of network
network = bitonic_sort_network(16)

# Optimize it for minimum depth
optimized = optimize_network_depth(network)

print(f"Depth: {optimized.depth()}, Size: {optimized.size()}")
```

## Algorithms

### 1. Bubble Sort Network
- **Depth**: O(n)
- **Size**: O(n²)
- Simple but not optimal; good for very small n

### 2. Bitonic Sort Network
- **Depth**: O(log²n)
- **Size**: O(n log²n)
- Excellent for powers of 2
- Highly regular structure, good for FPGA layout

### 3. Odd-Even Merge Sort (Batcher's Algorithm)
- **Depth**: O(log²n)
- **Size**: O(n log²n)
- Often produces optimal or near-optimal networks
- Works well for any n

## FPGA Metrics

The tool reports several FPGA-relevant metrics:

- **Depth**: Number of sequential comparator stages = pipeline depth = critical path
- **Size**: Total number of comparators = area/resource usage
- **LUT Estimate**: Approximate FPGA LUTs needed (based on 32-bit comparators)

### Example Output

```
=== Sorting Network Metrics (n=8) ===
Depth (Pipeline Stages): 6
Comparators (Area): 19
Valid: True

FPGA Considerations:
  - Depth determines critical path and maximum clock frequency
  - Each comparator uses ~1-2 LUTs per bit
  - Estimated LUTs (32-bit): ~1216
  - Can be pipelined with 6 stages
```

## Verilog Generation

The tool can generate synthesizable Verilog code for any sorting network:

```python
network = find_optimal_network(4)
verilog = network.to_verilog("sort_4")
print(verilog)
```

Generates a parameterized module with:
- Configurable bit width
- All comparators properly staged
- Correct wire routing between stages

## Known Optimal Networks

For reference, here are known optimal sorting networks:

| n | Min Depth | Min Size | Algorithm |
|---|-----------|----------|-----------|
| 4 | 3 | 5 | Optimal |
| 8 | 6 | 19 | Optimal |
| 16 | 10 | 60 | Optimal |

## Design Considerations for FPGAs

When selecting a sorting network for FPGA implementation:

1. **Depth vs. Size Tradeoff**:
   - Lower depth → Higher Fmax → Better throughput
   - Lower size → Fewer resources → Better area efficiency

2. **Pipelining**:
   - Each layer can be a pipeline stage
   - Register insertion between stages improves Fmax
   - Depth = minimum pipeline stages for maximum throughput

3. **Bit Width**:
   - Generated Verilog is parameterized
   - Wider data paths use more LUTs linearly
   - 32-bit comparator ≈ 64 LUTs (min + max)

4. **Regular Structures**:
   - Bitonic sort has very regular structure
   - Better for FPGA place & route
   - Easier to pipeline uniformly

## Advanced Usage

### Custom Optimization

```python
# Build a custom network
network = SortingNetwork(4)
network.add_layer([Comparator(0, 2), Comparator(1, 3)])
network.add_layer([Comparator(0, 1), Comparator(2, 3)])
network.add_layer([Comparator(1, 2)])

# Verify it works
if network.is_valid():
    print("Network is valid!")
    
# Optimize depth
optimized = optimize_network_depth(network)
```

## Testing

The validation system tests networks against:
- All permutations (for n ≤ 8)
- 1000+ random permutations (for n > 8)

This ensures the network correctly sorts any input.

## License

This project is open source and available for use in FPGA designs.

## References

- Knuth, D.E. "The Art of Computer Programming, Volume 3: Sorting and Searching"
- Batcher, K.E. "Sorting networks and their applications" (1968)
- https://en.wikipedia.org/wiki/Sorting_network
