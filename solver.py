#!/usr/bin/env pypy3

import sys
import resource
from time import perf_counter
from platform import system as platform_system
from npuzzle.visualizer import visualizer
from npuzzle.search import a_star_search, ida_star_search
from npuzzle.is_solvable import is_solvable
from npuzzle import colors
from npuzzle.colors import color
from npuzzle import parser
from npuzzle import heuristics
from npuzzle import solved_states

def color_yes_no(v):
    return color('green', 'YES') if v else color('red', 'NO')

def verbose_info(args, puzzle, solved, size):
    opts1 = {'greedy search:': args.g,
            'uniform cost search:': args.u,
            'visualizer:': args.v,
            'solvable:': is_solvable(puzzle, solved, size)
            }
    opt_color = 'cyan2'
    for k,v in opts1.items():
        print(color(opt_color, k), color_yes_no(v))

    opts2 = {'heuristic function:': args.f,
            'puzzle size:': str(size),
            'solution type:': args.s,
            'initial state:': str(puzzle),
            'final state:': str(solved)}
    for k,v in opts2.items():
        print(color(opt_color, k), v)
   
    print(color('blue2', 'heuristic scores for initial state'))
    for k,v in heuristics.KV.items():
        print(color('blue2', '  - ' + k + '\t:'), v(puzzle, solved, size))








    '''
    opt_values = [args.g, args.u, is_solvable(puzzle, solved, size), args.v]
    

    option_color = 'cyan'
    print(color
    greedy search: YES/NO
    uniform cost search: YES/NO
    solvable: YES/NO
    visualizer: YES/NO
    solution type
    initial state
    final state
    heuristic
    '''

if __name__ == '__main__':
    data = parser.get_input()
    if not data:
        sys.exit()        
    puzzle, size, args = data
    if args.c:
        colors.enabled = True

    solved = solved_states.KV[args.s](size)
    verbose_info(args, puzzle, solved, size)
    if not is_solvable(puzzle, solved, size):
        print(color('red','this puzzle is not solvable'))
        sys.exit(0)

    TRANSITION_COST = 1
    if args.g:
        TRANSITION_COST = 0

    HEURISTIC = heuristics.KV[args.f]
    if args.u:
        HEURISTIC = heuristics.uniform_cost

    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(color('red', 'max rss before search:'), maxrss)

    t_start = perf_counter()
    if args.ida:
        res = ida_star_search(puzzle, solved, size, HEURISTIC, TRANSITION_COST)
    else:
        res = a_star_search(puzzle, solved, size, HEURISTIC, TRANSITION_COST)
    t_delta = perf_counter() - t_start

    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(color('red', 'max rss after search: '), maxrss)

    print(color('yellow','search duration:') + ' %.4f second(s)' % (t_delta))
    success, steps, complexity = res
    fmt = '%d' + color('yellow',' evaluated nodes, ') + '%.8f' + color('yellow',' second(s) per node')
    print(fmt % (complexity['time'], t_delta / max(complexity['time'],1) ))
    if success:
        print(color('green','length of solution'), max(len(steps) - 1, 0))
        for s in steps:
            print(s)
    else:
        print(color('red','solution not found'))
    print(color('magenta','space complexity'), complexity['space'])
    print(color('magenta','time complexity'), complexity['time'])
    if success and args.v:
        visualizer(steps, size)


