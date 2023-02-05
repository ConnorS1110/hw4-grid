import argparse
import csv
import json
import math
import os
from num import NUM
from sym import SYM
from data import DATA
from math import floor
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
    stringToPrint = "{ "
    for attr, value in vars(obj).items():
        stringToPrint += str(attr) + ": " + str(value) + " "
    return stringToPrint + "}"

def dofile(filename):
    with open(filename) as f:
        return json.load(f)

def transpose(t):
    u = []
    for i in range(0, len(t[0])):
        u[i] = []
        for j in range(0, len(t)):
            u[i][j] = t[j][i]
    return u

def repCols(cols):
    copyCols = deepcopy(cols)
    for col in cols:
        col[-1] = str(col[0]) + ":" + str(col[-1])
        for j in range(1, len(col)):
            col[j - 1] = col[j]
        col.pop()
    cols.insert(0, ['Num' + str(k) for k in range(len(cols[0]))])
    cols[0][-1] = "thingX"
    return DATA(cols)

def show(node, what, cols, nPlaces, lvl=None):
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
        print("| " * lvl + str(len(node["data"].rows)) + " ", end="")
        if ("left" not in node) or lvl == 0:
            print(node["data"].stats("mid", node["data"].cols.y, nPlaces))
        else:
            print("")
        show(node.get("left", None), what,cols, nPlaces, lvl+1)
        show(node.get("right", None), what,cols,nPlaces, lvl+1)

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


def many(t, n):
    """
    Function:
        many
    Description:
        Creates a list of random rows
    Input:
        t - DATA object
        n - Number of row samples
    Output:
        u - list of random n rows from t
    """
    u = []
    for i in range(1, n + 1):
        u.append(any(t))
    return u

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

def randFunc():
    """
    Function:
        randFunc
    Description:
        Callback function to test the rand function
    Input:
        None
    Output:
        checks if m1 equals m2 and that they round to 0.5 as a boolean
    """
    global args
    global Seed
    num1, num2 = NUM(), NUM()
    Seed = args.seed
    for i in range(10**3):
        num1.add(rand(0, 1))
    Seed = args.seed
    for i in range(10**3):
        num2.add(rand(0, 1))
    m1, m2 = round(num1.mid(), 10), round(num2.mid(), 10)
    return m1 == m2 and 0.5 == round(m1, 1)

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
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", "--dump", type=bool, default=False, required=False, help="on crash, dump stack")
    parser.add_argument("-g", "--go", type=str, default="all", required=False, help="start-up action")
    parser.add_argument("-h", "--help", action='store_true', help="show help")
    parser.add_argument("-s", "--seed", type=int, default=937162211, required=False, help="random number seed")
    parser.add_argument("-f", "--file", type=str, default="../etc/data/repgrid1.json", required=False, help="name of file")
    parser.add_argument("-p", "--p", type=int, default=2, required=False, help="distance coefficient")

    args = parser.parse_args()

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

def csvFunc():
    """
    Function:
        csvFunc
    Description:
        Callback function to test readCSV() function
    Input:
        None
    Output:
        there are 8 * 399 elements in the default csv file in etc/data/auto93.csv
    """
    global n
    def fun(t):
        global n
        n += len(t)
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    readCSV(full_path, fun)
    return n == 8 * 399

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

def dataFunc():
    """
    Function:
        dataFunc
    Description:
        Callback function to test DATA class
    Input:
        None
    Output:
        DATA instance is created and has correct property values when reading the default CSV file at etc/data/auto93.csv
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    return (len(data.rows) == 398 and
    data.cols.y[1].w == -1 and
    data.cols.x[1].at == 1 and
    len(data.cols.x) == 4
    )

def statsFunc():
    """
    Function:
        statsFunc
    Description:
        Callback function to test stats function in DATA class
    Input:
        None
    Output:
        the statistics for the DATA instance using the default file at etc/data/auto93.csv are printed to the console
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    for k, cols in {'y': data.cols.y, 'x': data.cols.x}.items():
        print(k, "\tmid", (data.stats("mid", cols, 2)))
        print("", "\tdiv", (data.stats("div", cols, 2)))

def cloneFunc():
    """
    Function:
        cloneFunc
    Description:
        Callback function to test clone function in DATA class
    Input:
        None
    Output:
        the cloned DATA object contains the same metadata as the original object
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data1 = DATA(full_path)
    data2 = data1.clone(data1.rows)
    return (len(data1.rows) == len(data2.rows) and
            data1.cols.y[1].w == data2.cols.y[1].w and
            data1.cols.x[1].at == data2.cols.x[1].at and
            len(data1.cols.x) == len(data2.cols.x))

def clusterFunc():
    """
    Function:
        clusterFunc
    Description:
        Callback function to test cluster function in DATA class
    Input:
        None
    Output:
        the correct data is output from the cluster function
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    show(data.cluster(), "mid", data.cols.y, 1)

def swayFunc():
    """
    Function:
        swayFunc
    Description:
        Callback function to test sway function in DATA class
    Input:
        None
    Output:
        the correct data is output from the sway function
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    show(data.sway(), "mid", data.cols.y, 1)

def aroundFunc():
    """
    Function:
        aroundFunc
    Description:
        Callback function to test around function in DATA class
    Input:
        None
    Output:
        the rows are correctly sorted for the DATA object
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    for n, t in enumerate(data.around(data.rows[1])):
        if n % 50 == 0:
            print(n, round(t[1], 2), t[0].cells)

def halfFunc():
    """
    Function:
        halfFunc
    Description:
        Callback function to test half function in DATA class
    Input:
        None
    Output:
        the DATA object is correctly split in half
    """
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    data = DATA(full_path)
    left, right, A, B, mid, c = data.half()
    print(len(left), len(right), len(data.rows))
    print(A.cells, c)
    print(mid.cells)
    print(B.cells)

def repColsFunc():
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, args.file)
    rawData = dofile(full_path)
    t = repCols(rawData["cols"])
    for col in t.cols.all:
        print(vars(col))
    for row in t.rows:
        print(vars(row))
