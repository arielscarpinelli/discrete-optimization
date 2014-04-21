#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location', 'usage_variable', 'usage_constraint', 'capacity_constraint'])
Customer = namedtuple("Customer", ['index', 'demand', 'location', 'facility_variables'])

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
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])), None, None, None ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2])), []))

    solver = pywraplp.Solver('CP is fun!', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING);
# GLPK_MIXED_INTEGER_PROGRAMMING
# CBC_MIXED_INTEGER_PROGRAMMING
# SCIP_MIXED_INTEGER_PROGRAMMING

    print "creating variables"

    objective = solver.Objective()
    
    f = []

    total_demand = sum([customer.demand for customer in customers])
    demand_constraint = solver.Constraint(total_demand, solver.Infinity())
    total_capacity = 0
	
    for facility in facilities:

    	capacity_constraint = solver.Constraint(0, facility.capacity)
    	total_capacity = total_capacity + facility.capacity

    	usage_variable = solver.BoolVar('f%d' % facility.index)
        objective.SetCoefficient(usage_variable, facility.setup_cost )
        demand_constraint.SetCoefficient(usage_variable, facility.capacity )

    	usage_constraint = solver.Constraint(-solver.Infinity(), 0)
    	usage_constraint.SetCoefficient(usage_variable, -M)
    	
    	f.append(Facility(facility.index, facility.setup_cost, facility.capacity, facility.location, usage_variable, usage_constraint, capacity_constraint))
    	
    facilities = f

    print "demand  ", total_demand
    print "capacity", total_capacity


    variables = facility_count

    for customer in customers:
		facilities_distances = [(facility, length(customer.location, facility.location)) for facility in facilities]
		
		# aca cortar solo las mas cercanas
		facilities_distances = sorted(facilities_distances, key=lambda tup: tup[1])
		
		max_cost = (facilities_distances[0][0].setup_cost + facilities_distances[0][1]) / 2
		
		customer_single_facility_constraint = solver.Constraint(1, 1)
		for facility_distance in facilities_distances:
			if facility_distance[1] <= max_cost:
				facility = facility_distance[0]
				variables = variables + 1
				x = solver.BoolVar('x_%d_%d' % (facility.index, customer.index))
				customer_single_facility_constraint.SetCoefficient(x, 1)
				facility.usage_constraint.SetCoefficient(x, 1)
				facility.capacity_constraint.SetCoefficient(x, customer.demand)
				objective.SetCoefficient(x, facility_distance[1])
				customer.facility_variables.append((facility, x))

    #
    # solution and search
    #

    print "variables", variables
    print "starting search"

    solver.SetTimeLimit(1 * 60 * 60 * 1000 - 5000)
    result_status = solver.Solve()
    print "WallTime:", solver.WallTime()
    print "Status:",result_status
    assert (result_status == pywraplp.Solver.OPTIMAL) or (result_status == pywraplp.Solver.FEASIBLE)


    solution = [-1]*len(customers)
    
    for customer in customers:
    	for x in customer.facility_variables:
            if x[1].SolutionValue() > 0:
                solution[customer.index] = x[0].index
    		

    # calculate the cost of the solution
    #obj = sum([f.setup_cost*used[f.index] for f in facilities])
    #for customer in customers:
    #    obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = str(objective.Value()) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, solution))

    f = open("solution",'w')
    f.write(output_data)
    f.close()

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
        print solution
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)'

