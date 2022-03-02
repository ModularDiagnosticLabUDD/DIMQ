# DIMQ
Repositorio para el proyecto "Dispositivos interactivos para mediciones químicas" o  DIMQ. Este proyecto conisdera el desarrollo de una estación que integra distintos sensores de variables químicas con una interfaz al computador, con el objetivo de generar instrumentación de bajo costo para laboratorios químicos.

La versión DIMQ considera la integración de 6 sensores distintos que miden 3 variables
- pH
- Oxigeno disuelto (OD)
- NO3

La siguiente tabla resume los sensores considerados para esta estación y su principales características.

ADD TABLE

El dispositivo utiliza un microcontrolador Arduino Mega (Atmega2560)

La documentación de este proyecto se encuentra en los siguientes links
- [Drive]()
- [Click Up](https://app.clickup.com/30934223/v/li/157006335)
- [Overleaf]()

## Firmware
El firmware fue desarrollado en platformio. Para compilar nuevos cambios puede ejecutar directamente en consola los comandos 
- Compilar el código
`pio run`
- Subir y compilar al puerto autodetectado
`pio run --target upload`

### Código
El código esta escrito para el microcontrolador Arduino Mega (Atmega2560). La función principal del código es realizar la lectura de los sensores y posteriormente enviar los datos por serial. Adicionalmente, impementa un sistema de control por medio de una comunicación basada en comandos y respuestas. 
Toda la información transmitida en ambos formatos se códificada en formato Json. 
 - Lista de bibliotecas utilizadas:
  - `ArduinoJson`: (bblanchon/ArduinoJson @ ^6.18.5) Permite administrar la códificación 
  - `oneWire`: (paulstoffregen/OneWire @ ^2.3.6) Lectura del sensor de temperatura ds18b20
  - `DallasTemperature`: (milesburton/DallasTemperature @ ^3.9.1) Lectura del sensor de temperatura ds18b20
  - `FastLED`: () Biblioteca para administrar las funciones de los LEDs RGB ws2812

### Comandos
El formato de los comandos para configurar el dispositivo es: 

`{"cmd":"comando","arg":valor}`

En donde `"comando"` es el comando a implementar y `valor` es el valor numérico del argumento.

- Lista de comandos implementados
  - `slope` : configura la pendiente para implementar un ajuste lineal local en el dispositivo. recibe como argumento el valor de la nueva pendiente en unidades de [pH/mV]. Retora "m_ok" en caso de que se haya realizado la configuración con exito.
  - `offset` : configura el valor del offset para implementar un ajuste lineal local en el dispositivo. recibe como argumento el valor del nuevo offset en unidades de [pH]. Retora "n_ok" en caso de que se haya realizado la configuración con exito.
  - `time`: Configura el periodo de muestreo. Es el timepo que transcurre entre muestras. recibe como argumento el valor del nuevo tiempo de muestreo en unidades de [s].
  - `type` : Configura el tipo de sensor. Recibe como argumento un número equivalente al sensor a utilizar.
  - `reset`: Realiza un reset por software del dispositivo.


## Software
Por la parte del hub se ha desarrollado una aplicación que implementa una interfaz de usuario y permite comunicarse con los sensores. La aplicación desarrollada se estructura en un sistema de 3 capas: GUI, implementa el módulo grafico que ve el usuario; Interfaz de hardware, código que implementa la comunicación de bajo nivel con el dispositivo; MainApp es el código que implementa comunicación entre las otras dos otras capas, entregandole funcionalidad a la gui. Adicionalmente esta última capa puede funcionar independiente de la gui como una aplicación con interfaz de consola agregando la opción `-cli` al ejecutarlo. 
