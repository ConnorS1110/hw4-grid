import argparse
import csv
import json
import math
import os
from num import NUM
from sym import SYM
from data import DATA
from copy import deepcopy

help = """
grid.lua : a rep grid processor
(c)2022, Tim Menzies <timm@ieee.org>, BSD-2

USAGE: grid.lua  [OPTIONS] [-g ACTION]

OPTIONS:
  -d  --dump    on crash, dump stack   = false
  -f  --file    name of file           = ../etc/data/repgrid1.csv
  -g  --go      start-up action        = data
  -h  --help    show help              = false
  -p  --p       distance coefficient   = 2
  -s  --seed    random number seed     = 937162211

ACTIONS:
"""

args = None
Seed = 937162211
egs = {}
n = 0

def print_all_attributes(obj):
    """
    Function:
        print_all_attributes
    Description:
        Prints all attributes of an object
    Input:
        obj - Object whose class attributes will be printed
    Output:
        Formatted string of all class instance attributes and their values
    """
    stringToPrint = "{ "
    for attr, value in vars(obj).items():
        stringToPrint += str(attr) + ": " + str(value) + " "
    return stringToPrint + "}"

def dofile(filename):
    """
    Function:
        dofile
    Description:
        Opens .json file and returns data
    Input:
        filename - path to .json file to read
    Output:
        Data from .json file
    """
    with open(filename) as f:
        return json.load(f)

def transpose(t):
    """
    Function:
        transpose
    Description:
        Transposes matrix
    Input:
        t - Matrix to be transposed
    Output:
        u - Transposed matrix
    """
    u = []
    for i in range(len(t[0])):
        u.append([t[j][i] for j in range(len(t))])
    return u

def repCols(cols):
    """
    Function:
        repCols
    Description:
        Turns repgrid cols into DATA object
    Input:
        cols - Cols to be manipulated for DATA object conversion
    Output:
        DATA object of cols
    """
    copyCols = deepcopy(cols)
    for col in copyCols:
        col[-1] = str(col[0]) + ":" + str(col[-1])
        for j in range(1, len(col)):
            col[j - 1] = col[j]
        col.pop()
    copyCols.insert(0, ['Num' + str(k) for k in range(len(copyCols[0]))])
    copyCols[0][-1] = "thingX"
    return DATA(copyCols)

def repRows(t, rows, u=None):
    """
    Function:
        repRows
    Description:
        Turns repgrid rows into DATA object
    Input:
        t - Dictionary of repgrid data
        rows - Rows to be manipulated for DATA object conversion
    Output:
        DATA object of rows
    """
    rows = deepcopy(rows)
    for j, s in enumerate(rows[-1]):
        rows[0][j] = str(rows[0][j]) + ":" + str(s)
    rows.pop()
    for n, row in enumerate(rows):
        if n==0:
            row.append("thingX")
        else:
            u = t["rows"][len(t["rows"]) - n]
            row.append(u[-1])
    return DATA(rows)

def repPlace(data):
    """
    Function:
        repPlace
    Description:
        Turns a clustered repgrid object and turns it into a 2d grid
    Input:
        data - repgrid data
    Output:
        None
    """
    n,g = 20,[]
    for i in range(n+1):
        g.append([])
        for j in range(n+1):
            g[i].append(" ")
    maxy = 0
    print("")
    for r, row in enumerate(data.rows):
        c = chr(r+65)
        print(c, last(row.cells))
        x, y = int(row.x*n), int(row.y*n)
        maxy = max(maxy, y)
        g[y][x] = c
    print("")
    for y in range(maxy):
        print("{" + "".join(g[y]) + "}")

def repgrid(sFile):
    """
    Function:
        repgrid
    Description:
        Clusters rows and cols and outputs a 2d grid representation of this clustering
    Input:
        sFile - .json file to be used as data
    Output:
        None
    """
    t = dofile(sFile)
    rows = repRows(t, transpose(t["cols"]))
    cols = repCols(t["cols"])
    show(rows.cluster())
    show(cols.cluster())
    repPlace(rows)

