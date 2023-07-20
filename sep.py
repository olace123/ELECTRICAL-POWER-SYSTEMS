import numpy as np
from math import pi


'''leer archivo_datos_lineas(archivo): El archivo a leer debe ser un archivo de texto y consistir en 4 columnas
NOTA: ¡ LA PRIMERA LÍNEA DEL ARCHIVO NO SE LEE POR SER LAS CABECERAS DE TABLA!
columna 1 y 2 : nodos enumerados 
columna 3: impedancia entre los nodos (impedancia de la línea)
columna 4: susceptancia en paralelo
 retorna una la lista [n, nodos1, nodos2, admitancias, susceptancias]
 nodos1 y nodos2 son listas con los números de nodos
 admitancias es una lista con las admitancias entre los nodos
 susceptancias es una lista que contiene las susceptancias en paralelo
 n es el número de nada'''


def leer_archivo_datos_lineas(archivo):  # el argumento debe ser el nombre del archivo
    nodos1 = []  # columna 1 de nodos
    nodos2 = []  # columna 2 de nodos
    admitancias = []  # admitancias entre nodos
    susceptancias = []

    with open(archivo, "r") as f:
        lineas = sum(1 for i in f)  # calculando número de líneas del archivo (que son también las líneas del sistema)
        f.seek(0)  # regresando el puntero al inicio del archivo
        f.readline()
        for i in range(lineas-1):
            aux = f.readline().split()
            nodos1.append(int(aux[0]))
            nodos2.append(int(aux[1]))
            admitancias.append(1 / complex(aux[2]))  # conversión de impedancias a admitancias
            susceptancias.append(complex(aux[3]))

    n = max(max(nodos1), max(nodos2))  # numero de nodos del sistema
    return [n, nodos1, nodos2, admitancias, susceptancias]


''' leer_archivo_datos_de_barras(archivo): el archivo debe ser un .txt, de 7 columnas
NOTA: ¡ LA PRIMERA LÍNEA DEL ARCHIVO NO SE LEE POR SE LAS CABECERAS DE TABLA!
columna 1: nodos enumerados
columna 2: potencia real generada (MW)
columna 3: Potencia reactiva generada (MVAR)
columna 4: potencia real demandada(MW)
columna 5 : potencia reactiva demandada(MVAR)
columna 6: impedancia del generador conectado a la barra en P.U (bases del sistema)
columna 7: impedancia equivalente de las cargas conectadas a la barra en P.U (bases del sistema)
retorna las potencias generadas y demandadas en P.U y las admitancias conectadas directamente a los nodos'''


def leer_archivo_datos_de_barras(archivo):  # retorna las potencias generadas y demandadas en por unidad
    pg = []
    qg = []
    pd = []
    qd = []
    y_nodos = []  # admitancias totales conectadas a la barra (sin tomar en cuenta la de las líneas)
    tipo_de_nodo = []
    mag = []
    ang = []
    mva_base = float(input("\n MVA base del sistema? "))
    with open(archivo, "r") as f:
        lineas = sum(1 for i in f)
        f.seek(0)
        f.readline()
        for i in range(lineas-1):
            aux = f.readline().split()
            tipo_de_nodo.append(aux[0])
            pg.append(float(aux[1])/mva_base)
            qg.append(float(aux[2])/mva_base)
            pd.append(float(aux[3])/mva_base)
            qd.append(float(aux[4])/mva_base)
            if complex(aux[5]) != 0:  # z generador
                y_nodos.append(1/complex(aux[5]))
            else:
                y_nodos.append(0)
            if complex(aux[6]) != 0j:
                y_nodos[i] += (1/complex(aux[6]))  # z equivalente de cargas en el nodo
            mag.append(float(aux[7]))
            ang.append(float(aux[8])*pi/180)

    return [pg, qg, pd, qd, y_nodos, tipo_de_nodo, mag, ang]


