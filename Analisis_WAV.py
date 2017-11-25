import numpy as np					# importa libreria de matematicas
import scipy.io.wavfile				# importa libreria de lectura de archivos.wav
import matplotlib.pyplot   			# importa libreria de graficacion matematica
from tkinter import * 				# importa dependencia de matplotlib.pyplot (funcion desconocida)
from matplotlib import pyplot as plt

# Leera el archivo .wav obteniendo dos valores de salida (rate,data): 

#Se le solicita al usiario ingresar el nombre del archivo .wav
Archivo    = input("Archivo(/home/martin/Escritorio/Proyecto  .wav): ")
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
Start = 0 					# Bool denota que ya empezo el frame

#Se abre/crea un archivo que contendra los datos procesados
Archivo_letra = open("Archivo_letra_"+Archivo,"w+") 

#Variables para analisis y graficacion de datos
D_test  =[0]*len(data)
D_test2 =[0]*len(data)
D_test3 =[0]*len(data)
D_test4 =[0]*len(data)


#Variables Traduccion binario-ASCII
Letras=[]
Archivo_Letras=open("Archivo_Letras", "w+")
diccionario={"000000010010011110101100000111101001100":"a",'000000010010011110101100000001011011000':"b",'0000000100100111101011000011100110101000':"c",'0000000010010011110101100001111101010000':"d",'0000000100100111101011000010101010101000':"e",'000000010010011110101100011111101101000':"f",'0000000100100111101011000000000111101000':"g",'000000010010011110101100010000011001100':"h",'0000000100100111101011000111101010001000':"i",'000000010010011110101100001000011101000':"j",'000000010010011110101100011000011010000':"k",'000000010010011110101100000100011011100':"l",'0000000100100111101011000010010110001000':"m",'000000010010011110101100010001011100000':"n",'0000000100100111101011000000011011100000':"o",'0000000100100111101011000100011010010000':"p",'0000000100100111101011000000101010010000':"q",'000000010010011110101100011010101101100':"r",'0000000100100111101011000101111011101000':"s",'000000010010011110101100000110101100000':"t",'000000010010011110101100001110101111100':"u",'000000010010011110101100011110011101100':"v",'0000000100100111101011000100101011100000':"w",'000000010010011110101100010110011110000':"x",'000000010010011110101100010110101011000':"y",'000000010010011110101100000110011001000':"z",'0000000100100111101011000011110111110000':" ",'0000000100100111110101100001111101010000':"p",'00000001001000111101011000011110111110000':"d",'000000010010011110101100001111101010000':"d",'00000001001001111011011000100011010010000':"p",'0000000100100111101101100001000011101000':"j"}

# **************************************************************************************************************************
#					             	Filtrado de Ruido
# **************************************************************************************************************************

#------------------------------------------------------------------------------
#------------------------      VARIABLES DEL FILTRO   000000010010011110101100011000011010000 ------------------------
#------------------------------------------------------------------------------

u  = 0.02*np.pi   	#Frecuecia que se desea eliminar (MODIFICAR SOLO EL NUMERO)
r  = 0.5  	     	#Radio del polo
wc = 0.04*np.pi 	#Frecuencia a fitrar(MODIFICAR SOLO EL NUMERO)

inicio_t_filtro = 0 #inicio del tiempo en cero que esta entre los bits del filtro (valor discreto)

#------------------------------------------------------------------------------
#----------------------------       FILTRO     --------------------------------
#------------------------------------------------------------------------------

#Inicializacion de variables (entradas y salidas pasadas)

x_1,x_2,x_3,y_1,y_2,y_3 = 0,0,0,0,0,0

#Normalizacion
X1c1 = np.sqrt((1 +        np.cos(u))**2 +       (np.sin(u))**2)
X1c2 = np.sqrt((1 +   np.cos(u + wc))**2 +  (np.sin(u + wc))**2)
X1c3 = np.sqrt((1 +   np.cos(u - wc))**2 +  (np.sin(u - wc))**2)
X2p1 = np.sqrt((1 -      r*np.cos(u))**2 +     (r*np.sin(u))**2)
X2p2 = np.sqrt((1 -  r*np.cos(u + u))**2 + (r*np.sin(u + u))**2)
X2p3 = np.sqrt((1 -  r*np.cos(u - u))**2 + (r*np.sin(u - u))**2)

