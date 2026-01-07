#!/usr/bin/env python3
"""
Visualize sorting networks as ASCII art diagrams.
"""

from sorting_network import find_optimal_network, get_optimal_small_network


def visualize_network(network, title="Sorting Network"):
    """
    Generate an ASCII art visualization of a sorting network.
    """
    n = network.n
    depth = network.depth()
    
    print("=" * 70)
    print(f"  {title}")
    print(f"  Elements: {n}, Depth: {depth}, Size: {network.size()}")
    print("=" * 70)
    
    # Create the visualization grid
    width = depth * 4 + 4
    lines = []
    
    for i in range(n):
        line = f"{i} "
        for layer_idx in range(depth):
            # Check if this wire has a comparator in this layer
            layer = network.layers[layer_idx]
            involved = False
            comp_char = " "
            
            for comp in layer:
                if comp.i == i:
                    comp_char = "└"
                    involved = True
                    break
                elif comp.j == i:
                    comp_char = "┌"
                    involved = True
                    break
            
            if involved:
                line += f"{comp_char}──"
            else:
                line += "───"
            
            if layer_idx < depth - 1:
                line += "─"
        
        lines.append(line)
    
    # Print the network
    for line in lines:
        print(line)
    
    # Print layer information
    print()
    print("Layers:")
    for i, layer in enumerate(network.layers):
        comps = ", ".join(str(c) for c in layer)
        print(f"  {i}: {comps}")
    
    print("=" * 70)
    print()


def visualize_network_detailed(network, title="Sorting Network"):
    """
    Generate a more detailed ASCII visualization showing comparator connections.
    """
    n = network.n
    depth = network.depth()
    
    print("=" * 80)
    print(f"  {title}")
    print(f"  Elements: {n}, Depth: {depth}, Size: {network.size()}")
    print("=" * 80)
    print()
    
    # For each layer, show the comparators
    for layer_idx, layer in enumerate(network.layers):
        print(f"Layer {layer_idx}:")
        
        # Create a visual representation of this layer
        for i in range(n):
            line = f"  {i}: "
            
            # Check if this element is part of a comparator in this layer
            comp_with = None
            is_min = False
            
            for comp in layer:
                if comp.i == i:
                    comp_with = comp.j
                    is_min = True
                    break
                elif comp.j == i:
                    comp_with = comp.i
                    is_min = False
                    break
            
            if comp_with is not None:
                if is_min:
                    line += f"├──────┬ compare with {comp_with}, output min"
                else:
                    line += f"└──────┘ compare with {comp_with}, output max"
            else:
                line += "────────  (pass through)"
            
            print(line)
        print()
    
    print("=" * 80)
    print()


def print_execution_trace(network, input_data):
    """
    Show step-by-step execution of the network on specific input.
    """
    n = network.n
    if len(input_data) != n:
        print(f"Error: input must have {n} elements")
        return
    
    print("=" * 80)
    print(f"  Execution Trace")
    print("=" * 80)
    print(f"Input: {input_data}")
    print()
    
    current = input_data.copy()
    
    for layer_idx, layer in enumerate(network.layers):
        print(f"Layer {layer_idx}: {layer}")
        
        # Show the state before this layer
        print(f"  Before: {current}")
        
        # Apply comparators
        next_state = current.copy()
        for comp in layer:
            if current[comp.i] > current[comp.j]:
                next_state[comp.i], next_state[comp.j] = current[comp.j], current[comp.i]
                print(f"    Swap ({comp.i}, {comp.j}): {current[comp.i]} <-> {current[comp.j]}")
        
        current = next_state
        print(f"  After:  {current}")
        print()
    
    print(f"Output: {current}")
    print(f"Sorted: {current == sorted(input_data)}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    # Visualize a 4-element network
    net4 = find_optimal_network(4)
    visualize_network(net4, "Optimal 4-Element Sorting Network")
    visualize_network_detailed(net4, "Detailed View - 4 Elements")
    
    # Show execution trace
    print_execution_trace(net4, [4, 2, 3, 1])
    print_execution_trace(net4, [3, 1, 4, 2])
    
    # Visualize a 6-element network
    net6 = find_optimal_network(6)
    visualize_network(net6, "Optimal 6-Element Sorting Network")
    
    # Show execution trace for 6 elements
    print_execution_trace(net6, [6, 3, 1, 5, 2, 4])
