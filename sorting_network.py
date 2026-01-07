"""
Optimum Sorting Network Finder for FPGAs

This module provides tools for generating and optimizing sorting networks
specifically designed for FPGA implementation. Sorting networks are ideal
for hardware because they have fixed, data-independent control flow.
"""

from typing import List, Tuple, Set
from dataclasses import dataclass
from itertools import permutations
import math


@dataclass
class Comparator:
    """Represents a compare-and-swap operation between two indices."""
    i: int  # First index (min output)
    j: int  # Second index (max output)
    
    def __repr__(self):
        return f"({self.i},{self.j})"
    
    def apply(self, values: List[int]) -> List[int]:
        """Apply this comparator to a list of values."""
        result = values.copy()
        if result[self.i] > result[self.j]:
            result[self.i], result[self.j] = result[self.j], result[self.i]
        return result


@dataclass
class SortingNetwork:
    """Represents a sorting network as a sequence of comparator layers."""
    n: int  # Number of inputs
    layers: List[List[Comparator]]  # Comparators organized by depth/layer
    
    def __init__(self, n: int):
        self.n = n
        self.layers = []
    
    def add_layer(self, comparators: List[Comparator]):
        """Add a layer of parallel comparators."""
        self.layers.append(comparators)
    
    def add_comparator(self, i: int, j: int):
        """Add a single comparator to the last layer (or create new layer)."""
        comp = Comparator(min(i, j), max(i, j))
        if not self.layers:
            self.layers.append([comp])
        else:
            # Try to add to last layer if no conflict
            last_layer = self.layers[-1]
            indices_used = set()
            for c in last_layer:
                indices_used.add(c.i)
                indices_used.add(c.j)
            
            if comp.i not in indices_used and comp.j not in indices_used:
                last_layer.append(comp)
            else:
                # Create new layer
                self.layers.append([comp])
    
    def depth(self) -> int:
        """Return the depth (number of layers) of the network."""
        return len(self.layers)
    
    def size(self) -> int:
        """Return the total number of comparators."""
        return sum(len(layer) for layer in self.layers)
    
    def sort(self, values: List[int]) -> List[int]:
        """Apply the sorting network to a list of values."""
        result = values.copy()
        for layer in self.layers:
            for comp in layer:
                result = comp.apply(result)
        return result
    
    def is_valid(self) -> bool:
        """Check if this network correctly sorts all possible inputs."""
        # Test all permutations for small n (only feasible for n <= 8)
        if self.n > 8:
            # For larger n, test a large random sample
            import random
            test_cases = [list(range(self.n)), list(range(self.n-1, -1, -1))]
            for _ in range(1000):
                test = list(range(self.n))
                random.shuffle(test)
                test_cases.append(test)
        else:
            test_cases = list(permutations(range(self.n)))
        
        for perm in test_cases:
            result = self.sort(list(perm))
            if result != sorted(perm):
                return False
        return True
    
    def __repr__(self):
        lines = [f"SortingNetwork(n={self.n}, depth={self.depth()}, size={self.size()})"]
        for i, layer in enumerate(self.layers):
            lines.append(f"  Layer {i}: {layer}")
        return "\n".join(lines)
    
    def to_verilog(self, module_name: str = "sorting_network") -> str:
        """Generate Verilog code for this sorting network."""
        width = 32  # Default bit width
        
        verilog = f"""// Auto-generated sorting network for {self.n} elements
module {module_name} #(
    parameter WIDTH = {width}
) (
    input wire [WIDTH-1:0] in_{0},
"""
        for i in range(1, self.n):
            verilog += f"    input wire [WIDTH-1:0] in_{i},\n"
        
        for i in range(self.n):
            suffix = "" if i == self.n - 1 else ","
            verilog += f"    output wire [WIDTH-1:0] out_{i}{suffix}\n"
        
        verilog += ");\n\n"
        
        # Generate intermediate wires for each layer
        for layer_idx in range(len(self.layers)):
            for i in range(self.n):
                verilog += f"    wire [WIDTH-1:0] stage{layer_idx}_{i};\n"
        
        verilog += "\n"
        
        # Generate comparators
        for layer_idx, layer in enumerate(self.layers):
            indices_in_layer = set()
            for comp in layer:
                indices_in_layer.add(comp.i)
                indices_in_layer.add(comp.j)
            
            # Determine input source (previous layer or input)
            if layer_idx == 0:
                input_prefix = "in_"
            else:
                input_prefix = f"stage{layer_idx-1}_"
            
            output_prefix = f"stage{layer_idx}_"
            
            # Pass-through for indices not in this layer
            for i in range(self.n):
                if i not in indices_in_layer:
                    verilog += f"    assign {output_prefix}{i} = {input_prefix}{i};\n"
            
            # Comparators
            for comp in layer:
                verilog += f"\n    // Comparator ({comp.i}, {comp.j})\n"
                verilog += f"    assign {output_prefix}{comp.i} = ({input_prefix}{comp.i} < {input_prefix}{comp.j}) ? {input_prefix}{comp.i} : {input_prefix}{comp.j};\n"
                verilog += f"    assign {output_prefix}{comp.j} = ({input_prefix}{comp.i} < {input_prefix}{comp.j}) ? {input_prefix}{comp.j} : {input_prefix}{comp.i};\n"
            
            verilog += "\n"
        
        # Connect final stage to outputs
        last_layer = len(self.layers) - 1
        for i in range(self.n):
            verilog += f"    assign out_{i} = stage{last_layer}_{i};\n"
        
        verilog += "\nendmodule\n"
        return verilog