def show(node, what= None, cols = None, nPlaces = None, lvl=None):
    """
    Function:
        show
    Description:
        Displays optimization of data as a tree
    Input:
        node - data
        what - stat to display
        cols - data columns
        nPlaces - # of decimal places to display stats
        lvl - how deep the tree is
    Output:
        None
    """
    if node:
        lvl = lvl or 0
        print("|.. " * lvl, end="")
        if ("left" not in node):
            print(last(last(node["data"].rows).cells))
        else:
            print(str(int(100 * node["C"])))
        show(node.get("left", None), what,cols, nPlaces, lvl+1)
        show(node.get("right", None), what,cols,nPlaces, lvl+1)

def last(t):
    """
    Function:
        last
    Description:
        Returns last element in a list
    Input:
        t - List to return last element from
    Output:
        Last element in t
    """
    return t[-1]

def rint(lo = None, hi = None):
    """
    Function:
        rint
    Description:
        Makes a random number
    Input:
        low - low value
        high - high value
    Output:
        Random number
    """
    return math.floor(0.5 + rand(lo, hi))

def eg(key, string, fun):
    """
    Function:
        eg
    Description:
        Creates an example test case and adds it to the dictionary of test cases. Appends the key/value to the actions of the help string
    Input:
        key - key of argument
        string - value of argument as a string
        fun - callback function to use for test case
    Output:
        None
    """
    global egs
    global help
    egs[key] = fun
    help += f"  -g {key}    {string}"

def oo():
    pass

def kap(listOfCols, fun):
    """
    Function:
        kap
    Description:
        Creates map that stores functions as value
    Input:
        listOfCols - list of columns
        fun - anonymous function to be used as value in map
    Output:
        u - map of anonymous functions
    """
    u = {}
    for k, v in enumerate(listOfCols):
        v, k = fun(v)
        u[k or len(u)+1] = v
    return u

def rand(low, high):
    """
    Function:
        rand
    Description:
        Creates a random number
    Input:
        low - low value
        high - high value
    Output:
        Random number
    """
    global Seed
    low, high = low or 0, high or 1
    Seed = (16807 * Seed) % 2147483647
    return low + (high - low) * Seed / 2147483647

def cosine(a, b, c):
    """
    Function:
        cosine
    Description:
        Finds x, y of line between a & b
    Input:
        a - First point
        b - Second point
        c - distance between a & b
    Output:
        x2 - x of line between a & b
        y - y of line between a & b
    """
    x1 = (a ** 2 + c ** 2 - b ** 2) / (2 * c)
    x2 = max(0, min(1, x1))
    y = (abs(a ** 2 - x2 ** 2)) ** 0.5
    return x2, y

def any(t):
    """
    Function:
        any
    Description:
        Selects a random row
    Input:
        t - DATA object
    Output:
        Random row from t
    """
    rintVal = rint(None, len(t) - 1)
    return t[rintVal]

def symFunc():
    """
    Function:
        symFunc
    Description:
        Callback function to test SYM class
    Input:
        None
    Output:
        'a' is the median value in the array and that the div to 3 decimal points equals 1.379 as a boolean
    """
    sym = SYM()
    for i in ["a","a","a","a","b","b","c"]:
        sym.add(i)
    return "a" == sym.mid() and 1.379 == round(sym.div(), ndigits=3)

def numFunc():
    """
    Function:
        numFunc
    Description:
        Callback function to test the NUM class
    Input:
        None
    Output:
        The mean equals 11/7 and the div equals 0.787 as a boolean
    """
    num = NUM()
    for element in [1,1,1,1,2,2,3]:
        num.add(element)
    return 11/7 == num.mid() and 0.787 == round(num.div(), ndigits=3)

def crashFunc():
    """
    Function:
        crashFunc
    Description:
        Callback function to test crashes
    Input:
        None
    Output:
        an instance of NUM doesn't have the property 'some.missing.nested.field'
    """
    num = NUM()
    return not hasattr(num, 'some.missing.nested.field')

