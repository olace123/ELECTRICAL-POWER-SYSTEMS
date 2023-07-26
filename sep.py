import numpy as np
from math import pi


'''read_line_data_file(file): The file to be read must be a text file and consist of 4 columns.
NOTE: THE FIRST LINE OF THE FILE IS NOT READ BECAUSE IT IS THE TABLE HEADERS!
column 1 and 2 : numbered nodes 
column 3 : impedance between the nodes (line impedance)
column 4: parallel susceptance
 returns a list [n, nodes1, nodes2, admittances, susceptances].
 nodes1 and nodes2 are lists with the numbers of nodes
 admittances is a list containing the admittances between nodes
 susceptances is a list containing the parallel susceptances
 n is the number of nodes'''


def read_line_data_file(file):  # the argument is the file name
    nodes1 = []
    nodes2 = []
    admittances = []
    susceptances = []

    with open(file, "r") as f:
        lines = sum(1 for i in f)  # calculating number of lines of the file (which are also the system lines)
        f.seek(0)  # returning the pointer to the beginning of the file
        f.readline()
        for i in range(lines-1):
            aux = f.readline().split()
            nodes1.append(int(aux[0]))
            nodes2.append(int(aux[1]))
            admittances.append(1 / complex(aux[2]))  # impedance to admittance conversion
            susceptances.append(complex(aux[3]))

    n = max(max(nodes1), max(nodes2))  # number of nodes of the system
    return [n, nodes1, nodes2, admittances, susceptances]


'''' read_bus_data_file(file): the file must be a txt file, consisting of 7 columns.
NOTE: THE FIRST LINE OF THE FILE IS NOT READ BECAUSE IT IS THE TABLE HEADERS!
column 1: enumerated nodes
column 2: real power generated (MW)
column 3: generated reactive power (MVAR)
column 4: real power demanded (MW)
column 5: reactive power demanded (MVAR)
column 6: impedance of the generator connected to the bus in P.U (system bases)
column 7: equivalent impedance of the loads connected to the bus in P.U (system bases)
returns the power generated and demanded in P.U and the admittances directly connected to the nodes'''


def read_bus_data_file(file):  # returns the generated and demanded power in per unit
    pg = []
    qg = []
    pd = []
    qd = []
    y_nodes = []  # total admittances connected to the bus (without taking into account that of the lines)
    node_type = []
    mag = []
    ang = []
    mva_base = float(input("\n MVA system base? "))
    with open(file, "r") as f:
        lines = sum(1 for i in f)
        f.seek(0)
        f.readline()
        for i in range(lines - 1):
            aux = f.readline().split()
            node_type.append(aux[0])
            pg.append(float(aux[1])/mva_base)
            qg.append(float(aux[2])/mva_base)
            pd.append(float(aux[3])/mva_base)
            qd.append(float(aux[4])/mva_base)
            if complex(aux[5]) != 0:  # generador impedance
                y_nodes.append(1 / complex(aux[5]))
            else:
                y_nodes.append(0)
            if complex(aux[6]) != 0j:
                y_nodes[i] += (1 / complex(aux[6]))  # equivalent impedance of the load in the node
            mag.append(float(aux[7]))
            ang.append(float(aux[8])*pi/180)

    return [pg, qg, pd, qd, y_nodes, node_type, mag, ang]


'''ybus_zbus() constructs the ybus array of nXn (where n is the number of nodes) using the function values 
 to assign a value to each position in the matrix. Once the ybus matrix is constructed, it inverts it to obtain zbus.
 In programming languages the indices in the arrays start counting from zero and in the (SEP)
 (electrical power system) the nodes are enumerated starting from 1, then the function "values" is sent the indices incremented by 1, 
 since it makes use of the lists that contain the enumerated nodes '''
# returns the list [ybus, zbus], where ybus and zbus are np arrays.
# generates two text files named YBUS and ZBUS with the data of the ybus and zbus arrays respectively.


def ybus_zbus(line_data, bus_data):  # función que construye la matriz YBUS
    n = line_data[0]  # nombre of system nodes
    nodes1 = line_data[1]
    nodes2 = line_data[2]
    admittances = line_data[3]
    susceptancias = line_data[4]
    y_nodos = bus_data[4]
    ybus = np.empty((n, n), complex)  # empty array nXn

    for i in range(n):  # nested cycles that go through the matrix row by row to assign them value
        for j in range(n):
            ybus[i, j] = values(i + 1, j + 1, nodes1, nodes2, admittances)

    reply = int(input("\nenter\n1 : if YBUS is being built for\
     a power flux problem\n2: if YBUS is being built for a shor circuit analysis"))
    if reply == 2:
        for i in range(n):
            ybus[i, i] += y_nodos[i, i]

    reply = int(input("\ndo you want to take in account the parallel susceptances ?\n 1 = yes\n2 = no"))
    if reply == 1:
        for i in range(n):
            ybus[i, i] += values(i + 1, i + 1, nodes1, nodes2, susceptancias)
    zbus = np.linalg.inv(ybus)

    with open("YBUS.txt", "w") as f:
        f.write("[")
        first_line = False
        for i in range(n):
            if first_line:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(ybus[i, j])}\t")
                first_line = True
        f.write("]")
    with open("ZBUS.txt", "w") as f:
        f.write("[")
        first_line = False
        for i in range(n):
            if first_line:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(zbus[i, j])}\t")
                first_line = True
        f.write("]")

    return [ybus, zbus]


