import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import string
import pandas as pd
import numpy as np
from tabulate import tabulate

# Constants for styling
EMSI_GREEN = "#006838"
DARK_GRAY = "#333333"
WINDOW_BG = "#FFFFFF"

# Function to show graph in 3D in a new window (with Tkinter integration)
def show_graph_in_new_window_3d(graph, title, path=None, mst_edges=None, bellman_ford_paths=None):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    pos = nx.spring_layout(graph, dim=3)
    x, y, z = zip(*[pos[node] for node in graph.nodes()])

    node_colors = ['lightblue' if node not in path else 'green' for node in graph.nodes()] if path else 'lightblue'
    ax.scatter(x, y, z, s=700, c=node_colors, marker='o')

    for edge in graph.edges():
        edge_color = 'gray'
        if mst_edges and edge in mst_edges:
            edge_color = 'red'
        elif path and (edge[0] in path and edge[1] in path):
            edge_color = 'red'
        elif bellman_ford_paths:
            for p in bellman_ford_paths.values():
                if edge[0] in p and edge[1] in p and p.index(edge[1]) == p.index(edge[0]) + 1:
                    edge_color = 'red'
                    break
        ax.plot(*zip(pos[edge[0]], pos[edge[1]]), color=edge_color)

    if path:
        path_edges = list(zip(path, path[1:]))
        for edge in path_edges:
            ax.plot(*zip(pos[edge[0]], pos[edge[1]]), color='red', linewidth=2)

    ax.set_title(title)

    # Creating a Tkinter window to embed the plot
    plot_window = tk.Toplevel()
    plot_window.title(title)

    # Embed the matplotlib plot into Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Welsh-Powell algorithm
def generate_random_graph(num_vertices, probability):
    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices))
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if random.random() < probability:
                graph.add_edge(i, j)
    return graph

def welsh_powell(graph):
    sorted_nodes = sorted(graph.degree, key=lambda x: x[1], reverse=True)
    sorted_nodes = [node for node, degree in sorted_nodes]
    colors = {}
    current_color = 0
    for node in sorted_nodes:
        if node not in colors:
            colors[node] = current_color
            for other_node in sorted_nodes:
                if other_node not in colors and not any(graph.has_edge(other_node, n) for n in colors if colors[n] == current_color):
                    colors[other_node] = current_color
            current_color += 1
    return colors

# Dijkstra algorithm
def generate_weighted_graph(num_vertices, probability):
    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices))
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if random.random() < probability:
                weight = random.randint(1, 100)
                graph.add_edge(i, j, weight=weight)
    return graph

def dijkstra(graph, start, end):
    path = nx.dijkstra_path(graph, start, end, weight='weight')
    return path

# Kruskal algorithm
def generate_labeled_weighted_graph(num_vertices, probability):
    graph = nx.Graph()
    labels = [c for c in string.ascii_uppercase[:num_vertices]]
    graph.add_nodes_from(labels)
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if random.random() < probability:
                weight = random.randint(1, 100)
                graph.add_edge(labels[i], labels[j], weight=weight)
    return graph

def kruskal(graph):
    edges = sorted(graph.edges(data=True), key=lambda x: x[2]['weight'])
    mst = nx.Graph()
    mst.add_nodes_from(graph.nodes())
    union_find = {node: node for node in graph.nodes()}

    def find(node):
        if union_find[node] != node:
            union_find[node] = find(union_find[node])
        return union_find[node]

    def union(node1, node2):
        root1, root2 = find(node1), find(node2)
        union_find[root1] = root2

    for edge in edges:
        node1, node2, data = edge
        if find(node1) != find(node2):
            mst.add_edge(node1, node2, weight=data['weight'])
            union(node1, node2)

    return mst

# Bellman-Ford algorithm
def generate_random_weighted_digraph(num_nodes, prob_edge=0.3, min_weight=-10, max_weight=10):
    graph = nx.DiGraph()
    graph.add_nodes_from(range(num_nodes))
    
    for u in range(num_nodes):
        for v in range(num_nodes):
            if u != v and random.random() < prob_edge:
                weight = random.randint(min_weight, max_weight)
                graph.add_edge(u, v, weight=weight)
    
    return graph

