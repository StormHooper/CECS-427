"""
graph.py
Author(s): Tyler Pham
"""

import argparse
import math
import sys

import networkx as nx
import matplotlib.pyplot as plt


# Argument Parsing
def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Graph analysis and visualization tool"
    )

    parser.add_argument("--input", type=str,
                        help="Input graph file (.gml)")

    parser.add_argument("--create_random_graph", nargs=2, metavar=("n", "c"),
                        help="Create Erdős–Rényi graph with n nodes and parameter c")

    parser.add_argument("--multi_BFS", nargs="+",
                        help="Run BFS from one or more source nodes")

    parser.add_argument("--analyze", action="store_true",
                        help="Perform structural graph analysis")

    parser.add_argument("--plot", action="store_true",
                        help="Visualize the graph")

    parser.add_argument("--output", type=str,
                        help="Output graph file (.gml)")

    return parser.parse_args()

# Graph Generation & I/O
def generate_random_graph(n, c):
    """
    Generate an Erdős–Rényi random graph.

    p = (c * ln(n)) / n
    Nodes are labeled as strings: "0", "1", ..., "n-1"
    """
    n = int(n)
    c = float(c)

    p = (c * math.log(n)) / n
    G = nx.erdos_renyi_graph(n, p)

    # Relabel nodes to strings
    G = nx.relabel_nodes(G, lambda x: str(x))
    return G


def load_graph(filename):
    """Load a graph from a GML file."""
    try:
        return nx.read_gml(filename)
    except Exception as e:
        print(f"Error reading graph file: {e}")
        sys.exit(1)


def save_graph(G, filename):
    """Save graph with attributes to a GML file."""
    try:
        nx.write_gml(G, filename)
    except Exception as e:
        print(f"Error writing graph file: {e}")


# Graph Algorithms
def multi_source_bfs(G, sources):
    """
    Run BFS from multiple source nodes.

    Returns:
        dict[source] = {
            "distances": {node: distance},
            "parents": {node: parent}
        }
    """
    bfs_results = {}

    for source in sources:
        if source not in G:
            raise ValueError(f"BFS source {source} not in graph")

        distances = dict(nx.single_source_shortest_path_length(G, source))
        paths = nx.single_source_shortest_path(G, source)

        parents = {}
        for node, path in paths.items():
            parents[node] = path[-2] if len(path) > 1 else None

        bfs_results[source] = {
            "distances": distances,
            "parents": parents
        }

    return bfs_results


def analyze_graph(G):
    """
    Perform structural analysis on the graph.
    Prints results to the terminal.
    """
    print("\n--- Graph Analysis ---")

    # Connected components
    components = list(nx.connected_components(G))
    print(f"Connected Components: {len(components)}")

    # Cycle detection
    has_cycle = not nx.is_forest(G)
    print(f"Contains Cycle: {has_cycle}")

    # Isolated nodes
    isolated = list(nx.isolates(G))
    print(f"Isolated Nodes: {len(isolated)}")

    # Graph density
    density = nx.density(G)
    print(f"Graph Density: {density:.4f}")

    # Average shortest path length
    if nx.is_connected(G):
        avg_len = nx.average_shortest_path_length(G)
        print(f"Average Shortest Path Length: {avg_len:.4f}")
    else:
        print("Average Shortest Path Length: N/A (Graph not connected)")

# Visualization
def plot_graph(G, bfs_results=None):
    """Visualize graph and BFS paths."""
    pos = nx.spring_layout(G)

    plt.figure(figsize=(10, 8))

    # Draw base graph
    nx.draw(G, pos, node_size=50, with_labels=False)

    # Highlight isolated nodes
    isolated = list(nx.isolates(G))
    nx.draw_networkx_nodes(G, pos, nodelist=isolated, node_color="red")

    # BFS visualization placeholder
    if bfs_results:
        for source, data in bfs_results.items():
            edges = []
            for node, parent in data["parents"].items():
                if parent is not None:
                    edges.append((parent, node))
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=2)

    plt.title("Graph Visualization")
    plt.show()



# Main Program
def main():
    args = parse_arguments()

    G = None

    # Graph creation or loading
    if args.create_random_graph:
        G = generate_random_graph(*args.create_random_graph)
    elif args.input:
        G = load_graph(args.input)
    else:
        print("Error: No graph source provided.")
        sys.exit(1)

    bfs_results = None

    # Multi-source BFS
    if args.multi_BFS:
        bfs_results = multi_source_bfs(G, args.multi_BFS)

    # Analysis
    if args.analyze:
        analyze_graph(G)

    # Plotting
    if args.plot:
        plot_graph(G, bfs_results)

    # Output
    if args.output:
        save_graph(G, args.output)


if __name__ == "__main__":
    main()
