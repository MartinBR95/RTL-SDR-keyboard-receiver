import numpy as np					# importa libreria de matematicas
import scipy.io.wavfile				# importa libreria de lectura de archivos.wav
import matplotlib.pyplot   			# importa libreria de graficacion matematica
from tkinter import * 				# importa dependencia de matplotlib.pyplot (funcion desconocida)
from matplotlib import pyplot as plt

# Leera el archivo .wav obteniendo dos valores de salida (rate,data): 

#Se le solicita al usiario ingresar el nombre del archivo .wav
Archivo    = input("Archivo(/home/martin/Escritorio/Proyecto .wav): ")
rate, data = scipy.io.wavfile.read("/home/martin/Escritorio/Proyecto/"+Archivo+".wav") 
	# rate: El valor de muestras por segundo (frecuencia de muestreo).
	# data: Una matriz de n fila y dos columnas con los valores de audio (oido izquierdo y oido derecho).

# ------------------------------------------------------------------------------------------ ----------------------------
# inicializa matriz que contendra los valores procesados de los datos del .WAV (Data_t = []_x1M)

#Vectores (matriz de una fila)
Data_filtro = [0]*len(data) # Datos filtrados
Data_mask = [0]*len(data)   # Mascara que se usara para eliminar el ruido de los datos
Data_cp   = [0]*len(data)	# Copia de datos de entrada (data)
Duracion_bit = 0.0004	    # Define la duracion esperada de un bit
P_bit = 0					# Tiempo (en periodos: 1,2,3... etc) las distancias entre cambios de signo
Signo_last = 0				# Ultimo signo(no cero) registrado (para poder detectar correctamente cambios de signo)
inicio_bit = 0			    # Momento(Discreto) en que se inicia un bit 
Pulso = -1					# numero de Pulso que se esta guardando (primera,segunda.etc)
Datos_decod = []			# Vector en el que se guardaran los datos decodificados

#Se abre/crea un archivo que contendra los datos procesados
Archivo_letra = open("Archivo_letra_"+Archivo,"w+") 

#Variables para analisis y graficacion de datos
D_test  =[0]*len(data)
D_test2 =[0]*len(data)
D_test3 =[0]*len(data)
D_test4 =[0]*len(data)

# **************************************************************************************************************************
#					             	Filtrado de Ruido
# **************************************************************************************************************************


#------------------------------------------------------------------------------
#------------------------      VARIABLES DEL FILTRO    ------------------------
#------------------------------------------------------------------------------

N = [0]*len(data)    	#Variable N a muestrear (SIMULACION)

for i in range(1,len(data)):
	N[i] = i

s = len(N)    		#Tama�o de matriz (SIMULACION) 

u  = 0.02*np.pi   	#Frecuecia que se desea eliminar (MODIFICAR SOLO EL NUMERO)
r  = 0.5  	     	#Radio del polo
wc = 0.04*np.pi 	#Frecuencia a fitrar(MODIFICAR SOLO EL NUMERO)

inicio_t_filtro=0     #inicio del tiempo en cero que esta entre los bits del filtro (valor discreto)
#------------------------------------------------------------------------------
#----------------------------       FILTRO     --------------------------------
#------------------------------------------------------------------------------

#Inicializacion de variables (entradas y salidas pasadas)

x_1 = 0
x_2 = 0
x_3 = 0
y_1 = 0
y_2 = 0
y_3 = 0

#Normalizacion
X1c1 = np.sqrt((1 +        np.cos(u))**2 +       (np.sin(u))**2)
X1c2 = np.sqrt((1 +   np.cos(u + wc))**2 +  (np.sin(u + wc))**2)
X1c3 = np.sqrt((1 +   np.cos(u - wc))**2 +  (np.sin(u - wc))**2)

