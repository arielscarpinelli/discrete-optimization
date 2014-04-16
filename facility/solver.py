#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    M = 10000000

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    solver = pywraplp.Solver('CP is fun!', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING);
# GLPK_MIXED_INTEGER_PROGRAMMING
# CBC_MIXED_INTEGER_PROGRAMMING
# SCIP_MIXED_INTEGER_PROGRAMMING

    print "creating variables"

    f = [solver.BoolVar('f%d' % facility.index) for facility in facilities]

    x = [[solver.IntVar(0, customer.demand, 'x%d_%d' % (customer.index,facility.index)) for customer in customers] for facility in facilities]
    k = [[solver.BoolVar('k%d_%d' % (customer.index,facility.index)) for customer in customers] for facility in facilities]

    objective = solver.Objective()
    for i in range(facility_count):
        facility = facilities[i]
        solver.Add ( solver.Sum(x[i]) <= M*f[i]  )
        solver.Add ( solver.Sum(x[i]) <= facility.capacity)
        objective.SetCoefficient(f[i], facility.setup_cost )
    
    for i in range(customer_count):
        column = [x[j][i] for j in range(facility_count)]
        solver.Add ( solver.Sum(column) == customers[i].demand )
        for j in range(facility_count):
            solver.Add ( M*k[j][i] >= x[j][i] )
            objective.SetCoefficient(k[j][i], length(facilities[j].location, customers[i].location))

    #
    # solution and search
    #

    print "starting search"

    solver.SetTimeLimit(60000)
    result_status = solver.Solve()
    print result_status
    assert result_status == pywraplp.Solver.OPTIMAL
    print "WallTime:", solver.WallTime()


    solution = [-1]*len(customers)

    for i in range(facility_count):
        for j in range(customer_count):
            if x[i][j].SolutionValue() > 0:
                solution[j] = i

    # calculate the cost of the solution
    #obj = sum([f.setup_cost*used[f.index] for f in facilities])
    #for customer in customers:
    #    obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = str(objective.Value()) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print 'Solving:', file_location
        solution = solve_it(input_data)
        f = open("solution",'w')
        f.write(solution)
        f.close()
        print solution
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)'