def bubble_sort_network(n: int) -> SortingNetwork:
    """Generate a bubble sort network for n elements."""
    network = SortingNetwork(n)
    
    for i in range(n):
        layer = []
        if i % 2 == 0:
            # Even phase: compare (0,1), (2,3), (4,5), ...
            for j in range(0, n-1, 2):
                layer.append(Comparator(j, j+1))
        else:
            # Odd phase: compare (1,2), (3,4), (5,6), ...
            for j in range(1, n-1, 2):
                layer.append(Comparator(j, j+1))
        
        if layer:
            network.add_layer(layer)
    
    return network


def bitonic_merge(network: SortingNetwork, low: int, n: int, ascending: bool):
    """Helper for bitonic sort: merge a bitonic sequence."""
    if n <= 1:
        return
    
    m = 1
    while m < n:
        m *= 2
    m = m // 2
    
    for i in range(low, low + n - m):
        network.add_comparator(i, i + m)
    
    bitonic_merge(network, low, m, ascending)
    if low + m < low + n:
        bitonic_merge(network, low + m, n - m, ascending)


def bitonic_sort_recursive(network: SortingNetwork, low: int, n: int, ascending: bool):
    """Helper for bitonic sort: recursively build the network."""
    if n <= 1:
        return
    
    m = n // 2
    bitonic_sort_recursive(network, low, m, True)  
    bitonic_sort_recursive(network, low + m, n - m, False)  
    bitonic_merge(network, low, n, ascending)


def bitonic_sort_network(n: int) -> SortingNetwork:
    """
    Generate a bitonic sort network for n elements.
    Note: Works best when n is a power of 2.
    """
    network = SortingNetwork(n)
    bitonic_sort_recursive(network, 0, n, True)
    return network


def odd_even_merge(network: SortingNetwork, low: int, n: int):
    """Batcher's odd-even merge algorithm."""
    if n <= 1:
        return
    
    if n == 2:
        network.add_comparator(low, low + 1)
        return
    
    m = n // 2
    odd_even_merge(network, low, m)
    odd_even_merge(network, low + m, n - m)
    
    for i in range(low + 1, low + n - 1, 2):
        network.add_comparator(i, i + 1)


def odd_even_merge_sort_recursive(network: SortingNetwork, low: int, n: int):
    """Batcher's odd-even merge sort - recursive helper."""
    if n <= 1:
        return
    
    m = n // 2
    odd_even_merge_sort_recursive(network, low, m)
    odd_even_merge_sort_recursive(network, low + m, n - m)
    odd_even_merge(network, low, n)


def odd_even_merge_sort_network(n: int) -> SortingNetwork:
    """
    Generate Batcher's odd-even merge sort network.
    This is often optimal or near-optimal for small n.
    """
    network = SortingNetwork(n)
    odd_even_merge_sort_recursive(network, 0, n)
    return network


def optimize_network_depth(network: SortingNetwork) -> SortingNetwork:
    """
    Optimize a sorting network by minimizing depth.
    This reorganizes comparators into parallel layers where possible.
    """
    # Flatten all comparators
    all_comps = []
    for layer in network.layers:
        all_comps.extend(layer)
    
    # Rebuild layers greedily
    optimized = SortingNetwork(network.n)
    used = [False] * len(all_comps)
    
    while not all(used):
        current_layer = []
        indices_used = set()
        
        for i, comp in enumerate(all_comps):
            if not used[i]:
                if comp.i not in indices_used and comp.j not in indices_used:
                    current_layer.append(comp)
                    indices_used.add(comp.i)
                    indices_used.add(comp.j)
                    used[i] = True
        
        if current_layer:
            optimized.add_layer(current_layer)
    
    return optimized


