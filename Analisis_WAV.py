import numpy						# importa libreria de matematicas
import scipy.io.wavfile				# importa libreria de lectura de archivos.wav
import matplotlib.pyplot   			# importa libreria de graficacion matematica
from tkinter import * 				# importa dependencia de matplotlib.pyplot (funcion desconocida)
from matplotlib import pyplot as plt


####################Seccion no implementada aun################
def print_graph(X,Y,C="b",EjeX="",EjeY="",Titulo="",subplot="111"):
	Figura = matplotlib.pyplot.figure() 	# crean la figura que contendra la grafica
	Grafica = Figura.add_subplot(subplot)   # crea la grafica
	Grafica.set_xlabel(EjeX)				# etiquetan los ejes
	Grafica.set_ylabel(EjeY)
	Grafica.set_title(Titulo)
	Trazo = Grafica.plot(X,Y,C)				# genera la grafica
	Figura.show()							# muestra la grafica


# Leera el archivo .wav obteniendo dos valores de salida (rate,data): 
# rate: El valor de muestras por segundo (frecuencia de muestreo).
# data: Una matriz de n fila y dos columnas con los valores de audio (oido izquierdo y oido derecho).

Archivo    = input("Archivo(/home/martin/Escritorio/Proyecto .wav): ")  
								#Se le solicita al usiario ingresar el nombre del archivo .wav

rate, data = scipy.io.wavfile.read("/home/martin/Escritorio/Proyecto/"+Archivo+".wav") 
								#Se optienen los valores de salida mencionados anteriormente



# ------------------------------------------------------------------------------------------ ----------------------------
# inicializa matriz que contendra los valores procesados de los datos del .WAV (Data_t = []_x1M)

#Vectores (matriz de una fila)

Data_cp = [0]*len(data)		# Copia de datos de entrada (data)
Data_t = []		     	    # Guarda los tiempos de duracion de los bits en segundos (1 o 0) sin escalar
Data_t_x1M  = [0]*len(data)	# Se le da a la matriz la misma extension que data (inicialmente llena de ceros) con el fin de graficar

inicio   = 0	# Inicio del bit (1 o 0)
t_bit    = 0    # Tiempo en el bit (individual)
Mag_max  = 3000 # Por encima de este valor se considera ruido
t_bit_min = 0.000250 #Por debajo de este tiempo de estado se considera ruido
t_entre_letra = 0.03 #tiempo(en segundos) minimo entre dos letras,Tiempo que debe transcurrir luego de un estado para que se considere que el siguiente pertenese a una nueva letra
t_letra  = 0    # tiempo transcurrido en cero (en busca de tiempos entre letras)
Archivo_letra_a = open("Archivo_letra_a","w+") #Se abre/crea un archivo que contendra los datos procesados para luego usarlos en la neural network


data_test = [0]*len(data)
# ----------------------------------------------------------------------------------------------------------------------
# Seccion de procesamiento de datos (deteccion de duracion de bits)
 
for i in range(len(data)):	# For en en que se leen todos los tiempos de data

	Data_cp[i] = data[i][0] # Se copian solo los datos del sonido izquierdo, ya que los del derecho son igual. 
							# Esto se hace para trabajar con Data_cp y no modificar data 

	if  data[i][0] < 0:     # Cambia a cero todos los valores negativos
		Data_cp[i] = 0		# Se eliminan los negativos, para facilitar el procesamiento

	if  data[i][0] > Mag_max:     # Cambia a cero todos los valores mayores a 2500 (para eliminar ruido)
		Data_cp[i] = 0		

	if (Data_cp[i] > 0)and(Data_cp[i-1] == 0):	# Detecta los cambios de cero a un valor positivo
		inicio = i 								# Tiempo (discreto) en que inicia el bit (inicio de la medicion)

	if (Data_cp[i] == 0)and(Data_cp[i-1] > 0):	# Detecta los cambios de un valor positivo a cero 
		t_bit = (i-1)/rate - inicio/rate        # Se pasa de tiempo "discreto" a continuo (se divide entre rate)
											    # Se resta el inicio de la medida con el final de la misma
		for r in range(inicio,i):
			if t_bit > t_bit_min:               # filtra los tiempos pequeños(ruido)
				Data_t_x1M[r] = -1000000*t_bit  # Se guardan los valores de los tiempos escalados, para ser posteriormente graficados

		if t_bit > t_bit_min:				    # filtra los tiempos pequeños(ruido)
			Data_t.append(t_bit)                # Se añade los tiempos de duracion de cada estado sin escalar a Data_t

	# if Data_t_x1M[i] == 0: #si el dato es cero se aumenta el tiempo en cero
	# 	t_letra += 1
	#  	if (t_letra/rate == t_entre_letra): #si ya ha transcurrio el tiempo entre letras
	#  		Archivo_letra_a.write(str(Data_t) +'\n') #se inicia una nueva letra en el archivo
	#  		t_letra  = 0 #se reinician los valores para las siguientes letras
	#  		Data_t = []
	#  		data_test[i] = -100
	# else:
	#  	t_letra  = 0

Archivo_letra_a.close()

#Grafica de magnitud de los datos (tanto el .wav como los tiempos de duracion de cada bit)

Figura = matplotlib.pyplot.figure() 	# Crean la figura que contendra la grafica
Grafica_data = Figura.add_subplot(111)  # Crea la grafica
x_points = list(range(len(data)))		# Crea una indexacion para los datos (recordar que cada data[i] esta relacionado con un i, no con el tiempo)

for i in x_points:						# convierte la indexacion a segundos
	x_points[i] /= rate					# Esto se lee x_points[i] = x_points[i]/rate


# *********************************************************************************************************************
# Esta seccion comentada pregunta por si se desea graficar los puntos de muestro (meramente de simulacion)

#select_trazo = input("Mostrar puntos: S/N: ") #seleccion para mostrar puntos
#if select_trazo == "S" or select_trazo =="s":
 #	Trazo = Grafica_data.plot(x_points, Data_t = []_x1M, linestyle='-', marker='.',color='b',)	# genera la grafica
#else:
# *********************************************************************************************************************

Trazo  =  Grafica_data.plot(x_points, Data_t_x1M,  'g')	# Genera la grafica (Grafica los datos obtenidos del .wav)
Trazo2 =  Grafica_data.plot(x_points, Data_cp, 'b')	# Genera la grafica (Coloca los valores medidos graficamente)
Trazo3 =  Grafica_data.plot(x_points, data_test, 'r')
Grafica_data.set_xlabel('Tiempo(s)')				# Etiquetan los ejes
Grafica_data.set_ylabel('Magnitud')
Grafica_data.set_title('Magnitud')
Figura.show()										# Muestra la grafica


# **************************************************************************************************************************
#					             	FIN DE EJECUCION
# **************************************************************************************************************************
nada=input("Salir: ")
matplotlib.pyplot.close("all")						# Cierra las figuras abiertas