b0 = 10*(X2p1*X2p2*X2p3)/(X1c1*X1c2*X1c3)

#Salida
A = 2*np.cos(wc) + 1    #Multiplos de entradas anteriores
B = 2*np.cos(u)  + 1	#Multiplos de salidas anteriores

for i in range(1,len(data)):

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

	if (Data_mask[i] == 1) and (Data_mask[i-1] == 0)and((i-1)-inicio_t_filtro < 0.0012*rate):
		for n in range(inicio_t_filtro,i):
			Data_mask[n] = 1
		inicio_t_filtro = 0

for i in range(len(data)):
	if (Data_mask[i] == 1) and (Data_mask[i-1] == 0): 
		aux_inicio = i

	if (Data_mask[i] == 0) and (Data_mask[i-1] == 1): 
		if (i - aux_inicio < 0.012*rate):
			for n in range(aux_inicio,i):
				Data_mask[n] = 0

# ----------------------------------------------------------------------------------------------------------------------
# Seccion de procesamiento de datos
 
for i in range(len(data)):				# For en el que se leen todos los valores de data

	if Data_mask[i] == 1:				#Uso de la mascara para eliminar el ruido
		Data_cp[i] = data[i][0]/6000
	else:
		Data_cp[i] = 0


# **************************************************************************************************************************
#					             	Decodificacion
# **************************************************************************************************************************

	# Detecta los cambios de un + a un - para Detectar el inicio de una pulso
	if (inicio_bit == 0)and(Signo_last == -1)and(np.sign(Data_cp[i]) == 1):
		inicio_bit = i-1 	    # se guarda el momento en que se inicia una pulso
		#Pulso += 1				# Se cambia de pulso
		#Datos_decod.append("")  # Nueva fila para un nuevo pulso
		D_test2[i-1] = -2
		#print("Pulso#: "+str(Pulso+1)+" en "+str(i/rate)) #TEST? se muertra los tiempos de inicio de cada pulso

	# Detecta el tiempo de estabilidad en cero entre pulsos
	if (Data_cp[i] == 0)and(Data_cp[i-1] == 0)and(Data_cp[i-2] == 0)and(Data_cp[i-3] == 0)and(Data_cp[i-4] == 0):
		inicio_bit = 0		# Estado entre pulsos
		Signo_last = 0
	
	# Detecta los cambio de signo
	if (Signo_last != np.sign(Data_cp[i]))and(inicio_bit != 0):	# Detecta los cambios de un valor negativo a un valor positivo
		
		P_bit = (i-inicio_bit)/(Duracion_bit*rate) #tiempo entr cambio de signo(en relacion al periodo de un bit)
		D_test[i-1] = -P_bit #TEST

		#3 Periodos de bit sin cambio, es un cambio de frame
		if P_bit > 3:
			

			if Start == 1:	#Se establece condicion para solo guardar los datos del frame
				Start = 0
			else:
				Start = 1
				Datos_decod.append("")  # Nueva fila para un nuevo pulso
				Pulso += 1				# Se cambia de pulso
				print("Pulso#: "+str(Pulso+1)+" en "+str(i/rate)) #TEST? se muertra los tiempos de inicio de cada pulso

		#En caso de que el cambio de signo se encuentre en el medio del periodo del bit se
		#asume que es un 1 y se revisa si en el periodo pasado nu hubo cambios(0)
		if 0.25<(P_bit-int(P_bit))<0.75:

			inicio_bit = i - (Duracion_bit*rate)/2 #Correccion de variaciones en el periodo del bit
			if Start == 1:        #solo se graban los datos del frame
				if  2.5<P_bit<3 : #no hubo cambio en el periodo pasado por lo tanto 01
					Datos_decod[Pulso] += "0"
					Datos_decod[Pulso] += "1"
					D_test3[i]=1 #TEST
					D_test3[i-int(Duracion_bit*rate)]=0.5 #TEST

				else:
					Datos_decod[Pulso] += "1" #hubo cambio en el periodo de bit pasado entonces 1
					D_test3[i]=1 #TEST

		else: #el cambio ocurrio entre dos periodos por lo tanto el segundo es cero
			inicio_bit = i #Correccion de variaciones en el periodo del bit
			
			if Start == 1:        #solo se graban los datos del frame
				if  1.5<P_bit<2.5 : #no hubo cambio en el periodo pasado por lo tanto 00
					Datos_decod[Pulso] += "0"
					Datos_decod[Pulso] += "0"
					D_test3[i+int(Duracion_bit*rate/2)]=0.5 #TEST
					D_test3[i-int(Duracion_bit*rate/2)]=0.5 #TEST

				else:
					Datos_decod[Pulso] += "0"
					D_test3[i+int(Duracion_bit*rate/2)]=0.5 #TEST
					
		
	#TEST
	if ((inicio_bit != 0)and( (i-inicio_bit)%(Duracion_bit*rate) < 1)):
		D_test4[i] = -1
	#TEST

	#Actualiza el valor del signo
	if np.sign(Data_cp[i]) != 0:
		Signo_last = np.sign(Data_cp[i])
	