def get_optimal_small_network(n: int) -> SortingNetwork:
    """
    Return known optimal sorting networks for small n.
    These are hand-crafted for best depth and size.
    """
    if n == 2:
        net = SortingNetwork(2)
        net.add_layer([Comparator(0, 1)])
        return net
    
    elif n == 3:
        net = SortingNetwork(3)
        net.add_layer([Comparator(0, 2)])
        net.add_layer([Comparator(0, 1), Comparator(1, 2)])
        return net
    
    elif n == 4:
        # Optimal: depth 3, size 5
        net = SortingNetwork(4)
        net.add_layer([Comparator(0, 1), Comparator(2, 3)])
        net.add_layer([Comparator(0, 2), Comparator(1, 3)])
        net.add_layer([Comparator(1, 2)])
        return net
    
    elif n == 5:
        # Optimal: depth 5, size 9
        net = SortingNetwork(5)
        net.add_layer([Comparator(0, 1), Comparator(3, 4)])
        net.add_layer([Comparator(2, 4)])
        net.add_layer([Comparator(2, 3), Comparator(0, 1)])
        net.add_layer([Comparator(0, 2), Comparator(1, 4)])
        net.add_layer([Comparator(1, 3), Comparator(2, 3)])
        return net
    
    elif n == 6:
        # Optimal: depth 5, size 12
        net = SortingNetwork(6)
        net.add_layer([Comparator(1, 2), Comparator(4, 5)])
        net.add_layer([Comparator(0, 2), Comparator(3, 5)])
        net.add_layer([Comparator(0, 1), Comparator(3, 4), Comparator(2, 5)])
        net.add_layer([Comparator(0, 3), Comparator(1, 4)])
        net.add_layer([Comparator(2, 4), Comparator(1, 3), Comparator(2, 3)])
        return net
    
    elif n == 8:
        # Use bubble sort as a fallback for n=8 until we get the optimal network correct
        return None
    
    return None


def find_optimal_network(n: int, max_depth: int = None, verbose: bool = False) -> SortingNetwork:
    """
    Find an optimal sorting network for n elements.
    Tries multiple algorithms and returns the best one based on depth and size.
    """
    # Try to use known optimal network first
    optimal = get_optimal_small_network(n)
    if optimal is not None:
        if verbose:
            print(f"Using known optimal network for n={n}")
            print(f"  Depth: {optimal.depth()}, Size: {optimal.size()}")
        return optimal
    
    candidates = []
    
    # Try bubble sort (simple but not optimal)
    if verbose:
        print(f"Generating bubble sort network for n={n}...")
    bubble = bubble_sort_network(n)
    bubble_opt = optimize_network_depth(bubble)
    candidates.append(("Bubble Sort (optimized)", bubble_opt))
    
    # Try bitonic sort (good for powers of 2)
    if verbose:
        print(f"Generating bitonic sort network for n={n}...")
    try:
        bitonic = bitonic_sort_network(n)
        bitonic_opt = optimize_network_depth(bitonic)
        candidates.append(("Bitonic Sort (optimized)", bitonic_opt))
    except:
        if verbose:
            print("  Bitonic sort failed")
    
    # Try odd-even merge sort (often optimal)
    if verbose:
        print(f"Generating odd-even merge sort network for n={n}...")
    try:
        odd_even = odd_even_merge_sort_network(n)
        odd_even_opt = optimize_network_depth(odd_even)
        candidates.append(("Odd-Even Merge Sort (optimized)", odd_even_opt))
    except:
        if verbose:
            print("  Odd-even merge sort failed")
    
    # Validate and score
    valid_candidates = []
    for name, net in candidates:
        if net.is_valid():
            # Score: prioritize depth (critical for FPGA timing), then size
            score = (net.depth(), net.size())
            valid_candidates.append((score, name, net))
            if verbose:
                print(f"  {name}: depth={net.depth()}, size={net.size()}, valid=True")
        else:
            if verbose:
                print(f"  {name}: INVALID")
    
    if not valid_candidates:
        raise ValueError("No valid sorting network found!")
    
    # Sort by score (lower is better)
    valid_candidates.sort()
    best_score, best_name, best_network = valid_candidates[0]
    
    if verbose:
        print(f"\nBest network: {best_name}")
        print(f"  Depth: {best_network.depth()} (critical path delay)")
        print(f"  Size: {best_network.size()} (comparator count)")
    
    return best_network


def print_network_metrics(network: SortingNetwork):
    """Print FPGA-relevant metrics for a sorting network."""
    print(f"=== Sorting Network Metrics (n={network.n}) ===")
    print(f"Depth (Pipeline Stages): {network.depth()}")
    print(f"Comparators (Area): {network.size()}")
    print(f"Valid: {network.is_valid()}")
    print(f"\nFPGA Considerations:")
    print(f"  - Depth determines critical path and maximum clock frequency")
    print(f"  - Each comparator uses ~1-2 LUTs per bit")
    print(f"  - Estimated LUTs (32-bit): ~{network.size() * 64}")
    print(f"  - Can be pipelined with {network.depth()} stages")
    print(f"\nNetwork Structure:")
    for i, layer in enumerate(network.layers):
        print(f"  Stage {i}: {layer}")


if __name__ == "__main__":
    # Example usage
    print("=== FPGA Sorting Network Generator ===\n")
    
    # Test small networks
    for n in [4, 8, 16]:
        print(f"\n{'='*60}")
        print(f"Finding optimal sorting network for n={n}")
        print('='*60)
        
        network = find_optimal_network(n, verbose=True)
        print()
        print_network_metrics(network)
        
        # Test the network
        test_input = list(range(n, 0, -1))
        test_output = network.sort(test_input)
        print(f"\nTest: {test_input} -> {test_output}")
        
        # Generate Verilog for n=4 as example
        if n == 4:
            print("\n" + "="*60)
            print("Verilog code for n=4 network:")
            print("="*60)
            print(network.to_verilog("sort_4"))
