#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import array
from collections import namedtuple
from collections import deque
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])
Segment = namedtuple("Segment", ['f', 't', 'id'])

class DistanceMatrix:
    
    def __init__(self, points):
        self._points = points
        l = len(points)
        self._distances = array.array('I', [65535] * (l*(l+1)/2))

    def _distance(self, i,j):
        return self._distanceP(self._points[i], self._points[j])
    
    def _distanceP(p0, p1):
        return math.sqrt((p0.x - p1.x)**2 + (p0.y - p1.y)**2) * 100

    def _distanceBuffered(self, i, j):
        if (j > i):
            i,j = j,i
        k = (i * (i + 1) / 2) + j        
        l = self._distances[k]
        if l == 65535:
            l = self._distance(i,j)
            self._distances[k] = l
        return l

    def get(self, i, j):
        return self._distanceBuffered(i,j)    


    def obj(self, solution):
        return sum([self._distanceP(s[0],s[1]) for s in segmentize(self._points)])

def segmentize(points):
    l = len(points)
    s = [Segment(points[i], points[i+1], i) for i in range(l - 1)]
    s.append(Segment(points[-1], points[0], l))
    return s    


def solve_routing(customers, customerCount, vehicleCount, vehicleCapacity):

    distanceMatrix = DistanceMatrix(customers)

    routing = pywrapcp.RoutingModel(customerCount, vehicleCount)
    routing.UpdateTimeLimit(5 * 60000)

    parameters = pywrapcp.RoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution = 'PathCheapestArc'
    #parameters.solution_limit = 10
    parameters.guided_local_search = True
    #parameters.simulated_annealing = True
    #parameters.tabu_search = True
    parameters.no_lns = True
    

    cost = distanceMatrix.get

    routing.SetDepot(0)
    routing.SetCost(cost)

    capacity = lambda i,j: customers[i].demand

    routing.AddDimension(capacity, 0, vehicleCapacity, True, "capacity")


    #search_log = routing.solver().SearchLog(10000000, routing.CostVar())
    #routing.AddSearchMonitor(search_log)

    assignment = routing.SolveWithParameters(parameters, None)

    vehicle_tours = []

    for vehicle in range(vehicleCount):

        solution = []

        node = routing.Start(vehicle)
        while not routing.IsEnd(node):
            solution.append(node)
            node = assignment.Value(routing.NextVar(node))

        vehicle_tours.append(solution)

    return (assignment.ObjectiveValue(), solution)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])
    
    customers = []
    for i in range(1, customer_count+1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i-1, int(parts[0]), float(parts[1]), float(parts[2])))

    #the depot is always the first customer in the input
    depot = customers[0] 


    # build a trivial solution
    # assign customers to vehicles starting by the largest customer demands
    
    (obj, vehicle_tours) = solve_routing(customers, customer_count, vehicle_count, vehicle_capacity)

    # prepare the solution in the specified output format
    outputData = str(obj) + ' ' + str(0) + '\n'
    for v in range(0, vehicle_count):
        outputData += ' '.join([str(customer_index) for customer_index in vehicle_tours[v]]) + '\n'

    return outputData


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print 'Solving:', file_location
        print solve_it(input_data)
    else:

        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)'