Archivo_letra.write(str(Datos_decod)) #se escriben los datos en el archivo correspondiente
Archivo_letra.close() #se cierra el archivo


# -------------------------------------------------------------------------------------------------------------------------
#					             	Decodificacion (SIMULACION)
# --------------------------------------------------------------------------------------------------------------------------

#Grafica de magnitud de los datos (tanto el .wav como los tiempos de duracion de cada bit)

Figura = matplotlib.pyplot.figure() 	# Crean la figura que contendra la grafica
Grafica_data = Figura.add_subplot(111)  # Crea la grafica
x_points = list(range(len(data)))		# Crea una indexacion para los datos (recordar que cada data[i][0] esta relacionado con un i, no con el tiempo)

for i in x_points:						# convierte la indexacion a segundos
	x_points[i] /= rate					# Esto se lee x_points[i] = x_points[i]/rate


#Grafica verde, mide(en periodos: 1,2,3... etc) las distancias entre cambios de signo
Trazo2 = Grafica_data.plot(x_points, D_test, 'g', linestyle='-', marker='.',color='g')
#Grafica roja marca cada nuevo pulso
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

# --------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------



# **************************************************************************************************************************
#					             	Traduccion binario-ASCII
# **************************************************************************************************************************

cuenta = 0
for x in range(len(Datos_decod)-3): 	#Datos en el rango de los datos decodificados

	if x%4 == 0: 				#Busca los datos ubicados en una posicón que sea múltiplo de 4, ya que ahí habrá una nueva letra
		if str(diccionario.get(Datos_decod[x])) == 'None' and cuenta < 3:
				cuenta = cuenta + 1
				
		Letras.append(Datos_decod[x+cuenta]) #Agrega las letras filtradas a una lista llamada "Letras"

Archivo_Letras.write(str(Letras))
Archivo_Letras.close()

string_Salida = ''

contador=0 #contador de los índices de la lista
for buscador in range(len(Letras)):#Datos dentro del rango de los datos decodificados filtrados
	if (contador < len(Letras)):#se recorre indice por indice de la lista
		descriptado = Letras[buscador] #según el indice, se selecciona el valor que se ubica en dicho indice de la lista
		string_Salida = string_Salida + str(diccionario.get(descriptado)) #se compara con alguno de los valores del diccionario
		contador = contador+1 #se incrementa el valor del contador, para seguir con el siguiente índice

print (string_Salida)	

# **************************************************************************************************************************
#					             	FIN DE EJECUCION
# **************************************************************************************************************************

nada=input("Salir: ")
matplotlib.pyplot.close("all")						# Cierra las figuras abiertas