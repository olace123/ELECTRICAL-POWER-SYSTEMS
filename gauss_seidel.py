import sep # take a look at the sep module first 
from math import pi, cos, sin
from cmath import phase

""" function to solve the nonlinear power flux equation system, it returns the voltages at each bus and the power 
generated or demanded at each bus
"""


def gauss_seidel(ybus, datos_de_barras):
    nodos = len(ybus)
    [pg, qg, pd, qd] = [datos_de_barras[0], datos_de_barras[1], datos_de_barras[2], datos_de_barras[3]]
    [tipo_de_nodo, mag, ang] = [datos_de_barras[5], datos_de_barras[6], datos_de_barras[7]]
    v = [1+0j]*nodos  # inicio plano de voltajes
    for i in range(nodos):
        v[i] = mag[i] * (cos(ang[i])+1j*sin(ang[i]))

    nodo_slack = tipo_de_nodo.index('slack')
    diferencial_voltajes = [1+1j]*nodos
    diferencial_voltajes[nodo_slack] = 0
    convergencia = False
    while not convergencia:
        convergencia = True
        for i in range(nodos):
            dif_aux = v[i]
            if tipo_de_nodo[i] != 'slack':  # continúa para todos los nodos excepto para el slack
                if tipo_de_nodo[i] == 'pq':  # el siguiente procedimiento es solo para nodos de carga
                    aux = 0
                    for j in range(nodos):
                        if j != i:
                            aux += ybus[i, j]*v[j]
                    v[i] = ((((pg[i]-pd[i])-(qg[i]-qd[i])*1j) / (v[i].real-v[i].imag*1j))-aux)/ybus[i, i]
                else:  # procedimiento para nodos PV
                    aux = 0
                    for j in range(nodos):
                        aux += ybus[i, j]*v[j]
                    qg[i] = -((v[i].real-v[i].imag*1j)*aux).imag  # no es qg[i], se ocupa para ahorrar recursos
                    aux = 0
                    mag_aux = v[i].__abs__()
                    for j in range(nodos):
                        if j != i:
                            aux += ybus[i, j] * v[j]
                    v[i] = ((((pg[i] - pd[i]) - (qg[i]) * 1j) / (v[i].real - v[i].imag * 1j)) - aux) / ybus[i, i]
                    v[i] = mag_aux*v[i]/v[i].__abs__()

            diferencial_voltajes[i] = v[i]-dif_aux
            if abs(diferencial_voltajes[i].real) < 0.00000001 and abs(diferencial_voltajes[i].imag) < 0.00000001:
                convergencia *= True
            else:
                convergencia *= False

    for i in range(nodos):  # cálculo de la qg en los nodos pv
        if tipo_de_nodo[i] == 'pv':
            aux = 0
            for j in range(nodos):
                aux += ybus[i, j] * v[j]
            qg[i] = -((v[i].real - v[i].imag * 1j) * aux).imag + qd[i]
    #  A continuación se calcula pg y qg en el nodo slack
    aux = 0
    for j in range(nodos):
        aux += ybus[nodo_slack, j] * v[j]
    pg[nodo_slack] = ((v[nodo_slack].real - v[nodo_slack].imag * 1j) * aux).real + pd[nodo_slack]
    qg[nodo_slack] = -((v[nodo_slack].real - v[nodo_slack].imag * 1j) * aux).imag + qd[nodo_slack]

    potencias = [pg, qg, pd, qd]

    return [v, potencias]


line_data = sep.read_line_data_file("line_data.txt")
bus_data = sep.read_bus_data_file("bus_data.txt")
ybus = sep.ybus_zbus(line_data, bus_data)[0]
[v, potencias] = gauss_seidel(ybus, bus_data)

for i in range(len(v)):
    print(v[i].__abs__(), phase(v[i])*(180/pi))

print("\n POTENCIAS ( EN P.U)")

for i in range(len(potencias)):
    print(potencias[i])
    
