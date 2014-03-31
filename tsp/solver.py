#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

Point = namedtuple("Point", ['id', 'x', 'y'])

class LengthMatrix:
    
    def __init__(self, points):
        self._points = points
        #l = len(points)
        #self._lengths = [-1 for i in range(l*(l+1)/2)]

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

    def obj(self, solution):
        val = self._length(solution[-1],solution[0])
        for index in range(0, nodeCount-1):
            val += self._length(solution[index],solution[index+1])
        return val

def solve_clustered(points, nodeCount):
    if nodeCount < 5000:
        return solve_routing(points, nodeCount)
    else:
        clusters = [[] for i in range(23)]
        for point in points:
            clusters[int(point.y / 30000)].append(point)

        solution = []

        for cluster in clusters:
            (objective, sol) = solve_routing(cluster, len(cluster))
            solution.extend(cluster[i] for i in sol)

    return (LengthMatrix(points).obj(solution), solution)

def solve_routing(points, nodeCount):

    lengthMatrix = LengthMatrix(points)

    routing = pywrapcp.RoutingModel(nodeCount, 1)

    parameters = pywrapcp.RoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution = 'LocalCheapestArc'
    parameters.time_limit = 180000
    parameters.solution_limit = 1
    #parameters.guided_local_search = True
    #parameters.simulated_annealing = True

    cost = lengthMatrix._length

    routing.SetCost(cost)

    assignment = routing.SolveWithParameters(parameters, None)

    solution = []

    node = routing.Start(0)
    while not routing.IsEnd(node):
        solution.append(node)
        node = assignment.Value(routing.NextVar(node))

    return (assignment.ObjectiveValue(), solution)

def solve_mip(lengthMatrix, nodeCount):

    solver = pywraplp.Solver('CP is fun!', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING);
# GLPK_MIXED_INTEGER_PROGRAMMING
# CBC_MIXED_INTEGER_PROGRAMMING
# SCIP_MIXED_INTEGER_PROGRAMMING

    print "creating variables"
    nodes = range(nodeCount)

    x = [[solver.BoolVar('x%d_%d' % (i,j)) for j in nodes] for i in nodes]

    print "enter/exit just once"
    for i in nodes:
        solver.Add ( x[i][i] == 0 )
        row = x[i]
        solver.Add ( solver.Sum(row) == 1 )
        column = [x[j][i] for j in nodes]
        solver.Add ( solver.Sum(column) == 1 ) 

    u = [solver.IntVar(0, nodeCount - 1, 'u%d' % i) for i in nodes]
    solver.Add (u[0] == 0)

    objective = solver.Objective()
    for i in nodes:
        for j in nodes:
            if (i != j):
                objective.SetCoefficient(x[i][j], lengthMatrix._length(i,j))
                solver.Add( u[i] - u[j] + nodeCount * x[i][j] <= (nodeCount - 1) )

    #
    # solution and search
    #

    print "starting search"

    solver.SetTimeLimit(1)
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL
    print "WallTime:", solver.WallTime()
    print [[x[i][j].SolutionValue() for j in nodes] for i in nodes]

    solution = []
    current = 0
    next = -1
    while(next != 0):
        solution.append(current)
        for i in nodes:
            if x[current][i].SolutionValue() > 0:
                next = i
                break
        current = next

    return (objective.Value(), solution)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    print "reading file"

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []

    print "converting"
    _id = 0
    for line in lines[1:-1]:
        parts = line.split()
        p = Point(_id, float(parts[0]), float(parts[1]))
        points.append(p)
        _id += 1

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    print "calling solver"
    (obj, solution) = solve_clustered(points, nodeCount)

    print solution
         
    # prepare the solution in the specified output format
    output_data = str(obj / 100) + ' ' + str(1) + '\n'
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