def bellman_ford(graph, source):
    try:
        shortest_paths = nx.single_source_bellman_ford_path(graph, source)
        shortest_distances = nx.single_source_bellman_ford_path_length(graph, source)
        return shortest_paths, shortest_distances
    except nx.NetworkXUnbounded:
        return None, None

# Potentiel-Metra algorithm
def generer_taches(nb_taches):
    taches = []
    for i in range(nb_taches):
        duree = random.randint(1, 10)
        jour_debut = random.randint(1, 30)
        taches.append({
            'Tache': f'Tâche {i+1}',
            'Durée': duree,
            'Jour Début': jour_debut
        })
    return taches

def appliquer_methode_potentiel(taches):
    taches_sorted = sorted(taches, key=lambda x: x['Jour Début'])
    
    for tache in taches_sorted:
        tache['Jour Fin'] = tache['Jour Début'] + tache['Durée'] - 1
    
    for i, tache in enumerate(taches_sorted):
        if i == 0:
            tache['Marge Plus Tôt'] = 0
            tache['Marge Plus Tard'] = tache['Jour Fin']
        else:
            prev_tache = taches_sorted[i - 1]
            tache['Marge Plus Tôt'] = prev_tache['Jour Fin']
            tache['Marge Plus Tard'] = tache['Jour Fin'] + tache['Durée'] - 1

    return taches_sorted

# Ford-Fulkerson algorithm
def generate_flow_network(num_vertices, max_capacity=10):
    G = nx.DiGraph()
    for i in range(num_vertices):
        for j in range(num_vertices):
            if i != j:
                capacity = random.randint(1, max_capacity)
                G.add_edge(i, j, capacity=capacity)
    return G

def bfs(capacity, flow, source, sink):
    parent = [-1] * len(capacity)
    parent[source] = -2
    queue = deque([(source, float('inf'))])
    while queue:
        u, min_cap = queue.popleft()
        
        for v in range(len(capacity)):
            if parent[v] == -1 and capacity[u][v] - flow[u][v] > 0:
                parent[v] = u
                new_flow = min(min_cap, capacity[u][v] - flow[u][v])
                if v == sink:
                    return new_flow, parent
                queue.append((v, new_flow))
    return 0, parent

def ford_fulkerson(capacity, source, sink):
    n = len(capacity)
    flow = [[0] * n for _ in range(n)]
    max_flow = 0
    
    while True:
        path_flow, parent = bfs(capacity, flow, source, sink)
        if path_flow == 0:
            break
        max_flow += path_flow
        
        v = sink
        while v != source:
            u = parent[v]
            flow[u][v] += path_flow
            flow[v][u] -= path_flow
            v = u
    return max_flow, flow

def find_min_cut(capacity, flow, source):
    visited = [False] * len(capacity)
    queue = deque([source])
    visited[source] = True
    
    while queue:
        u = queue.popleft()
        for v in range(len(capacity)):
            if capacity[u][v] - flow[u][v] > 0 and not visited[v]:
                visited[v] = True
                queue.append(v)
    return visited

# Stepping Stone algorithm
def generate_data(nb_usines, nb_magasins, min_cost=1, max_cost=20, min_cap=10, max_cap=50):
    couts = np.random.randint(min_cost, max_cost, size=(nb_usines, nb_magasins))
    capacites = np.random.randint(min_cap, max_cap, size=nb_usines)
    demandes = np.random.randint(min_cap, max_cap, size=nb_magasins)

    total_capacite = sum(capacites)
    total_demande = sum(demandes)
    if total_capacite > total_demande:
        demandes[-1] += total_capacite - total_demande
    else:
        capacites[-1] += total_demande - total_capacite

    return couts, capacites, demandes

def calculer_cout_total(couts, allocation):
    return np.sum(couts * allocation)

def nord_ouest(capacites, demandes):
    allocation = np.zeros((len(capacites), len(demandes)), dtype=int)
    i, j = 0, 0
    while i < len(capacites) and j < len(demandes):
        alloc = min(capacites[i], demandes[j])
        allocation[i, j] = alloc
        capacites[i] -= alloc
        demandes[j] -= alloc
        if capacites[i] == 0:
            i += 1
        if demandes[j] == 0:
            j += 1
    return allocation

