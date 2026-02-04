## Authors
- Tyler Pham
- Carlos Ponce

# Erdős–Rényi Graph Analyzer

A comprehensive Python tool for generating, analyzing, and visualizing Erdős–Rényi random graphs with advanced features including multi-source BFS, connected component analysis, cycle detection, and rich visualization.

## Features

- **Graph Generation**: Create Erdős–Rényi random graphs with specified nodes and edges/average degree
- **File I/O**: Import and export graphs in `.gml` format
- **Multi-Source BFS**: Perform breadth-first search from multiple nodes with path tracking
- **Graph Analysis**: 
  - Identify connected components
  - Detect cycles
  - Find isolated nodes
  - Calculate degree statistics
- **Visualization**: Rich graph visualization with color-coded components and highlighted paths

## Requirements

```bash
pip install networkx matplotlib
```

## Usage

### Basic Command Structure

```bash
python graph.py [--input FILE] [--create_random_graph N C] 
                [--multi_BFS NODE ...] [--analyze] [--plot] 
                [--output FILE]
```

### Command-Line Arguments

| Argument | Description |
|----------|-------------|
| `--input FILE` | Load graph from `.gml` file |
| `--create_random_graph N C` | Create Erdős–Rényi graph with N nodes and C edges/avg_degree |
| `--multi_BFS NODE [NODE...]` | Perform BFS from specified nodes |
| `--analyze` | Analyze graph structure (components, cycles, etc.) |
| `--plot` | Visualize the graph |
| `--output FILE` | Save graph to `.gml` file |

### Parameter Types

**`--create_random_graph N C`**:
- **N** (integer): Number of nodes
- **C** (float): Constant for edge probability formula
  - Edge probability: **p = (C · ln N) / N**
  - This creates an Erdős–Rényi random graph using the G(n,p) model
  - Example: `N=200, C=1.01` gives `p = (1.01 × ln 200) / 200 ≈ 0.0268` (2.68% chance for each edge)

## Examples

### Example 1: Create Random Graph with Specified Edge Probability

Create a graph with 20 nodes using c=1.5:

```bash
python graph.py --create_random_graph 20 1.5 --plot
```

**Output:**
```
============================================================
ERDŐS–RÉNYI GRAPH ANALYZER
============================================================

✓ Created Erdős–Rényi graph with n=20, c=1.50
  Edge probability p = (c·ln n)/n = (1.50·ln 20)/20 = 0.2246
  Generated 42 edges
Generating visualization...
✓ Graph visualization displayed
```

### Example 2: Create Graph and Analyze

Create a graph with 200 nodes and c=1.01, then analyze it:

```bash
python graph.py --create_random_graph 200 1.01 --analyze --output my_graph.gml
```

**Output:**
```
============================================================
ERDŐS–RÉNYI GRAPH ANALYZER
============================================================

✓ Created Erdős–Rényi graph with n=200, c=1.01
  Edge probability p = (c·ln n)/n = (1.01·ln 200)/200 = 0.0268
  Generated 534 edges

============================================================
GRAPH ANALYSIS
============================================================

Basic Statistics:
  Nodes: 200
  Edges: 534

Connected Components: 1
  Component 1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]... (200 nodes)

Isolated Nodes: 0

Cycle Detection:
  Contains cycles: Yes

Graph Density:
  Density: 0.026834
  (Ratio of actual edges to maximum possible edges)

Average Shortest Path Length:
  Average: 3.5421
  (Average number of steps along shortest paths for all pairs of nodes)

Degree Statistics:
  Average degree: 5.34
  Min degree: 1
  Max degree: 14
============================================================

✓ Saved graph to my_graph.gml
  Included component IDs for 1 component(s)
```

### Example 3: Multi-Source BFS with Attribute Storage

Perform BFS from multiple nodes and save with computed attributes:

```bash
python graph.py --create_random_graph 50 1.5 --multi_BFS 0 10 20 --output result.gml
```

**Output:**
```
✓ Created Erdős–Rényi graph with n=50, c=1.50
  Edge probability p = (c·ln n)/n = (1.50·ln 50)/50 = 0.1173
  Generated 140 edges

✓ BFS from node 0: reached 50 nodes
✓ BFS from node 10: reached 50 nodes
✓ BFS from node 20: reached 50 nodes

✓ Saved graph to result.gml
  Included BFS attributes from 3 source(s)
  Included component IDs for 1 component(s)
```