X2p1 = np.sqrt((1 -      r*np.cos(u))**2 +     (r*np.sin(u))**2)
X2p2 = np.sqrt((1 -  r*np.cos(u + u))**2 + (r*np.sin(u + u))**2)
X2p3 = np.sqrt((1 -  r*np.cos(u - u))**2 + (r*np.sin(u - u))**2)

b0 = 10*(X2p1*X2p2*X2p3)/(X1c1*X1c2*X1c3)

#Salida
A = 2*np.cos(wc) + 1
B = 2*np.cos(u)  + 1

for i in range(1,s):

	Data_filtro[i] = data[i][0]

	if abs(Data_filtro[i]) > 3000:
	  	Data_filtro[i] = 0

	Data_mask[i] = b0*( x_1*A + x_2*A + x_3 + Data_filtro[i]) + y_1*B*r - y_2*B*r**2 + y_3*r**3

	x_3 = x_2 
	x_2 = x_1 
	x_1 = Data_filtro[i]
  
	y_3 = y_2 
	y_2 = y_1 
	y_1 = Data_mask[i]

	if Data_mask[i] > 17000:
		Data_mask[i] = 1
	else:
	    if Data_mask[i] < -17000:
	    	Data_mask[i] = 1
	    else: 
	        Data_mask[i] = 0


for i in range(len(data)):
	if (Data_mask[i] == 0) and (Data_mask[i-1] == 1): 
		inicio_t_filtro = i

	if (Data_mask[i] == 1) and (Data_mask[i-1] == 0):
		if (i-1)-inicio_t_filtro < 0.0012*rate:
			for n in range(inicio_t_filtro,i):
				Data_mask[n] = 1
		inicio_t_filtro=0


# ----------------------------------------------------------------------------------------------------------------------
# Seccion de procesamiento de datos
 
for i in range(len(data)):	# For en el que se leen todos los valores de data

	# Se copian los datos eliminando(=0) los menores a 1000(ruido en los cambio de signo)
	#if (data[i][0]>1000)or(data[i][0]<-1000):
	#	Data_cp[i] = int(data[i][0])/10000 # Se copian solo los datos del sonido izquierdo, ya que los del derecho son igual. 
								     	   # Esto se hace para trabajar con Data_cp y no modificar data 
	if Data_mask[i] == 1:
		Data_cp[i] = data[i][0]/6000
	else:
		Data_cp[i] = 0

# **************************************************************************************************************************
#					             	Decodificacion
# **************************************************************************************************************************

	# Detecta los cambios de un + a un - para Detectar el inicio de una letra
	if (inicio_bit == 0)and(Signo_last == -1)and(np.sign(Data_cp[i]) == 1):
		inicio_bit = i-1 	    # se guarda el momento en que se inicia una letra
		Pulso += 1				# Se cambia de letra
		Datos_decod.append([])  # Nueva fila para una nueva letra
		D_test2[i-1] = -2
		print("Pulso#: "+str(Pulso+1)+" en "+str(i/rate)) #TEST? se muertra los tiempos de inicio de cada letra

	# Detecta el tiempo de estabilidad en cero entre letras
	if (Data_cp[i] == 0)and(Data_cp[i-1] == 0)and(Data_cp[i-2] == 0)and(Data_cp[i-3] == 0)and(Data_cp[i-4] == 0):
		inicio_bit = 0		# Estado entre letras
		Signo_last = 0
	
	# Detecta los cambio de signo
	if (Signo_last != np.sign(Data_cp[i]))and(np.sign(Data_cp[i]) != 0)and(inicio_bit != 0):	# Detecta los cambios de un valor negativo a un valor positivo
		
		P_bit = (i-inicio_bit)/(Duracion_bit*rate) #tiempo entr cambio de signo(en relacion al periodo de un bit)
		D_test[i-1] = -P_bit #TEST

		#3 Periodos de bit sin cambio, es un cambio de frame
		if 3 < P_bit:
					Datos_decod[Pulso].append("")

		#En caso de que el cambio de signo se encuentre en el medio del periodo del bit se
		#asume que es un 1 y se revisa si en el periodo pasado nu hubo cambios(0)
		if 0.25<(P_bit-int(P_bit))<0.75:

			inicio_bit = i - (Duracion_bit*rate)/2 #Correccion de variaciones en el periodo del bit

			if  2.5<P_bit<3 : #no hubo cambio en el periodo pasado por lo tanto 01
				Datos_decod[Pulso].append(0)
				Datos_decod[Pulso].append(1)
				D_test3[i]=1 #TEST
				D_test3[i-int(Duracion_bit*rate)]=0.5 #TEST

			else:
				Datos_decod[Pulso].append(1) #hubo cambio en el periodo de bit pasado entonces 1
				D_test3[i]=1 #TEST

		else: #el cambio ocurrio entre dos periodos por lo tanto en segundo es cero
			Datos_decod[Pulso].append(0)
			D_test3[i]=0.5 #TEST
			inicio_bit = i #Correccion de variaciones en el periodo del bit

	#TEST
	if ((inicio_bit != 0)and( (i-inicio_bit)%(Duracion_bit*rate) < 1)):
		D_test4[i] = -1
	#TEST

	#Actualiza el valor del signo
	if np.sign(Data_cp[i]) != 0:
		Signo_last = np.sign(Data_cp[i])
	
