# DIMQ
Repositorio para el proyecto "Dispositivos interactivos para mediciones químicas" o  DIMQ. Este proyecto conisdera el desarrollo de una estación que integra distintos sensores de variables químicas con una interfaz al computador, con el objetivo de generar instrumentación de bajo costo para laboratorios químicos.

La versión DIMQ considera la integración de 6 sensores distintos que miden 3 variables
- pH
- Oxigeno disuelto (OD)
- NO3

La siguiente tabla resume los sensores considerados para esta estación y su principales características.

ADD TABLE

El dispositivo utiliza un microcontrolador m

La documentación de este proyecto se encuentra en los siguientes links
- Drive 
- Click Up
- Overleaf

## Firmware
El firmware fue desarrollado en platformio. Para compilar nuevos cambios puede ejecutar directamente en consola los comandos 
- Compilar el código
'pio run'
- Subir y compilar al puerto autodetectado
'pio run --target upload'

### Código