def values(a, b, nodos1, nodos2, admitancias):  # calculates the values for YBUS
    value = 0  # When creating an empty matrix, random values are assigned, so the value is initialized to zero.
    n = len(nodos1)
    if a == b:  # for diagonal elements
        for i in range(n):
            if nodos1[i] == a:
                value += admitancias[i]
            elif nodos2[i] == a:
                value += admitancias[i]
    else:  # off-diagonal elements (connections between nodes)
        for i in range(n):
            if (nodos1[i] == a) and (nodos2[i] == b):
                value += -admitancias[i]
                break
            elif (nodos1[i] == b) and (nodos2[i] == a):
                value += -admitancias[i]
                break
    return value


'''fault_between_nodes(): returns a list with the information of the three-phase fault between nodes a and b,
the list is: [fault current, ybus_fault, Zbus_fault, nodes1_fault, nodes2_fault, fault_admittances].'''


def fault_between_nodes(a, b, nodos1, nodos2, admitancias):  # at 50% of the line
    n = len(nodos1)
    nodos1_falla = nodos1[:]
    nodos2_falla = nodos2[:]
    admitancias_falla = admitancias[:]
    for i in range(n):
        if ((nodos1_falla[i] == a) and (nodos2_falla[i] == b)) or \
                ((nodos1_falla[i] == b) and (nodos2_falla[i] == a)):
            nodos1_falla.pop(i)
            nodos2_falla.pop(i)
            admitancias_falla.pop(i)
            nodos1_falla.extend([n+1, n+1])
            nodos2_falla.extend([a, b])
            admitancias_falla.extend([1/((1/admitancias[i])/2), 1/((1/admitancias[i])/2)])
            break
    ybus_falla = y_bus(n+1, nodos1_falla, nodos2_falla, admitancias_falla)  # need to be corrected
    zbus_falla = np.linalg.inv(ybus_falla)
    with open("YBUS_FALLA.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n+1):
            if primera_linea:
                f.write(";\n")
            for j in range(n+1):
                f.write(f"{str(ybus_falla[i, j])}\t")
                primera_linea = True
        f.write("]")
    with open("ZBUS_FALLA.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n+1):
            if primera_linea:
                f.write(";\n")
            for j in range(n+1):
                f.write(f"{str(zbus_falla[i, j])}\t")
                primera_linea = True
        f.write("]")
    return [1/zbus_falla[n, n], ybus_falla, zbus_falla, nodos1_falla, nodos2_falla, admitancias_falla]


'''' removes the line located between system nodes a and b and modify ybus and zbus for that case.
if you do not want to modify the original ybus then send a copy'''


def remover_linea_entre_nodos(a, b, ybus, nodos1, nodos2, admitancias):
    for i in range(len(nodos1)):
        if ((nodos1[i] == a) and (nodos2[i] == b)) or ((nodos1[i] == b) and (nodos2[i] == a)):
            ybus[a-1, b-1] = 0
            ybus[b - 1, a - 1] = 0
            ybus[a - 1, a - 1] -= admitancias[i]
            ybus[b - 1, b - 1] -= admitancias[i]
            break
    zbus = np.linalg.inv(ybus)
    return [ybus, zbus]


# does not take into account the factorization PA=LU (not necessary if the receiving matrix is Ybus).
def factor_lu(upper):  # returns the LU factorization of the matrix (numpy array) that receives
    n = len(upper)
    lower = np.empty((n, n), complex)
    for i in range(n):  # nested cycles filling "lower" as an identity matrix
        for j in range(n):
            if i == j:
                lower[i, j] = 1
            else:
                lower[i, j] = 0
    pivote = 0
    while pivote < n-1:  # ciclos de eliminación gaussiana (aquí se llenan las 2 matrices)
        for i in range(pivote+1, n):
            k = upper[i, pivote] / upper[pivote, pivote]
            lower[i, pivote] = k
            for j in range(n):
                upper[i, j] -= k * upper[pivote, j]
        pivote += 1

    with open("lower.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n):
            if primera_linea:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(lower[i, j])}\t")
                primera_linea = True
        f.write("]")

    with open("upper.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n):
            if primera_linea:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(upper[i, j])}\t")
                primera_linea = True
        f.write("]")

    return [lower, upper]