def moindre_cout(couts, capacites, demandes):
    allocation = np.zeros_like(couts, dtype=int)
    couts_temp = couts.astype(float)
    while np.any(capacites) and np.any(demandes):
        i, j = np.unravel_index(np.argmin(couts_temp, axis=None), couts_temp.shape)
        alloc = min(capacites[i], demandes[j])
        allocation[i, j] = alloc
        capacites[i] -= alloc
        demandes[j] -= alloc
        if capacites[i] == 0:
            couts_temp[i, :] = np.inf
        if demandes[j] == 0:
            couts_temp[:, j] = np.inf
    return allocation

def stepping_stone(couts, allocation):
    rows, cols = allocation.shape
    couts = couts.astype(float)
    while True:
        empty_cells = [(i, j) for i in range(rows) for j in range(cols) if allocation[i, j] == 0]
        best_improvement = 0
        best_allocation = allocation.copy()
        
        for cell in empty_cells:
            cycle, gain = find_cycle_and_gain(couts, allocation, cell)
            if cycle and gain < best_improvement:
                best_improvement = gain
                best_allocation = adjust_allocation(allocation, cycle)

        if best_improvement >= 0:
            break
        allocation = best_allocation

    return allocation

def find_cycle_and_gain(couts, allocation, start_cell):
    rows, cols = allocation.shape
    visited = set()
    cycle = []

    def dfs(cell, path):
        if cell in visited:
            if cell == start_cell and len(path) >= 4:
                return path
            return None

        visited.add(cell)
        row, col = cell

        for next_cell in [(row, c) for c in range(cols)] + [(r, col) for r in range(rows)]:
            if next_cell != cell and allocation[next_cell] > 0 or next_cell == start_cell:
                new_path = dfs(next_cell, path + [cell])
                if new_path:
                    return new_path

        visited.remove(cell)
        return None

    cycle = dfs(start_cell, [])

    if not cycle:
        return None, 0

    gain = calculate_cycle_gain(couts, allocation, cycle)
    return cycle, gain

def calculate_cycle_gain(couts, allocation, cycle):
    gain = 0
    for k, (i, j) in enumerate(cycle):
        sign = 1 if k % 2 == 0 else -1
        gain += sign * couts[i, j]
    return gain

def adjust_allocation(allocation, cycle):
    min_alloc = min(allocation[i, j] for k, (i, j) in enumerate(cycle) if k % 2 == 1)

    for k, (i, j) in enumerate(cycle):
        sign = 1 if k % 2 == 0 else -1
        allocation[i, j] += sign * min_alloc

    return allocation

def afficher_tableau(data, row_labels=None, col_labels=None, title=None):
    if row_labels is not None and col_labels is not None:
        table = tabulate(data, headers=col_labels, showindex=row_labels, tablefmt="fancy_grid")
    else:
        table = tabulate(data, tablefmt="fancy_grid")
    if title:
        print(f"\n{title}\n{'=' * len(title)}")
    print(table)

# Main interface functions
class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            relief=tk.FLAT,
            bg=EMSI_GREEN,
            fg="white",
            font=("Helvetica", 11),
            cursor="hand2",
            pady=8
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = DARK_GRAY

    def on_leave(self, e):
        self['background'] = EMSI_GREEN

def create_modern_window(title, geometry):
    window = tk.Toplevel()
    window.title(title)
    window.geometry(geometry)
    window.configure(bg=WINDOW_BG)
    return window

