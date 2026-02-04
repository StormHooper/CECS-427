"""
Erdős–Rényi Random Graph Generation, Analysis, Transformation, and Visualization
Authors: Tyler Pham, Carlos Ponce
"""

import argparse
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from typing import List, Dict, Set, Tuple, Optional


class GraphAnalyzer:
    """Class for analyzing and visualizing graphs"""
    
    def __init__(self, graph: Optional[nx.Graph] = None):
        """Initialize the analyzer with an optional graph"""
        self.graph = graph if graph is not None else nx.Graph()
        self.bfs_paths = {}
        self.analysis_results = {}
    
    def create_erdos_renyi_graph(self, n: int, c: float) -> nx.Graph:
        """
        Create an Erdős–Rényi random graph with n nodes
        Uses edge probability p = (c·ln n)/n as per specification
        
        Args:
            n: Number of nodes
            c: Constant for edge probability formula p = (c·ln n)/n
        
        Returns:
            Generated graph
        """
        import math
        
        # Calculate edge probability using the specified formula: p = (c·ln n)/n
        if n <= 0:
            raise ValueError("Number of nodes must be positive")
        
        p = (c * math.log(n)) / n
        
        # Validate probability is in valid range [0, 1]
        if p < 0:
            raise ValueError(f"Edge probability cannot be negative (c={c} gives p={p:.4f})")
        if p > 1:
            print(f"  ⚠ Warning: Edge probability p={p:.4f} > 1, clamping to 1.0")
            p = 1.0
        
        # Create empty graph with n nodes
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(n))
        
        # Generate edges with probability p
        # For each possible edge, add it with probability p
        edges_added = 0
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < p:
                    self.graph.add_edge(i, j)
                    edges_added += 1
        
        print(f"✓ Created Erdős–Rényi graph with n={n}, c={c:.2f}")
        print(f"  Edge probability p = (c·ln n)/n = ({c:.2f}·ln {n})/{n} = {p:.4f}")
        print(f"  Generated {edges_added} edges")
        return self.graph
    
    def load_graph(self, filename: str) -> nx.Graph:
        """
        Load a graph from a .gml file with robust error handling
        
        Args:
            filename: Path to the .gml file
        
        Returns:
            Loaded graph
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is malformed or not a valid GML file
        """
        # Check if file exists before attempting to load
        import os
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Graph file not found: {filename}")
        
        try:
            self.graph = nx.read_gml(filename)
        except Exception as e:
            raise ValueError(f"Malformed or invalid GML file: {e}")
        
        # Validate that we actually loaded a graph with some content
        if self.graph is None:
            raise ValueError("Failed to load graph: result is None")
        
        # Convert node labels to integers if possible for easier manipulation
        # This handles the common case where GML stores integers as strings
        mapping = {}
        for node in self.graph.nodes():
            try:
                mapping[node] = int(node)
            except (ValueError, TypeError):
                # Keep original label if not convertible to int
                mapping[node] = node
        self.graph = nx.relabel_nodes(self.graph, mapping)
        
        print(f"✓ Loaded graph from {filename}")
        print(f"  Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
        return self.graph
    
    def save_graph(self, filename: str):
        """
        Save the current graph to a .gml file with error handling
        Includes all computed attributes (distances, parent nodes, component IDs)
        
        Args:
            filename: Output file path
            
        Raises:
            ValueError: If graph is empty
            IOError: If file cannot be written
        """
        # Validate graph before saving
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Cannot save empty graph")
        
        # Create a copy of the graph to add computed attributes
        output_graph = self.graph.copy()
        
        # Add component IDs to nodes
        components = list(nx.connected_components(self.graph))
        node_to_component = {}
        for comp_id, component in enumerate(components):
            for node in component:
                node_to_component[node] = comp_id
        
        # Add attributes to each node
        for node in output_graph.nodes():
            # Component ID
            output_graph.nodes[node]['component_id'] = node_to_component.get(node, -1)
            
            # BFS distances and parents from each source
            if self.bfs_paths:
                for source, bfs_info in self.bfs_paths.items():
                    # Add distance (level) from this source
                    if node in bfs_info['level']:
                        output_graph.nodes[node][f'distance_from_{source}'] = bfs_info['level'][node]
                    
                    # Add parent from this source
                    if node in bfs_info['parent'] and bfs_info['parent'][node] is not None:
                        output_graph.nodes[node][f'parent_from_{source}'] = bfs_info['parent'][node]
        
        # Convert all node labels and attributes to strings for GML format compatibility
        # GML format requires string labels
        string_graph = nx.Graph()
        for node in output_graph.nodes():
            # Add node with all its attributes converted to strings
            attrs = {}
            for key, value in output_graph.nodes[node].items():
                attrs[str(key)] = str(value)
            string_graph.add_node(str(node), **attrs)
        
        for u, v in output_graph.edges():
            string_graph.add_edge(str(u), str(v))
        
        try:
            nx.write_gml(string_graph, filename)
            print(f"✓ Saved graph to {filename}")
            if self.bfs_paths:
                print(f"  Included BFS attributes from {len(self.bfs_paths)} source(s)")
            print(f"  Included component IDs for {len(components)} component(s)")
        except Exception as e:
            raise IOError(f"Failed to write graph file: {e}")
    
    def multi_source_bfs(self, sources: List[int]) -> Dict[int, Dict]:
        """
        Perform multi-source BFS from multiple starting nodes
        Tracks paths and discovery information using standard BFS algorithm
        
        Algorithm: For each source, perform iterative BFS using a queue:
        1. Initialize queue with source node
        2. Track visited nodes to avoid cycles
        3. For each node, explore all unvisited neighbors
        4. Record parent relationships for path reconstruction
        5. Track depth level for each discovered node
        
        Args:
            sources: List of source node IDs to start BFS from
        
        Returns:
            Dictionary mapping each source to its BFS results:
            - 'visited': set of reachable nodes
            - 'parent': dict for path reconstruction
            - 'level': depth of each node from source
            - 'reachable_count': number of nodes reached
        """
        self.bfs_paths = {}
        
        # Validate inputs
        if not sources:
            print("⚠ Warning: No source nodes provided for BFS")
            return self.bfs_paths
        
        for source in sources:
            # Check if node exists in graph - robust error handling
            if source not in self.graph.nodes():
                print(f"⚠ Warning: Node {source} not in graph, skipping")
                continue
            
            # BFS tracking data structures
            visited = {source}  # Set for O(1) membership checking
            queue = deque([source])  # Queue for FIFO processing
            parent = {source: None}  # For path reconstruction
            level = {source: 0}  # Distance from source
            
            # Standard BFS loop
            while queue:
                node = queue.popleft()
                
                # Explore all neighbors of current node
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        parent[neighbor] = node
                        level[neighbor] = level[node] + 1
            
            # Store BFS results for this source
            self.bfs_paths[source] = {
                'visited': visited,
                'parent': parent,
                'level': level,
                'reachable_count': len(visited)
            }
            
            print(f"✓ BFS from node {source}: reached {len(visited)} nodes")
        
        return self.bfs_paths
    
    def get_path(self, source: int, target: int) -> Optional[List[int]]:
        """
        Reconstruct shortest path from source to target using BFS parent pointers
        
        Algorithm: Backtrack from target to source using parent relationships,
        then reverse to get path from source to target
        
        Args:
            source: Source node ID
            target: Target node ID
        
        Returns:
            List of nodes forming shortest path, or None if:
            - BFS hasn't been run from source
            - Target is not reachable from source
        """
        # Validate that BFS was performed from this source
        if source not in self.bfs_paths:
            print(f"⚠ BFS not performed from node {source}")
            return None
        
        # Check if target is reachable
        if target not in self.bfs_paths[source]['visited']:
            return None
        
        # Reconstruct path by following parent pointers backwards
        path = []
        current = target
        parent = self.bfs_paths[source]['parent']
        
        # Walk backwards from target to source
        while current is not None:
            path.append(current)
            current = parent[current]
        
        # Reverse to get path from source to target
        path.reverse()
        return path
    
    def analyze_graph(self) -> Dict:
        """
        Perform comprehensive graph analysis:
        - Connected components
        - Cycles detection
        - Isolated nodes
        - Graph density
        - Average shortest path length
        
        Returns:
            Dictionary with analysis results
        """
        print("\n" + "="*60)
        print("GRAPH ANALYSIS")
        print("="*60)
        
        # Basic stats
        n_nodes = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        print(f"\nBasic Statistics:")
        print(f"  Nodes: {n_nodes}")
        print(f"  Edges: {n_edges}")
        
        # Connected components
        components = list(nx.connected_components(self.graph))
        n_components = len(components)
        print(f"\nConnected Components: {n_components}")
        for i, component in enumerate(components, 1):
            print(f"  Component {i}: {sorted(list(component))[:10]}" + 
                  (f"... ({len(component)} nodes)" if len(component) > 10 else f" ({len(component)} nodes)"))
        
        # Isolated nodes (nodes with degree 0)
        isolated = [node for node in self.graph.nodes() if self.graph.degree(node) == 0]
        print(f"\nIsolated Nodes: {len(isolated)}")
        if isolated:
            print(f"  {isolated[:20]}" + ("..." if len(isolated) > 20 else ""))
        
        # Cycle detection
        has_cycle = False
        cycles = []
        try:
            # Find simple cycles (limited to first few for performance)
            cycle_gen = nx.simple_cycles(self.graph.to_directed())
            for i, cycle in enumerate(cycle_gen):
                if i >= 5:  # Limit to first 5 cycles
                    has_cycle = True
                    break
                cycles.append(cycle)
                has_cycle = True
        except:
            # For undirected graphs, check if it's a tree
            if nx.is_connected(self.graph):
                has_cycle = n_edges >= n_nodes
            else:
                # Check each component
                for component in components:
                    subgraph = self.graph.subgraph(component)
                    if subgraph.number_of_edges() >= subgraph.number_of_nodes():
                        has_cycle = True
                        break
        
        print(f"\nCycle Detection:")
        print(f"  Contains cycles: {'Yes' if has_cycle else 'No'}")
        if cycles:
            print(f"  Sample cycles found: {len(cycles)}")
            for i, cycle in enumerate(cycles[:3], 1):
                print(f"    Cycle {i}: {cycle}")
        
        # Graph Density
        # Density = (number of edges) / (maximum possible edges)
        # For undirected graph: max_edges = n*(n-1)/2
        if n_nodes <= 1:
            density = 0.0
        else:
            max_possible_edges = n_nodes * (n_nodes - 1) / 2
            density = n_edges / max_possible_edges if max_possible_edges > 0 else 0.0
        
        print(f"\nGraph Density:")
        print(f"  Density: {density:.6f}")
        print(f"  (Ratio of actual edges to maximum possible edges)")
        
        # Average Shortest Path Length
        # Only computable for connected graphs
        avg_shortest_path = None
        if nx.is_connected(self.graph):
            try:
                avg_shortest_path = nx.average_shortest_path_length(self.graph)
                print(f"\nAverage Shortest Path Length:")
                print(f"  Average: {avg_shortest_path:.4f}")
                print(f"  (Average number of steps along shortest paths for all pairs of nodes)")
            except Exception as e:
                print(f"\nAverage Shortest Path Length:")
                print(f"  Could not compute: {e}")
        else:
            print(f"\nAverage Shortest Path Length:")
            print(f"  Not applicable (graph is disconnected)")
            print(f"  Computing for largest component:")
            
            # Find largest component and compute for it
            largest_component = max(components, key=len)
            if len(largest_component) > 1:
                try:
                    subgraph = self.graph.subgraph(largest_component)
                    avg_shortest_path = nx.average_shortest_path_length(subgraph)
                    print(f"    Largest component ({len(largest_component)} nodes): {avg_shortest_path:.4f}")
                except Exception as e:
                    print(f"    Could not compute: {e}")
        
        # Degree distribution
        degrees = dict(self.graph.degree())
        if degrees:
            max_degree = max(degrees.values())
            min_degree = min(degrees.values())
            avg_degree = sum(degrees.values()) / len(degrees)
            print(f"\nDegree Statistics:")
            print(f"  Average degree: {avg_degree:.2f}")
            print(f"  Min degree: {min_degree}")
            print(f"  Max degree: {max_degree}")
        
        # Store results
        self.analysis_results = {
            'n_nodes': n_nodes,
            'n_edges': n_edges,
            'n_components': n_components,
            'components': components,
            'isolated_nodes': isolated,
            'has_cycle': has_cycle,
            'sample_cycles': cycles,
            'degrees': degrees,
            'density': density,
            'avg_shortest_path': avg_shortest_path
        }
        
        print("="*60 + "\n")
        
        return self.analysis_results
    
    def visualize(self, highlight_paths: bool = True):
        """
        Visualize the graph with annotations
        
        Args:
            highlight_paths: Whether to highlight BFS paths
        """
        if self.graph.number_of_nodes() == 0:
            print("⚠ Cannot visualize empty graph")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Layout
        if self.graph.number_of_nodes() <= 100:
            pos = nx.spring_layout(self.graph, k=1, iterations=50, seed=42)
        else:
            pos = nx.spring_layout(self.graph, k=0.5, iterations=30, seed=42)
        
        # Color nodes based on connected components
        components = list(nx.connected_components(self.graph))
        node_colors = []
        color_map = plt.cm.Set3(range(len(components)))
        
        node_to_component = {}
        for i, component in enumerate(components):
            for node in component:
                node_to_component[node] = i
        
        for node in self.graph.nodes():
            node_colors.append(color_map[node_to_component[node]])
        
        # Draw base graph
        nx.draw_networkx_edges(self.graph, pos, alpha=0.3, width=1, edge_color='gray', ax=ax)
        
        # Highlight BFS paths if available
        if highlight_paths and self.bfs_paths:
            colors_palette = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
            for idx, (source, bfs_info) in enumerate(self.bfs_paths.items()):
                color = colors_palette[idx % len(colors_palette)]
                
                # Highlight edges in BFS tree
                bfs_edges = []
                for node, parent in bfs_info['parent'].items():
                    if parent is not None:
                        bfs_edges.append((parent, node))
                
                if bfs_edges:
                    nx.draw_networkx_edges(self.graph, pos, edgelist=bfs_edges,
                                         width=2, alpha=0.7, edge_color=color,
                                         arrows=True, arrowsize=15, ax=ax,
                                         label=f'BFS from {source}')
        
        # Draw nodes
        isolated_nodes = [n for n in self.graph.nodes() if self.graph.degree(n) == 0]
        regular_nodes = [n for n in self.graph.nodes() if n not in isolated_nodes]
        
        if regular_nodes:
            regular_colors = [node_colors[list(self.graph.nodes()).index(n)] for n in regular_nodes]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=regular_nodes,
                                 node_color=regular_colors, node_size=300,
                                 alpha=0.9, ax=ax)
        
        if isolated_nodes:
            isolated_colors = [node_colors[list(self.graph.nodes()).index(n)] for n in isolated_nodes]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=isolated_nodes,
                                 node_color=isolated_colors, node_size=400,
                                 alpha=0.9, node_shape='s', ax=ax,
                                 label='Isolated nodes')
        
        # Highlight BFS source nodes
        if self.bfs_paths:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=list(self.bfs_paths.keys()),
                                 node_color='yellow', node_size=500,
                                 alpha=1.0, edgecolors='black', linewidths=2, ax=ax)
        
        # Draw labels
        if self.graph.number_of_nodes() <= 50:
            nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold', ax=ax)
        
        # Title and legend
        title = f"Graph Visualization\n{self.graph.number_of_nodes()} nodes, "
        title += f"{self.graph.number_of_edges()} edges, "
        title += f"{len(components)} component{'s' if len(components) != 1 else ''}"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        if highlight_paths and self.bfs_paths or isolated_nodes:
            ax.legend(loc='upper left', fontsize=9)
        
        ax.axis('off')
        plt.tight_layout()
        plt.show()
        
        print("✓ Graph visualization displayed")


