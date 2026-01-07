"""
Merge Sort Network Builder

Builds sorting networks using the merge sort paradigm:
1. Sort pairs (2-sorters)
2. Merge 2+2 → 4
3. Merge 4+4 → 8
4. ... up to 2^k

This compositional approach is more intuitive and allows
analyzing each merge stage independently.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Comparator:
    """A compare-and-swap operation between two indices."""
    i: int  # Lower index (will hold min)
    j: int  # Higher index (will hold max)

    def __post_init__(self):
        # Ensure i < j for consistency
        if self.i > self.j:
            self.i, self.j = self.j, self.i

    def apply(self, values: List[int]) -> None:
        """Apply compare-and-swap in place."""
        if values[self.i] > values[self.j]:
            values[self.i], values[self.j] = values[self.j], values[self.i]


@dataclass
class MergeNetwork:
    """
    Represents a merge network that combines two sorted sequences.

    Attributes:
        input_size: Size of each input sequence (total inputs = 2 * input_size)
        layers: List of comparator layers (each layer runs in parallel)
    """
    input_size: int
    layers: List[List[Comparator]] = field(default_factory=list)

    @property
    def total_inputs(self) -> int:
        return 2 * self.input_size

    @property
    def depth(self) -> int:
        return len(self.layers)

    @property
    def size(self) -> int:
        return sum(len(layer) for layer in self.layers)

    def add_layer(self, comparators: List[Comparator]):
        if comparators:
            self.layers.append(comparators)

    def apply(self, values: List[int]) -> List[int]:
        """Apply the merge network to values."""
        result = values.copy()
        for layer in self.layers:
            for comp in layer:
                comp.apply(result)
        return result


@dataclass
class SortingNetwork:
    """
    Complete sorting network built from merge stages.
    """
    n: int  # Total elements to sort
    stages: List[Tuple[str, List[List[Comparator]]]] = field(default_factory=list)

    @property
    def depth(self) -> int:
        return sum(len(layers) for _, layers in self.stages)

    @property
    def size(self) -> int:
        return sum(
            sum(len(layer) for layer in layers)
            for _, layers in self.stages
        )

    def add_stage(self, name: str, layers: List[List[Comparator]]):
        self.stages.append((name, layers))

    def apply(self, values: List[int]) -> List[int]:
        """Apply the complete sorting network."""
        result = values.copy()
        for _, layers in self.stages:
            for layer in layers:
                for comp in layer:
                    comp.apply(result)
        return result

    def is_valid(self, num_tests: int = 1000) -> bool:
        """Validate the sorting network with random tests."""
        import random

        # Always test sorted and reverse sorted
        test_cases = [
            list(range(self.n)),
            list(range(self.n - 1, -1, -1)),
        ]

        # Add random test cases
        for _ in range(num_tests):
            test = list(range(self.n))
            random.shuffle(test)
            test_cases.append(test)

        for test in test_cases:
            result = self.apply(test)
            if result != sorted(test):
                return False
        return True

    def print_summary(self):
        """Print a summary of the network structure."""
        print(f"\n{'='*60}")
        print(f"Merge Sort Network for n={self.n}")
        print(f"{'='*60}")
        print(f"Total Depth: {self.depth}")
        print(f"Total Comparators: {self.size}")
        print(f"\nStage Breakdown:")
        print(f"{'-'*60}")

        cumulative_depth = 0
        cumulative_size = 0
        for name, layers in self.stages:
            stage_depth = len(layers)
            stage_size = sum(len(layer) for layer in layers)
            cumulative_depth += stage_depth
            cumulative_size += stage_size
            print(f"  {name:30} depth={stage_depth:4}  comps={stage_size:6}  "
                  f"(cumulative: d={cumulative_depth}, c={cumulative_size})")


def build_2_sorter(offset: int = 0) -> List[Comparator]:
    """
    Build a 2-sorter: single comparator for 2 elements.

    Args:
        offset: Base index offset for the comparator

    Returns:
        List with single comparator
    """
    return [Comparator(offset, offset + 1)]


def build_odd_even_merge(size: int, offset: int = 0) -> MergeNetwork:
    """
    Build Batcher's odd-even merge network.

    Merges two sorted sequences of 'size' elements each,
    starting at index 'offset'.

    Total input indices: [offset, offset + 2*size - 1]
    Left sequence:  indices offset, offset+1, ..., offset+size-1
    Right sequence: indices offset+size, offset+size+1, ..., offset+2*size-1

    Depth: ceil(log2(2*size)) = ceil(log2(size)) + 1
    Size: size * (ceil(log2(size)) + 1) - ceil(log2(size))

    Args:
        size: Size of each sorted sequence to merge
        offset: Starting index

    Returns:
        MergeNetwork for merging two sorted sequences of given size
    """
    network = MergeNetwork(input_size=size)

    if size == 1:
        # Base case: merge two single elements = one comparator
        network.add_layer([Comparator(offset, offset + 1)])
        return network

    # Collect all comparators with their dependencies
    # Each comparator gets a "round" based on when it can execute
    all_comparators = []

    def odd_even_merge_impl(lo: int, n: int, r: int):
        """
        Standard Batcher odd-even merge.

        lo: starting index
        n: total elements to merge
        r: stride (distance between compared elements)
        """
        m = r * 2
        if m < n:
            # Recursive step: merge odd and even subsequences
            odd_even_merge_impl(lo, n, m)      # Odd positions
            odd_even_merge_impl(lo + r, n, m)  # Even positions

            # Then compare-exchange middle elements
            i = lo + r
            while i + r < lo + n:
                all_comparators.append(Comparator(i, i + r))
                i += m
        else:
            # Base case: compare two elements at distance r
            if lo + r < lo + n:
                all_comparators.append(Comparator(lo, lo + r))

    # Generate all comparators
    odd_even_merge_impl(offset, 2 * size, 1)

    # Efficient scheduling: track last layer each index was used in
    # A comparator (i,j) must go in layer > max(last_used[i], last_used[j])
    last_used = {}  # index -> last layer it was used in

    layers = []

    for comp in all_comparators:
        # Find minimum layer this comparator can go in
        min_layer = max(last_used.get(comp.i, -1), last_used.get(comp.j, -1)) + 1

        # Extend layers list if needed
        while len(layers) <= min_layer:
            layers.append([])

        # Add comparator to this layer
        layers[min_layer].append(comp)

        # Update last used
        last_used[comp.i] = min_layer
        last_used[comp.j] = min_layer

    for layer in layers:
        network.add_layer(layer)

    return network


def build_bitonic_merge(size: int, offset: int = 0, ascending: bool = True) -> MergeNetwork:
    """
    Build a bitonic merge network.

    Assumes input is a bitonic sequence (first half sorted ascending/descending,
    second half sorted the opposite way).

    For merge sort, we need to reverse one half before feeding to bitonic merge,
    or use odd-even merge which handles two ascending sequences directly.
    """
    network = MergeNetwork(input_size=size)

    def bitonic_merge_recursive(lo: int, n: int, asc: bool):
        if n <= 1:
            return

        m = n // 2
        comparators = []
        for i in range(lo, lo + m):
            if asc:
                comparators.append(Comparator(i, i + m))
            else:
                comparators.append(Comparator(i + m, i))

        if comparators:
            network.add_layer(comparators)

        bitonic_merge_recursive(lo, m, asc)
        bitonic_merge_recursive(lo + m, m, asc)

    bitonic_merge_recursive(offset, size * 2, ascending)
    return network


def build_merge_sort_network(k: int) -> SortingNetwork:
    """
    Build a complete merge sort network for 2^k elements.

    Structure:
        Stage 1: 2^(k-1) parallel 2-sorters
        Stage 2: 2^(k-2) parallel 2+2 mergers
        Stage 3: 2^(k-3) parallel 4+4 mergers
        ...
        Stage k: 1 parallel 2^(k-1) + 2^(k-1) merger

    Args:
        k: Power of 2 (network sorts 2^k elements)

    Returns:
        Complete SortingNetwork
    """
    n = 2 ** k
    network = SortingNetwork(n=n)

    # Stage 1: Sort all pairs
    # 2^(k-1) comparators, all in parallel (depth 1)
    pair_comparators = []
    for i in range(0, n, 2):
        pair_comparators.extend(build_2_sorter(offset=i))
    network.add_stage(f"Stage 1: {n//2}× 2-sorters", [pair_comparators])

    # Stages 2 through k: Merge increasingly larger sequences
    for stage in range(2, k + 1):
        merge_size = 2 ** (stage - 1)  # Size of each sequence being merged
        num_merges = n // (2 * merge_size)  # Number of parallel merges

        # Build all parallel mergers for this stage
        stage_layers = {}  # layer_idx -> comparators

        for m in range(num_merges):
            offset = m * 2 * merge_size
            merger = build_odd_even_merge(merge_size, offset)

            # Add this merger's layers to the stage
            for layer_idx, layer in enumerate(merger.layers):
                if layer_idx not in stage_layers:
                    stage_layers[layer_idx] = []
                stage_layers[layer_idx].extend(layer)

        # Convert to list of layers
        layers = [stage_layers[i] for i in sorted(stage_layers.keys())]
        stage_name = f"Stage {stage}: {num_merges}× {merge_size}+{merge_size} merge"
        network.add_stage(stage_name, layers)

    return network


def analyze_merge_network(size: int):
    """Analyze a single merge network of given size."""
    print(f"\n{'='*50}")
    print(f"Odd-Even Merge Network Analysis: {size}+{size} → {2*size}")
    print(f"{'='*50}")

    merger = build_odd_even_merge(size)
    print(f"Depth: {merger.depth}")
    print(f"Comparators: {merger.size}")

    # Validate
    import random
    valid = True
    for _ in range(100):
        left = sorted([random.randint(0, 1000) for _ in range(size)])
        right = sorted([random.randint(0, 1000) for _ in range(size)])
        combined = left + right
        result = merger.apply(combined)
        if result != sorted(combined):
            valid = False
            print(f"FAILED: {left} + {right} → {result}")
            break

    print(f"Valid: {valid}")

    # Show layer structure
    print(f"\nLayer structure:")
    for i, layer in enumerate(merger.layers):
        print(f"  Layer {i}: {len(layer)} comparators")


def theoretical_complexity(k: int) -> Tuple[int, int]:
    """
    Calculate theoretical depth and size for merge sort network of 2^k elements.

    For odd-even merge:
        - Merge of two n-sequences: depth = log2(n) + 1, size = n * (log2(n) + 1) - n + 1
        - Actually simpler: depth = log2(2n), size ≈ n * log2(n)

    For full merge sort:
        - Total depth = sum of merge depths = O(log^2 n)
        - Total size = O(n log^2 n)
    """
    n = 2 ** k

    # Stage 1: n/2 comparators, depth 1
    total_depth = 1
    total_size = n // 2

    # Stages 2 to k
    for stage in range(2, k + 1):
        merge_size = 2 ** (stage - 1)
        num_merges = n // (2 * merge_size)

        # Odd-even merge of two m-sequences has depth log2(m) + 1
        merge_depth = stage  # log2(merge_size) + 1 = (stage-1) + 1 = stage
        # Size per merge: approximately m * log2(m) for large m
        merge_comps = merge_size * stage - merge_size + 1  # Approximate

        total_depth += merge_depth
        total_size += num_merges * merge_comps

    return total_depth, total_size


if __name__ == "__main__":
    import sys

    print("="*70)
    print("MERGE SORT NETWORK BUILDER")
    print("="*70)

    # Analyze individual merge networks first
    print("\n" + "="*70)
    print("MERGE NETWORK ANALYSIS")
    print("="*70)

    for size in [1, 2, 4, 8, 16]:
        analyze_merge_network(size)

    # Build and analyze complete sorting networks
    print("\n" + "="*70)
    print("COMPLETE SORTING NETWORKS")
    print("="*70)

    # Test small networks first
    for k in [2, 3, 4, 5, 6]:
        n = 2 ** k
        print(f"\n{'='*60}")
        print(f"Building merge sort network for n={n} (k={k})")

        network = build_merge_sort_network(k)
        network.print_summary()

        # Validate
        valid = network.is_valid(num_tests=min(1000, n * 10))
        print(f"\nValidation: {'PASSED' if valid else 'FAILED'}")

        if not valid and n <= 16:
            # Debug: test specific cases
            test = list(range(n - 1, -1, -1))
            result = network.apply(test)
            print(f"  Reverse sorted test: {test} → {result}")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY: Merge Sort Networks")
    print("="*70)
    print(f"{'k':>4} {'n':>8} {'Depth':>8} {'Comparators':>12} {'Valid':>8}")
    print("-"*44)

    for k in range(2, 15):
        n = 2 ** k
        network = build_merge_sort_network(k)

        # Only validate smaller networks (validation is slow for large n)
        if k <= 10:
            valid = network.is_valid(num_tests=100)
            valid_str = "✓" if valid else "✗"
        else:
            valid_str = "—"

        print(f"{k:>4} {n:>8} {network.depth:>8} {network.size:>12} {valid_str:>8}")

    # Build the target: 2^14
    print("\n" + "="*70)
    print("TARGET: 2^14 = 16384 elements")
    print("="*70)

    network_14 = build_merge_sort_network(14)
    network_14.print_summary()
