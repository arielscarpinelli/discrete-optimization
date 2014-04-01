#!/usr/bin/python
# -*- coding: utf-8 -*-

from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp
import networkx as nx
import networkx.algorithms.approximation as apxa
import time


def remap(nodes):
    color_map = {}
    current_color = -1
    result = []
    
    for node_color in nodes:
    	if not node_color in color_map:
    		current_color = current_color + 1
    		color_map[node_color] = current_color
    	result.append(color_map[node_color])
    
    return result


def cp_solve(edges, node_count, cliques, presets, max_allowed_colors, timeout):
    solver = pywraplp.Solver('CP is fun!', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING);
# GLPK_MIXED_INTEGER_PROGRAMMING
# CBC_MIXED_INTEGER_PROGRAMMING
# SCIP_MIXED_INTEGER_PROGRAMMING

    print "solving with " + str(max_allowed_colors) + " colors"

    colors = range(max_allowed_colors)
    nodes = range(node_count)
    nodes_colors = [[solver.BoolVar('n%s_c%s' % (node,color)) for color in colors] for node in nodes]
    obj = solver.IntVar(1, max_allowed_colors)

    for node in nodes:
        node_colors = nodes_colors[node]
        solver.Add ( solver.Sum(node_colors) == 1 ) # one color per node
        for color in colors:
            solver.Add( obj >= color*node_colors[color] )
    
    for edge in edges:
        print edge
        left = nodes_colors[edge[0]]
        right = nodes_colors[edge[1]]
        for color in colors:
            solver.Add ( left[color] + right[color] <= 1  ) # Different colors

    for (node, value) in presets:
        for color in colors:
            solver.Add(nodes_colors[node][color] == (color == value))

    #for clique in cliques:
	#    solver.Add(solver.AllDifferent([nodes_values[node] for node in clique]))
	    

    objective = solver.Minimize(obj)

    #
    # solution and search
    #

    print "starting search"

    solver.SetTimeLimit(timeout)
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL
    solution = [sum([color if nodes_colors[node][color].SolutionValue() > 0 else 0 for color in colors]) for node in nodes]

    #solution = solver.Assignment()
    #solution.Add(variables)
                           
    #db = solver.Phase(variables,
        #solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
    #    solver.CHOOSE_FIRST_UNBOUND,
    #    solver.ASSIGN_MAX_VALUE)
    
    
    #solver.NewSearch(db, [solver.TimeLimit(timeout)])
    
    #solver.NextSolution()
    
    #solution = [sum([color for color in colors if node_colors[color].Value()]) for node_colors in nodes_colors]
    
    #solver.EndSearch()
    
    #print "failures:", solver.Failures()
    #print "branches:", solver.Branches()
    print "WallTime:", solver.WallTime()
                           
    return remap(solution)

def get_graph(node_count, edges):
    G = nx.Graph()
    nodes = range(node_count)
    G.add_nodes_from(nodes);
    G.add_edges_from(edges);
    return G


def preset(node, neighbors, presets):
    if not node in presets:
        values = sorted([presets[n] for n in neighbors if n in presets])
        value = 0
        if len(values) > 0:
            values = values + [max(values)+2] # last item is the forced max value +2
            for i in range(len(values)): # find an "emtpy slot"
                if values[i+1] - values[i] > 1:
                    value = values[i] + 1
                    break
        presets[node] = value

def sorted_by_degree(G):
    degrees = [(node, nx.degree(G, node)) for node in G]    
    degrees = sorted(degrees, key=lambda t: -t[1])
    return degrees

def preset_most_connected(G, limit):
    degrees = sorted_by_degree(G)
    most_connected = degrees[:limit]
    
    presets = {}

    for (node, degree) in most_connected:
        neighbors = [n for n in G[node]]
        preset(node, neighbors, presets)
    
    return [(node, presets[node]) for node in presets]

def cliques_for_nodes(G, nodes):
    return [apxa.max_clique(G)]

def super_greedy(G):
    degrees = sorted_by_degree(G)

    tabu = set()

    nodes = len(degrees)

    solution = [-1] * nodes
    solved = 0

    current_color = 0

    while(solved < nodes):
        print "color: ", current_color, "solved: ", solved
        for (node, degree) in degrees:
            if solution[node] == -1 and not node in tabu:
                solution[node] = current_color
                tabu |= set(G[node])
                solved+=1
        tabu = set()        
        current_color+=1

    return solution
    

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
        
    G = get_graph(node_count, edges)
    
    #solution = super_greedy(G)

    presets = preset_most_connected(G, 12)
    print presets

    cliques = cliques_for_nodes(G, [preset[0] for preset in presets])
    print cliques

    solution = [node_count]
    
    for lap in range(5):
        solution = cp_solve(edges, node_count, cliques, presets, max(solution), 20 * 1000)
        print solution

    color_count = max(solution) + 1
    
    # prepare the solution in the specified output format
    output_data = str(color_count) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print solve_it(input_data)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'