def getCliArgs():
    """
    Function:
        getCliArgs
    Description:
        Parses out the arguments entered or returns an error if incorrect syntax is used
    Input:
        None
    Output:
        None
    """
    global args
    global Seed
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", "--dump", type=bool, default=False, required=False, help="on crash, dump stack")
    parser.add_argument("-g", "--go", type=str, default="all", required=False, help="start-up action")
    parser.add_argument("-h", "--help", action='store_true', help="show help")
    parser.add_argument("-s", "--seed", type=int, default=937162211, required=False, help="random number seed")
    parser.add_argument("-f", "--file", type=str, default="../etc/data/repgrid1.json", required=False, help="name of file")
    parser.add_argument("-p", "--p", type=int, default=2, required=False, help="distance coefficient")

    args = parser.parse_args()
    Seed = args.seed

def printCLIvalues():
    """
    Function:
        printCLIvalues
    Description:
        Prints the arguments
    Input:
        None
    Output:
        None
    """
    cli_args = {}
    cli_args["dump"] = args.dump
    cli_args["go"] = args.go
    cli_args["help"] = args.help
    cli_args["seed"] = args.seed
    cli_args["file"] = args.file
    print(cli_args)

def readCSV(sFilename, fun):
    """
    Function:
        readCSV
    Description:
        reads a CSV and runs a callback function on every line
    Input:
        sFilename - path of CSV file to be read
        fun - callback function to be called for each line in the CSV
    Output:
        None
    """
    with open(sFilename, mode='r') as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            fun(line)

def repColsFunc():
    """
    Function:
        repColsFunc
    Description:
        Callback function to test repCols function
    Input:
        None
    Output:
        the DATA object is created using .json repgrid cols data
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    rawData = dofile(full_path)
    t = repCols(rawData["cols"])
    for col in t.cols.all:
        print(vars(col))
    for row in t.rows:
        print(vars(row))

def synonymsFunc():
    """
    Function:
        synonymsFunc
    Description:
        Callback function to test clustering of repCols data
    Input:
        None
    Output:
        the synonyms of cols found through clustering
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    show(repCols(dofile(full_path)["cols"]).cluster())

def reprowsFunc():
    """
    Function:
        reprowsFunc
    Description:
        Callback function to test repRows function
    Input:
        None
    Output:
        the DATA object is created using .json repgrid rows data
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    t = dofile(full_path)
    rows = repRows(t, transpose(t["cols"]))
    for col in rows.cols.all:
        print(vars(col))
    for row in rows.rows:
        print(vars(row))

def copyFunc():
    """
    Function:
        copyFunc
    Description:
        Callback function to test deepcopy
    Input:
        None
    Output:
        the dictionary is successfully copied and manipulated
    """
    t1 = {'a': 1, 'b': {'c': 2, 'd': [3]}}
    t2 = deepcopy(t1)
    t2["b"]["d"][0] = 10000
    print("Before: " + str(t1) + "\nAfter: " + str(t2))

def prototypesFunc():
    """
    Function:
        prototypesFunc
    Description:
        Callback function to test clustering of rows data
    Input:
        None
    Output:
        the synonyms of rows found through clustering
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    t = dofile(full_path)
    rows = repRows(t, transpose(t["cols"]))
    show(rows.cluster())

def positionFunc():
    """
    Function:
        positionFunc
    Description:
        Callback function to test repPlace
    Input:
        None
    Output:
        the grid after clustering rows is displayed
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    t = dofile(full_path)
    rows = repRows(t, transpose(t["cols"]))
    rows.cluster()
    repPlace(rows)

def everyFunc():
    """
    Function:
        everyFunc
    Description:
        Callback function to test repgrid
    Input:
        None
    Output:
        the rows and cols are clustered and displayed, along with the 2d grid
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    repgrid(full_path)