Archivo_letra.write(str(Datos_decod)) #se escriben los datos en el archivo correspondiente
Archivo_letra.close() #se cierra el archivo

#Grafica de magnitud de los datos (tanto el .wav como los tiempos de duracion de cada bit)

Figura = matplotlib.pyplot.figure() 	# Crean la figura que contendra la grafica
Grafica_data = Figura.add_subplot(111)  # Crea la grafica
x_points = list(range(len(data)))		# Crea una indexacion para los datos (recordar que cada data[i][0] esta relacionado con un i, no con el tiempo)

for i in x_points:						# convierte la indexacion a segundos
	x_points[i] /= rate					# Esto se lee x_points[i] = x_points[i]/rate

# *********************************************************************************************************************
# Esta seccion comentada pregunta por si se desea graficar los puntos de muestro (meramente de simulacion)

#select_trazo = input("Mostrar puntos: S/N: ") #seleccion para mostrar puntos
#if select_trazo == "S" or select_trazo =="s":
 #	Trazo = Grafica_data.plot(x_points, Data_t = []_x1M, linestyle='-', marker='.',color='b',)	# genera la grafica
#else:
# *********************************************************************************************************************
#Grafica verde, mide(en periodos: 1,2,3... etc) las distancias entre cambios de signo
Trazo2 = Grafica_data.plot(x_points, D_test, 'g', linestyle='-', marker='.',color='g')
#Grafica roja marca cada nueva letra
Trazo3 = Grafica_data.plot(x_points, D_test2, 'r')
#Grafica cian marca los 1 como 1 y los ceros como 0.5
Trazo4 = Grafica_data.plot(x_points, D_test3, 'c')
#Gafica magenta marca cada ancho de bit 
Trazo5 = Grafica_data.plot(x_points, D_test4, 'm')
#Grafica azul datos de entrada
Trazo =  Grafica_data.plot(x_points, Data_cp, 'b')	# Genera la grafica (Coloca los valores medidos graficamente)
Grafica_data.set_xlabel('Tiempo(s)')				# Etiquetan los ejes
Grafica_data.set_ylabel('Magnitud')
Grafica_data.set_title("Archivo: "+Archivo+".wav")
Figura.show()										# Muestra la grafica

# **************************************************************************************************************************
#					             	Desencriptacion
# **************************************************************************************************************************





# **************************************************************************************************************************
#					             	FIN DE EJECUCION
# **************************************************************************************************************************
nada=input("Salir: ")
matplotlib.pyplot.close("all")						# Cierra las figuras abiertas
