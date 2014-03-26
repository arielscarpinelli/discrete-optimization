#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

Item = namedtuple("Item", ['index', 'value', 'weight', 'includes'])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []
    
    print "Capacity: "
    print capacity
    print "Items: "
    print item_count

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), list()))
    
    last_col = [0]*(capacity+1)

    for item in items:
      new_col = list(last_col)
      goes = False
      for current_capacity in range(item.weight, capacity+1):

        value_to_assign = last_col[current_capacity]
    	value_with_item = last_col[current_capacity - item.weight] + item.value
    	  
    	new_goes = False
    	if (value_with_item > value_to_assign):
    	  value_to_assign = value_with_item
    	  new_goes = True
    	    
    	if (new_goes != goes):
    	  goes = new_goes
    	  item.includes.append(current_capacity)

        new_col[current_capacity] = value_to_assign

      last_col = new_col
      print item.index


    total_value = last_col[capacity]
            
    taken = [0]*len(items)
    current_capacity = capacity
    acc_value = 0
    
    
    for item in reversed(items):
    
      goes = False
      for capacity_switch in item.includes:
        if capacity_switch <= current_capacity:
          goes = not goes
          
      if (goes):
        taken[item.index] = 1
        current_capacity -= item.weight
        acc_value += item.value
    
    
    assert acc_value == total_value

    # prepare the solution in the specified output format
    output_data = str(total_value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
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
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