def execute_welsh_powell_algorithm():
    window = create_modern_window("Welsh-Powell", "400x300")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de sommets :", bg=WINDOW_BG).pack(pady=5)
    vertices_entry = tk.Entry(main_frame)
    vertices_entry.pack(pady=5)

    tk.Label(main_frame, text="Probabilité (0-1) :", bg=WINDOW_BG).pack(pady=5)
    probability_entry = tk.Entry(main_frame)
    probability_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            num_vertices = int(vertices_entry.get())
            probability = float(probability_entry.get())
            graph = generate_random_graph(num_vertices, probability)
            colors = welsh_powell(graph)
            chromatic_number = len(set(colors.values()))
            result_label.config(text=f"Nombre chromatique : {chromatic_number}")
            show_graph_in_new_window_3d(graph, "Welsh-Powell Graph")
        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_dijkstra_algorithm():
    window = create_modern_window("Dijkstra", "400x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de sommets :", bg=WINDOW_BG).pack(pady=5)
    vertices_entry = tk.Entry(main_frame)
    vertices_entry.pack(pady=5)

    tk.Label(main_frame, text="Probabilité (0-1) :", bg=WINDOW_BG).pack(pady=5)
    probability_entry = tk.Entry(main_frame)
    probability_entry.pack(pady=5)

    tk.Label(main_frame, text="Sommet de départ :", bg=WINDOW_BG).pack(pady=5)
    start_entry = tk.Entry(main_frame)
    start_entry.pack(pady=5)

    tk.Label(main_frame, text="Sommet d'arrivée :", bg=WINDOW_BG).pack(pady=5)
    end_entry = tk.Entry(main_frame)
    end_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            num_vertices = int(vertices_entry.get())
            probability = float(probability_entry.get())
            start = int(start_entry.get())
            end = int(end_entry.get())
            graph = generate_weighted_graph(num_vertices, probability)
            path = dijkstra(graph, start, end)
            result_label.config(text=f"Chemin le plus court : {' -> '.join(map(str, path))}")
            show_graph_in_new_window_3d(graph, "Graphe Dijkstra", path)
        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_kruskal_algorithm():
    window = create_modern_window("Kruskal", "400x300")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de sommets :", bg=WINDOW_BG).pack(pady=5)
    vertices_entry = tk.Entry(main_frame)
    vertices_entry.pack(pady=5)

    tk.Label(main_frame, text="Probabilité (0-1) :", bg=WINDOW_BG).pack(pady=5)
    probability_entry = tk.Entry(main_frame)
    probability_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            num_vertices = int(vertices_entry.get())
            probability = float(probability_entry.get())
            graph = generate_labeled_weighted_graph(num_vertices, probability)
            mst = kruskal(graph)
            total_weight = sum(mst[u][v]['weight'] for u, v in mst.edges())
            result_label.config(text=f"Poids total de l'arbre couvrant minimal : {total_weight}")
            show_graph_in_new_window_3d(graph, "Graphe Kruskal", mst_edges=mst.edges())
        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_bellman_ford_algorithm():
    window = create_modern_window("Bellman-Ford", "400x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de sommets :", bg=WINDOW_BG).pack(pady=5)
    vertices_entry = tk.Entry(main_frame)
    vertices_entry.pack(pady=5)

    tk.Label(main_frame, text="Probabilité d'arête (0-1) :", bg=WINDOW_BG).pack(pady=5)
    probability_entry = tk.Entry(main_frame)
    probability_entry.pack(pady=5)

    tk.Label(main_frame, text="Sommet source :", bg=WINDOW_BG).pack(pady=5)
    source_entry = tk.Entry(main_frame)
    source_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            num_vertices = int(vertices_entry.get())
            probability = float(probability_entry.get())
            source = int(source_entry.get())
            graph = generate_random_weighted_digraph(num_vertices, probability)
            shortest_paths, shortest_distances = bellman_ford(graph, source)
            
            if shortest_paths is None:
                result_label.config(text="Le graphe contient un cycle de poids négatif.")
            else:
                result_text = f"Résultats de Bellman-Ford depuis le sommet {source}:\n"
                for target, path in shortest_paths.items():
                    distance = shortest_distances[target]
                    result_text += f"Vers {target}: {' -> '.join(map(str, path))} (distance: {distance})\n"
                result_label.config(text=result_text)
                show_graph_in_new_window_3d(graph, "Graphe Bellman-Ford", bellman_ford_paths=shortest_paths)
        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_potentiel_metra_algorithm():
    window = create_modern_window("Potentiel-Metra", "400x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de tâches :", bg=WINDOW_BG).pack(pady=5)
    tasks_entry = tk.Entry(main_frame)
    tasks_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            nb_taches = int(tasks_entry.get())
            taches = generer_taches(nb_taches)
            taches_calculees = appliquer_methode_potentiel(taches)
            
            df = pd.DataFrame(taches_calculees)
            result_text = "Tableau des tâches avec dates de début, fin et marges :\n"
            result_text += df.to_string(index=False)
            result_label.config(text=result_text)

            # Create a Gantt chart
            fig, ax = plt.subplots(figsize=(10, 6))
            for i, task in enumerate(taches_calculees):
                ax.barh(i, task['Durée'], left=task['Jour Début'], height=0.5)
                ax.text(task['Jour Début'], i, task['Tache'], va='center', ha='right', fontweight='bold')
            
            ax.set_yticks(range(len(taches_calculees)))
            ax.set_yticklabels([task['Tache'] for task in taches_calculees])
            ax.set_xlabel('Jours')
            ax.set_title('Diagramme de Gantt des tâches')
            
            # Show the Gantt chart in a new window
            chart_window = tk.Toplevel()
            chart_window.title("Diagramme de Gantt")
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_ford_fulkerson_algorithm():
    window = create_modern_window("Ford-Fulkerson", "400x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre de sommets :", bg=WINDOW_BG).pack(pady=5)
    vertices_entry = tk.Entry(main_frame)
    vertices_entry.pack(pady=5)

    tk.Label(main_frame, text="Capacité maximale :", bg=WINDOW_BG).pack(pady=5)
    max_capacity_entry = tk.Entry(main_frame)
    max_capacity_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            num_vertices = int(vertices_entry.get())
            max_capacity = int(max_capacity_entry.get())
            graph = generate_flow_network(num_vertices, max_capacity)
            
            source = 0
            sink = num_vertices - 1
            
            capacity = [[0] * num_vertices for _ in range(num_vertices)]
            for u, v, data in graph.edges(data=True):
                capacity[u][v] = data['capacity']
            
            max_flow, flow = ford_fulkerson(capacity, source, sink)
            
            result_text = f"Flot maximal : {max_flow}\n\n"
            result_text += "Flots sur les arcs :\n"
            for u in range(num_vertices):
                for v in range(num_vertices):
                    if flow[u][v] > 0:
                        result_text += f"De {u} à {v}: {flow[u][v]}/{capacity[u][v]}\n"
            
            result_label.config(text=result_text)
            
            # Visualize the flow network
            pos = nx.spring_layout(graph)
            plt.figure(figsize=(10, 8))
            nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold')
            
            edge_labels = {(u, v): f"{flow[u][v]}/{data['capacity']}" for u, v, data in graph.edges(data=True)}
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)
            
            plt.title("Réseau de flot avec flots/capacités")
            
            # Show the flow network in a new window
            chart_window = tk.Toplevel()
            chart_window.title("Réseau de flot")
            canvas = FigureCanvasTkAgg(plt.gcf(), master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def execute_stepping_stone_algorithm():
    window = create_modern_window("Stepping Stone", "400x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Nombre d'usines :", bg=WINDOW_BG).pack(pady=5)
    nb_usines_entry = tk.Entry(main_frame)
    nb_usines_entry.pack(pady=5)

    tk.Label(main_frame, text="Nombre de magasins :", bg=WINDOW_BG).pack(pady=5)
    nb_magasins_entry = tk.Entry(main_frame)
    nb_magasins_entry.pack(pady=5)

    result_label = tk.Label(main_frame, text="", bg=WINDOW_BG)
    result_label.pack(pady=10)

    def run_algorithm():
        try:
            nb_usines = int(nb_usines_entry.get())
            nb_magasins = int(nb_magasins_entry.get())
            
            couts, capacites, demandes = generate_data(nb_usines, nb_magasins)
            
            # Nord-Ouest
            allocation_nord_ouest = nord_ouest(capacites.copy(), demandes.copy())
            cout_nord_ouest = calculer_cout_total(couts, allocation_nord_ouest)
            
            # Moindres Coûts
            allocation_moindre_cout = moindre_cout(couts, capacites.copy(), demandes.copy())
            cout_moindre_cout = calculer_cout_total(couts, allocation_moindre_cout)
            
            # Stepping Stone
            allocation_optimisee = stepping_stone(couts, allocation_moindre_cout)
            cout_optimise = calculer_cout_total(couts, allocation_optimisee)
            
            result_text = f"Coût total (Nord-Ouest): {cout_nord_ouest}\n"
            result_text += f"Coût total (Moindres Coûts): {cout_moindre_cout}\n"
            result_text += f"Coût total optimisé (Stepping Stone): {cout_optimise}\n\n"
            
            result_text += "Allocation optimisée:\n"
            result_text += tabulate(allocation_optimisee, 
                                    headers=[f"Magasin {j+1}" for j in range(nb_magasins)],
                                    showindex=[f"Usine {i+1}" for i in range(nb_usines)])
            
            result_label.config(text=result_text)
            
            # Visualize the optimized allocation
            fig, ax = plt.subplots(figsize=(10, 6))
            im = ax.imshow(allocation_optimisee, cmap='YlOrRd')
            
            ax.set_xticks(np.arange(nb_magasins))
            ax.set_yticks(np.arange(nb_usines))
            ax.set_xticklabels([f"M{j+1}" for j in range(nb_magasins)])
            ax.set_yticklabels([f"U{i+1}" for i in range(nb_usines)])
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            for i in range(nb_usines):
                for j in range(nb_magasins):
                    text = ax.text(j, i, allocation_optimisee[i, j], ha="center", va="center", color="black")
            
            ax.set_title("Allocation optimisée")
            fig.tight_layout()
            
            # Show the allocation visualization in a new window
            chart_window = tk.Toplevel()
            chart_window.title("Allocation optimisée")
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            result_label.config(text=f"Erreur : {str(e)}")

    ModernButton(main_frame, text="Exécuter", command=run_algorithm).pack(pady=15)

def show_second_interface():
    window = create_modern_window("Algorithmes de Graphes", "600x400")
    main_frame = tk.Frame(window, bg=WINDOW_BG, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    algorithms = [
        ("Welsh-Powell", execute_welsh_powell_algorithm),
        ("Dijkstra", execute_dijkstra_algorithm),
        ("Kruskal", execute_kruskal_algorithm),
        ("Bellman-Ford", execute_bellman_ford_algorithm),
        ("Potentiel-Metra", execute_potentiel_metra_algorithm),
        ("Ford-Fulkerson", execute_ford_fulkerson_algorithm),
        ("Stepping Stone", execute_stepping_stone_algorithm),
    ]

    for i, (text, command) in enumerate(algorithms):
        btn = ModernButton(main_frame, text=text, command=command, width=20)
        btn.grid(row=i // 3, column=i % 3, padx=10, pady=10)

# Main window setup
root = tk.Tk()
root.title("EMSI - Algorithmes de Graphes")
root.geometry("600x400")
root.configure(bg=WINDOW_BG)

# Main content frame
main_frame = tk.Frame(root, bg=WINDOW_BG, padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = tk.Label(
    main_frame,
    text="Algorithmes de Théorie des Graphes",
    font=("Helvetica", 18, "bold"),
    fg=EMSI_GREEN,
    bg=WINDOW_BG
)
title_label.pack(pady=20)

# Subtitle
subtitle_label = tk.Label(
    main_frame,
    text="École Marocaine des Sciences de l'Ingénieur",
    font=("Helvetica", 12),
    fg=DARK_GRAY,
    bg=WINDOW_BG
)
subtitle_label.pack(pady=10)

# Author and Supervisor
author_label = tk.Label(
    main_frame,
    text="Réalisé par : Marwa Rouiss et Sanaa Rhriyeb",
    font=("Helvetica", 10),
    fg=DARK_GRAY,
    bg=WINDOW_BG
)
author_label.pack(pady=5)

supervisor_label = tk.Label(
    main_frame,
    text="Encadré par : El Mkhalet Mouna",
    font=("Helvetica", 10),
    fg=DARK_GRAY,
    bg=WINDOW_BG
)
supervisor_label.pack(pady=5)

# Buttons
buttons_frame = tk.Frame(main_frame, bg=WINDOW_BG)
buttons_frame.pack(pady=20)

ModernButton(buttons_frame, text="Commencer", width=20, command=show_second_interface).grid(row=0, column=0, padx=10)
ModernButton(buttons_frame, text="Quitter", width=20, command=root.quit).grid(row=0, column=1, padx=10)

# Footer
footer_label = tk.Label(
    main_frame,
    text="© 2024 EMSI - Tous droits réservés",
    font=("Helvetica", 8),
    fg=DARK_GRAY,
    bg=WINDOW_BG
)
footer_label.pack(side=tk.BOTTOM, pady=20)

root.mainloop()

