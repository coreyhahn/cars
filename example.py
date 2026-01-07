#!/usr/bin/env python3
"""
Example usage of the FPGA sorting network optimizer.
"""

from sorting_network import (
    find_optimal_network,
    print_network_metrics,
    bubble_sort_network,
    optimize_network_depth,
    get_optimal_small_network
)

print("=" * 70)
print("Example 1: Generate an optimal 4-element sorter")
print("=" * 70)

network4 = find_optimal_network(4, verbose=True)
print()
print_network_metrics(network4)

# Generate Verilog
print("\n" + "=" * 70)
print("Generating Verilog code...")
print("=" * 70)
verilog = network4.to_verilog("sorter_4")
print(verilog[:500] + "...\n")  # Print first 500 chars

# Save to file
with open("/tmp/sorter_4.v", "w") as f:
    f.write(verilog)
print("Full Verilog saved to /tmp/sorter_4.v")

print("\n" + "=" * 70)
print("Example 2: Test the network with different inputs")
print("=" * 70)

test_cases = [
    [4, 3, 2, 1],
    [1, 2, 3, 4],
    [2, 4, 1, 3],
    [4, 1, 3, 2]
]

for test in test_cases:
    result = network4.sort(test)
    print(f"  {test} -> {result}")

print("\n" + "=" * 70)
print("Example 3: Compare different network types for n=6")
print("=" * 70)

# Known optimal
optimal = get_optimal_small_network(6)
if optimal:
    print(f"Known optimal: depth={optimal.depth()}, size={optimal.size()}, valid={optimal.is_valid()}")

# Bubble sort
bubble = bubble_sort_network(6)
bubble_opt = optimize_network_depth(bubble)
print(f"Bubble sort (optimized): depth={bubble_opt.depth()}, size={bubble_opt.size()}, valid={bubble_opt.is_valid()}")

# Best overall
best = find_optimal_network(6)
print(f"Best found: depth={best.depth()}, size={best.size()}, valid={best.is_valid()}")

print("\n" + "=" * 70)
print("Example 4: Large network - 12 elements")
print("=" * 70)

network12 = find_optimal_network(12, verbose=False)
print(f"12-element network:")
print(f"  Depth: {network12.depth()} pipeline stages")
print(f"  Size: {network12.size()} comparators")
print(f"  Estimated area (32-bit): ~{network12.size() * 64} LUTs")
print(f"  Valid: {network12.is_valid()}")

# Test it
test12 = list(range(12, 0, -1))
result12 = network12.sort(test12)
print(f"  Test: {test12}")
print(f"  Result: {result12}")
print(f"  Correct: {result12 == sorted(test12)}")

print("\n" + "=" * 70)
print("Example 5: Generate Verilog for synthesis")
print("=" * 70)

# Create an 8-element sorter for FPGA
network8 = find_optimal_network(8)
verilog8 = network8.to_verilog("fpga_sorter_8")

# Save it
filename = "/tmp/fpga_sorter_8.v"
with open(filename, "w") as f:
    f.write(verilog8)

print(f"Generated 8-element sorter Verilog:")
print(f"  File: {filename}")
print(f"  Depth: {network8.depth()} stages")
print(f"  Comparators: {network8.size()}")
print(f"  Module name: fpga_sorter_8")
print(f"  Parameterized bit width (default 32-bit)")
print(f"\nThis can be synthesized for your FPGA using Vivado, Quartus, etc.")
