#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from ortools.constraint_solver import pywrapcp

Point = namedtuple("Point", ['x', 'y'])

class LengthMatrix:
    
    def __init__(self, points):
        self._points = points
        l = len(points)
        self._lengths = [-1 for i in range(l*(l+1)/2)]

    def _length(self, i,j):
        return math.sqrt((self._points[i].x - self._points[j].x)**2 + (self._points[i].y - self._points[j].y)**2) * 100

    def get(self, i, j):
        if (j > i):
            i,j = j,i
        k = (i * (i + 1) / 2) + j        
        l = self._lengths[k]
        if l < 0:
            l = self._length(i,j)
            self._lengths[k] = l
        return l


def length_matrix(points, nodeCount):
    return [[length(points[i], points[j]) for i in range(nodeCount)] for j in range(nodeCount)]

def solve_routing(lengthMatrix, nodeCount):

    routing = pywrapcp.RoutingModel(nodeCount, 1)

    parameters = pywrapcp.RoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution = 'LocalCheapestArc'
    parameters.time_limit = 1
    #parameters.guided_local_search = True

    cost = lambda i,j: lengthMatrix.get(i,j)

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
    lm = LengthMatrix(points)
    (obj, solution) = solve_routing(lm, nodeCount)

    obj2 = lm._length(solution[-1],solution[0])
    for index in range(0, nodeCount-1):
        obj2 += lm._length(solution[index],solution[index+1])
        
    print obj2/100

    # prepare the solution in the specified output format
    output_data = str(obj/100) + ' ' + str(1) + '\n'
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