The output file includes node attributes:
- `component_id`: Which component each node belongs to
-distance_from_0`, `distance_from_10`, `distance_from_20`: BFS distances
- `parent_from_0`, `parent_from_10`, `parent_from_20`: Parent nodes in BFS trees

### Example 4: Complete Workflow

Generate, analyze, and export in one command:

```bash
python graph.py --create_random_graph 50 2.5 --multi_BFS 0 10 20 --analyze --plot --output result.gml
```

### Example 5: Analyze Existing Graph

Load and analyze a graph from file:

```bash
python graph.py --input existing_graph.gml --analyze --plot
```

## Implementation Details

### Modular Architecture

The implementation follows a clean, modular design pattern:

#### 1. **Graph Generation Module**
- `GraphAnalyzer.create_erdos_renyi_graph(n, c)`: Creates random graphs
- Uses edge probability formula: **p = (c · ln n) / n**
- Implements the Erdős–Rényi G(n,p) model
- Validates parameters to prevent invalid configurations

#### 2. **File I/O Module**
- `GraphAnalyzer.load_graph(filename)`: Imports graphs from `.gml` files
- `GraphAnalyzer.save_graph(filename)`: Exports graphs to `.gml` files with computed attributes
- Stores BFS distances, parent nodes, and component IDs as node attributes
- Handles node label conversions for GML compatibility

#### 3. **Graph Algorithms Module**

**Multi-Source BFS:**
- `GraphAnalyzer.multi_source_bfs(sources)`: Performs BFS from multiple nodes
- `GraphAnalyzer.get_path(source, target)`: Reconstructs paths using parent tracking
- Tracks visited nodes, parent relationships, and depth levels

**Connected Components:**
- Uses NetworkX's `connected_components()` for efficient component detection
- Groups nodes into disjoint connected subgraphs

**Cycle Detection:**
- Employs `simple_cycles()` for directed graph analysis
- Component-based detection for undirected graphs
- Samples cycles to avoid performance issues on large graphs

**Isolated Nodes:**
- Identifies nodes with degree 0
- Useful for understanding graph connectivity

#### 4. **Visualization Module**
- `GraphAnalyzer.visualize(highlight_paths)`: Creates rich graph visualizations
- Features:
  - Spring layout algorithm for optimal node positioning
  - Color-coding by connected components
  - BFS path highlighting with unique colors per source
  - Special markers for isolated nodes (squares) and BFS sources (yellow circles)
  - Adaptive label display (shown only for smaller graphs)
  - Comprehensive statistics in title

#### 5. **Argument Parsing and Orchestration**
- `main()`: Command-line interface handler using `argparse`
- Validates argument combinations
- Orchestrates workflow execution
- Provides comprehensive help text and examples

### Error Handling

The implementation includes robust error handling for common scenarios:

#### File Not Found
```python
try:
    analyzer.load_graph(args.input)
except Exception as e:
    print(f"✗ Error loading graph: {e}")
    return 1
```

**Example:**
```bash
python graph.py --input nonexistent.gml
# Output: ✗ Error loading graph: [Errno 2] No such file or directory: 'nonexistent.gml'
```

#### Malformed Input Graphs
- NetworkX handles malformed `.gml` files with descriptive error messages
- Node label conversion attempts to parse integers, falls back to strings

#### Invalid Node IDs
```python
if source not in self.graph.nodes():
    print(f"⚠ Warning: Node {source} not in graph, skipping")
    continue
```

**Example:**
```bash
python graph.py --input graph.gml --multi_BFS 999
# Output: ⚠ Warning: Node 999 not in graph, skipping
```

#### Insufficient or Invalid Parameters
```python
if c > n * (n - 1) // 2:
    raise ValueError(f"Too many edges! Maximum is {n * (n - 1) // 2} for {n} nodes")
```

**Example:**
```bash
python graph.py --create_random_graph 10 100
# Output: ✗ Error creating graph: Too many edges! Maximum is 45 for 10 nodes
```

#### Mutually Exclusive Options
```python
if args.input and args.create_random_graph:
    parser.error("Cannot specify both --input and --create_random_graph")
```

#### Empty Graph Visualization
```python
if self.graph.number_of_nodes() == 0:
    print("⚠ Cannot visualize empty graph")
    return
```

### Code Documentation

All functions include comprehensive docstrings following Google style:

```python
def multi_source_bfs(self, sources: List[int]) -> Dict[int, Dict]:
    """
    Perform multi-source BFS from multiple starting nodes
    Tracks paths and discovery information
    
    Args:
        sources: List of source node IDs
    
    Returns:
        Dictionary with path information for each source
    """
```

Key implementation details are documented with inline comments explaining:
- Algorithm choices
- Data structure usage
- Edge case handling
- Performance considerations

## Output Visualization Features

When using `--plot`, the visualization includes:

- **Color-Coded Components**: Each connected component has a unique color
- **BFS Path Highlighting**: Paths explored from each BFS source shown in distinct colors
- **Node Markers**:
  - Regular nodes: circles
  - Isolated nodes: squares
  - BFS source nodes: yellow circles with black borders
- **Graph Statistics**: Title displays node count, edge count, and component count
- **Adaptive Labels**: Node labels shown for graphs with ≤50 nodes
- **Legend**: Identifies BFS sources and isolated nodes

## Testing

To verify the implementation:

```bash
# Test basic creation
python graph.py --create_random_graph 15 20 --analyze

# Test file I/O
python graph.py --create_random_graph 25 35 --output test.gml
python graph.py --input test.gml --analyze

# Test multi-source BFS
python graph.py --create_random_graph 30 40 --multi_BFS 0 10 20 --plot

# Test average degree
python graph.py --create_random_graph 100 2.5 --analyze

# Test error handling
python graph.py --input nonexistent.gml
python graph.py --create_random_graph 10 100
python graph.py --input test.gml --multi_BFS 9999
```

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: NetworkX (graph algorithms), Matplotlib (visualization)
- **Graph Format**: GML (Graph Modeling Language)
- **Layout Algorithm**: Spring layout (Fruchterman-Reingold force-directed)
- **Complexity**: 
  - Graph generation: O(n²) for creating possible edges, O(c) for adding them
  - BFS: O(V + E) per source
  - Connected components: O(V + E)
  - Visualization: O(V² + E) for layout computation
