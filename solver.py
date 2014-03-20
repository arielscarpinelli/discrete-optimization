#!/usr/bin/python
# -*- coding: utf-8 -*-

from ortools.constraint_solver import pywrapcp
import networkx as nx
import networkx.algorithms.approximation as apxa
import time


def cp_solve(edges, node_count, max_clique, max_allowed_colors, timeout):
    solver = pywrapcp.Solver('CP is fun!');

    print "solving with " + str(max_allowed_colors) + " colors"

    nodes = [solver.IntVar(0, max_allowed_colors-1, "node[%i]" %i) for i in range(node_count)]

    for edge in edges:
        solver.Add ( nodes[edge[0]] != nodes[edge[1]] )

    solver.Add(nodes[0] == 0)
    solver.Add(nodes[1] <= 1)

    for i in range(2, node_count):
        solver.Add(nodes[i] <= solver.Max(nodes[:i]) + 1)
        
	solver.Add(solver.AllDifferent([nodes[node] for node in max_clique]))

    #
    # solution and search
    #
    solution = solver.Assignment()
    solution.Add(nodes)
                           
    db = solver.Phase(nodes,
        solver.CHOOSE_MIN_SIZE_LOWEST_MAX,
        #solver.CHOOSE_FIRST_UNBOUND,
        solver.ASSIGN_MIN_VALUE)
                           
    solver.NewSearch(db, [solver.TimeLimit(timeout)])
    
    solver.NextSolution()
    
    solution = [node.Value() for node in nodes]
    
    solver.EndSearch()
    
    print "failures:", solver.Failures()
    print "branches:", solver.Branches()
    print "WallTime:", solver.WallTime()


                           
    return solution

def get_graph(node_count, edges):
    G = nx.Graph()
    nodes = range(node_count)
    G.add_nodes_from(nodes);
    G.add_edges_from(edges);
    return G

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
    
    degrees = [(node, nx.degree(G, node)) for node in G]
    
    print degrees
    
    solution = [node_count]
    
    for lap in range(4):
        solution = cp_solve(edges, node_count, sorted(apxa.max_clique(G)), max(solution), 20 * 1000)

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