'''ybus_zbus() construye la matriz ybus de nXn (siendo n el número de nodos) haciendo uso de la función valores 
 para asignarle valor a cada posición de la matriz. Una vez construida la matriz ybus, la invierte para obtener zbus.
 En los lenguajes de programación los indices en los arreglos empiezan a contar desde el cero y en el SEP
 (sistema eléctrico de potencia) los nodos se enumeran a partir del 1, entonces a la función "valores" se le 
 envían los indices incrementados en 1, ya que esta hace uso de las listas que contienen los nodos enumerados '''
# Recibe como argumento n, nodos1, nodos2, admitancias.
# retorna la lista [ybus, zbus], donde ybus y zbus son arreglos np
# genera dos archivos de texto con los nombres YBUS Y ZBUS con los datos de los arreglos ybus y zbus respectivamente


def ybus_zbus(datos_de_lineas, datos_de_barras):  # función que construye la matriz YBUS
    n = datos_de_lineas[0]  # número de nodos del sistema
    nodos1 = datos_de_lineas[1]
    nodos2 = datos_de_lineas[2]
    admitancias = datos_de_lineas[3]
    susceptancias = datos_de_lineas[4]
    y_nodos = datos_de_barras[4]
    ybus = np.empty((n, n), complex)  # construye una matriz vacía de nXn

    for i in range(n):  # ciclos anidados que recorren la matriz fila por fila para asignarles valor
        for j in range(n):
            ybus[i, j] = valores(i+1, j+1, nodos1, nodos2, admitancias)

    respuesta = int(input("\nintroduzca\n1 : si YBUS se está construyendo para un\
     problema de flujos de potencia\n2: si YBUS se está construyendo para un análisis de corto circuito"))
    if respuesta == 2:
        for i in range(n):
            ybus[i, i] += y_nodos[i, i]

    respuesta = int(input("\nel sistema tiene susceptancias en paralelo ?\n 1 = si\n2 = no"))
    if respuesta == 1:
        for i in range(n):
            ybus[i, i] += valores(i+1, i+1, nodos1, nodos2, susceptancias)
    zbus = np.linalg.inv(ybus)

    with open("YBUS.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n):
            if primera_linea:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(ybus[i, j])}\t")
                primera_linea = True
        f.write("]")
    with open("ZBUS.txt", "w") as f:
        f.write("[")
        primera_linea = False
        for i in range(n):
            if primera_linea:
                f.write(";\n")
            for j in range(n):
                f.write(f"{str(zbus[i, j])}\t")
                primera_linea = True
        f.write("]")

    return [ybus, zbus]


def valores(a, b, nodos1, nodos2, admitancias):  # calcula los valores para la matriz YBUS
    valor = 0  # al crear una matriz vacía se asignan valores basura por eso se inicializa el valor en cero
    n = len(nodos1)
    if a == b:  # para los elementos en la diagonal
        for i in range(n):
            if nodos1[i] == a:
                valor += admitancias[i]
            elif nodos2[i] == a:
                valor += admitancias[i]
    else:  # elementos fuera de la diagonal (conexiones entre nodos)
        for i in range(n):
            if (nodos1[i] == a) and (nodos2[i] == b):
                valor += -admitancias[i]
                break
            elif (nodos1[i] == b) and (nodos2[i] == a):
                valor += -admitancias[i]
                break
    return valor


'''falla_entre_nodos(): retorna una lista con la información de la falla trifásica entre los nodos a y b,
la lista es: [float corriente de falla, arreglo np ybus_falla, arreglo np Zbus_falla, lista nodos1_falla, 
lista nodos2_falla, lista admitancias_falla].'''


def falla_entre_nodos(a, b, nodos1, nodos2, admitancias):  # al 50 porciento de la linea
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
    ybus_falla = y_bus(n+1, nodos1_falla, nodos2_falla, admitancias_falla)
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


''' remueve la linea ubicada entre los nodos a y b del sistema y modifica ybus y zbus para ese caso.
si no se desea modificar el ybus original entonces envíe una copia'''


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


# no toma en cuenta la factorización PA=LU (no es necesario si la matriz que recibe es Ybus)
def factor_lu(upper):  # retorna la factorización LU de la matriz (arreglo numpy) que recibe
    n = len(upper)
    lower = np.empty((n, n), complex)
    for i in range(n):  # ciclos anidados que llenan a "lower" como una matriz identidad
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
