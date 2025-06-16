# Bootloader para ESP32 con MicroPython

Este script implementa una clase `Bootloader` para ESP32 utilizando MicroPython. Su función es gestionar de manera automatizada la copia de archivos desde y hacia una tarjeta microSD conectada al ESP32.

## 📦 Funcionalidades

- **Copia desde microSD al almacenamiento interno** (`/`):
  - Copia solo archivos con extensiones `.py`, `.mpy` o `.json`.
  - Se excluye el directorio `/sd/backup` de la copia.
  - Solo se ejecuta si existe el archivo `update.txt` en la raíz de la microSD.
  - Al finalizar, renombra `update.txt` a `update_done.txt`.
  - Se genera un log en `update.txt`.

- **Respaldo desde almacenamiento interno a microSD**:
  - Solo se ejecuta si existe el archivo `backup.txt` en la raíz de la microSD.
  - Copia todos los archivos y carpetas del sistema interno (salvo ocultos y archivos de control) al directorio `/sd/backup/`.
  - Se excluyen los archivos como `update.txt`, `backup.txt`, etc.
  - Al finalizar, renombra `backup.txt` a `backup_done.txt`.
  - Registra los archivos respaldados en el mismo `backup.txt`.

## 📁 Estructura de archivos esperada

En la raíz de la microSD se deben colocar los siguientes archivos según lo que se quiera ejecutar:

- `update.txt` → activa el proceso de actualización (copiar desde SD al ESP32).
- `backup.txt` → activa el proceso de respaldo (copiar desde el ESP32 a la SD).

## 🧪 Ejemplo de uso

```python
from bootloader import Bootloader

boot = Bootloader()
boot.run()