def main():
    """Main function to handle command-line interface"""
    parser = argparse.ArgumentParser(
        description='Erdős–Rényi Graph Generator and Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create random graph:
    python graph.py --create_random_graph 10 15 --plot --output my_graph.gml
  
  Analyze existing graph:
    python graph.py --input graph.gml --analyze --plot
  
  Multi-source BFS:
    python graph.py --input graph.gml --multi_BFS 0 5 10 --plot
  
  Complete workflow:
    python graph.py --create_random_graph 20 30 --multi_BFS 0 10 --analyze --plot --output result.gml
        """
    )
    
    parser.add_argument('--input', type=str, metavar='FILE',
                       help='Input graph file (.gml format)')
    parser.add_argument('--create_random_graph', nargs=2, metavar=('N', 'C'),
                       help='Create Erdős–Rényi graph with N nodes and C edges/avg_degree (int=edges, float=avg_degree)')
    parser.add_argument('--multi_BFS', nargs='+', type=int, metavar='NODE',
                       help='Perform multi-source BFS from specified nodes')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze graph (components, cycles, isolated nodes)')
    parser.add_argument('--plot', action='store_true',
                       help='Visualize the graph')
    parser.add_argument('--output', type=str, metavar='FILE',
                       help='Output graph file (.gml format)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.input and not args.create_random_graph:
        parser.error("Must specify either --input or --create_random_graph")
    
    if args.input and args.create_random_graph:
        parser.error("Cannot specify both --input and --create_random_graph")
    
    # Initialize analyzer
    analyzer = GraphAnalyzer()
    
    print("\n" + "="*60)
    print("ERDŐS–RÉNYI GRAPH ANALYZER")
    print("="*60 + "\n")
    
    # Load or create graph
    if args.input:
        try:
            analyzer.load_graph(args.input)
        except Exception as e:
            print(f"✗ Error loading graph: {e}")
            return 1
    elif args.create_random_graph:
        n_str, c_str = args.create_random_graph
        try:
            n = int(n_str)
            # Try to parse c as float (supports both int and float)
            c = float(c_str)
            analyzer.create_erdos_renyi_graph(n, c)
        except Exception as e:
            print(f"✗ Error creating graph: {e}")
            return 1
    
    # Perform multi-source BFS
    if args.multi_BFS:
        print()
        try:
            analyzer.multi_source_bfs(args.multi_BFS)
        except Exception as e:
            print(f"✗ Error in BFS: {e}")
    
    # Analyze graph
    if args.analyze:
        try:
            analyzer.analyze_graph()
        except Exception as e:
            print(f"✗ Error analyzing graph: {e}")
    
    # Save graph
    if args.output:
        try:
            analyzer.save_graph(args.output)
        except Exception as e:
            print(f"✗ Error saving graph: {e}")
    
    # Visualize
    if args.plot:
        print("\nGenerating visualization...")
        try:
            analyzer.visualize(highlight_paths=bool(args.multi_BFS))
        except Exception as e:
            print(f"✗ Error visualizing graph: {e}")
    
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60 + "\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
