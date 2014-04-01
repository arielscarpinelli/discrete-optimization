#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import array
from collections import namedtuple
from collections import deque
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

Point = namedtuple("Point", ['id', 'x', 'y'])
Segment = namedtuple("Segment", ['f', 't', 'id'])
Rect = namedtuple("Rect", ['x0', 'y0', 'x1', 'y1'])

class DistanceMatrix:
    
    def __init__(self, points):
        self._points = points
        #l = len(points)
        #self._distances = array.array('I', [65535] * range(l*(l+1)/2))

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
        return self._distance(i,j)    


    def obj(self, solution):
        return sum([self._distanceP(s[0],s[1]) for s in segmentize(self._points)])

def make_clusters(points):
    body = [[] for i in range(21)]
    left = []
    right = []    
    for point in points:
        if point.y > 15000 and point.y < 590000 and (point.x < 55000 or point.x > 620000):
            if point.x < 55000:
                left.append(point)
            else:
                right.append(point)
        else:
            body[int(point.y / 30000)].append(point)
    return (left, body, right)

def connection_cost(from_, to, cross, distances):
    savings = distances.get(from_[0], from_[1]) + distances.get(to[0], to[1])
    cost = distances.get(from_[1 if cross else 0], to[0]) + distances.get(from_[0 if cross else 1], to[1])
    return cost - savings

def shift_and_reverse(what, shift, reverse):
    d = deque(what)
    d.rotate(len(what) - shift - 1)
    if reverse:
        d.reverse()
    return d

def containing_rect(points):
    x0 = points[0].x
    y0 = points[0].y
    x1 = x0
    y1 = y0

    for p in points:
        if p.x < x0:
            x0 = p.x
        if p.y < y0:
            y0 = p.y
        if p.x > x1:
            x1 = p.x
        if p.y > y1:
            y1 = p.y

    dy = 1000
    dx = 60000

    return Rect(x0-dx, y0-dy, x1+dx, y1+dy)

def segmentize(points):
    l = len(points)
    s = [Segment(points[i], points[i+1], i) for i in range(l - 1)]
    s.append(Segment(points[-1], points[0], l))
    return s    

def in_rect(r, p):
    return r.x0 <= p.x and r.y0 <= p.y and p.x <= r.x1 and p.y <= r.y1

def choose_with_rect(r, segments, points):
    result = []
    while len(result) == 0:
        for s in segments:
            if in_rect(r, points[s[0]]) or in_rect(r, points[s[1]]):
                result.append(s)
        r = Rect(r.x0, r.y0 - 1000, r.x1, r.y1 + 1000)
    print len(result)
    return result

def insert_solution(solution, partial, distances):

    if len(solution) == 0:
        solution.extend(partial)        
        return

    points = distances._points

    rect = containing_rect([points[i] for i in partial])
    print rect

    segment_solution = segmentize(solution)
    filtered_solution = choose_with_rect(rect, segment_solution, points)

    segment_partial = segmentize(partial)

    best_solution = segment_solution[0].id
    best_partial = segment_partial[0].id
    best_cross = False
    best_cost = connection_cost(segment_solution[0], segment_partial[0], False, distances)

    for s in filtered_solution:
        for p in segment_partial:
            for cross in (False, True):
                cost = connection_cost(s, p, cross, distances)
                if cost < best_cost:
                    best_solution = s.id
                    best_partial = p.id
                    best_cross = cross
                    best_cost = cost


    solution[best_solution:best_solution] = shift_and_reverse(partial, best_partial, not best_cross) 


def solve_and_save(cluster, filename):
    l = len(cluster)
    print filename, l
    if l > 0:
        (objective, solution) = solve_routing(cluster, l)
        f = open(filename,'w')
        for i in solution:
            f.write(str(cluster[i].id) + "\n")
        f.close()

def clusterize_and_save(points):
    (left, body, right) = make_clusters(points) 

    solve_and_save(left, "clusters/left")
    solve_and_save(right, "clusters/right")

    _id = 0    
    for cluster in body:
        solve_and_save(cluster, "clusters/body_%d" % _id)
        _id += 1

def read_partial(name):
    print name
    return [int(line.strip()) for line in open(name)]

def solve_clustered(points, nodeCount):
    #clusterize_and_save(points)

    dm = DistanceMatrix(points)
    solution = []

    for i in range(21):
        partial = read_partial("clusters/body_%d" % i)
        insert_solution(solution, partial, dm)

    insert_solution(solution, read_partial("clusters/left"), dm)
    insert_solution(solution, read_partial("clusters/right"), dm)

    return (dm.obj(solution), solution)

def solve_routing(points, nodeCount):

    distanceMatrix = DistanceMatrix(points)

    routing = pywrapcp.RoutingModel(nodeCount, 1)
    routing.UpdateTimeLimit(180000)

    parameters = pywrapcp.RoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution = 'LocalCheapestArc'
    #parameters.solution_limit = 10
    parameters.guided_local_search = True
    #parameters.simulated_annealing = True

    cost = distanceMatrix.get

    routing.SetCost(cost)

    assignment = routing.SolveWithParameters(parameters, None)

    solution = []

    node = routing.Start(0)
    while not routing.IsEnd(node):
        solution.append(node)
        node = assignment.Value(routing.NextVar(node))

    return (assignment.ObjectiveValue(), solution)

def solve_mip(distanceMatrix, nodeCount):

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
                objective.SetCoefficient(x[i][j], distanceMatrix.get(i,j))
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

    print obj
         
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
        solution = solve_it(input_data)
        f = open("solution",'w')
        f.write(solution)
        f.close()
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)'

