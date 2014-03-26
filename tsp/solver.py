#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from ortools.constraint_solver import pywrapcp

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def length_matrix(points, nodeCount):
    return [[length(points[i], points[j]) for i in range(nodeCount)] for j in range(nodeCount)]

def solve_routing(points, nodeCount):

    routing = pywrapcp.RoutingModel(nodeCount, 1)

    parameters = pywrapcp.RoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution = 'PathCheapestArc'
    # Disabling Large Neighborhood Search, comment out to activate it.
    parameters.no_lns = True
    parameters.routing_no_tsp = False
    parameters.routing_time_limit = 60000



    #lengths = length_matrix(points, nodeCount)

    cost = lambda i,j: length(points[i],points[j])#lengths[i][j]

    routing.SetCost(cost)

    assignment = routing.SolveWithParameters(parameters, None)

    solution = []

    node = routing.Start(0)
    while not routing.IsEnd(node):
        solution.append(node)
        node = assignment.Value(routing.NextVar(node))

    return (assignment.ObjectiveValue(), solution)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    (obj, solution) = solve_routing(points, nodeCount)

    # calculate the length of the tour
    #obj = lengths[solution[-1]][solution[0]]
    #for index in range(0, nodeCount-1):
    #    obj += lengths[solution[index]][solution[index+1]]

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(1) + '\n'
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
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)'

