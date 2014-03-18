#!/usr/bin/python
# -*- coding: utf-8 -*-

from ortools.constraint_solver import pywrapcp

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
    
    
    solver = pywrapcp.Solver('CP is fun!');

    nodes = [solver.IntVar(0, node_count, "node[%i]" %i) for i in range(node_count)]

    for edge in edges:
        solver.Add ( nodes[edge[0]] != nodes[edge[1]] )


    #
    # solution and search
    #
    solution = solver.Assignment()
    solution.Add(nodes)
                           
    db = solver.Phase(nodes,
        solver.CHOOSE_FIRST_UNBOUND,
        solver.ASSIGN_MIN_VALUE)
                           
    solver.NewSearch(db)
    
    solver.NextSolution()
    
    solution = [node.Value() for node in nodes]
    
    color_count = max(solution)+1
                               
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

