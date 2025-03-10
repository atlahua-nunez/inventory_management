
# Inventory_management

Inventory management es una aplicación web para gestionar el inventario de productos, permitiendo agregar,
editar y eliminar de manera sencilla.

## Tecnologías Usadas

- Python 3.13
- Flask
- SQLAlchemy
- Bootstrap 5
- SQLite

## Instalación

1. Clona este repositorio:
`git clone https://github.com/atlahua-nunez/inventory_management.git`
2. Entra en la carpeta proyecto:
`cd inventory_management`
3. Crea un entorno virtual y actívalo:
`python -m venv venv`
`source venv/bin/activte` 
En windows: `venv\Scripts\active`
4. Instala las dependencias necesarias:
`pip install -r requirements.txt`
5. Ejecuta la aplicación:
`flask run`

## Uso del Proyecto

- **Agregar productos**: Permite registrar nuevos productos en el inventario.
- **Editar productos**: Modifica la cantidad o el precio de los productos existentes.
- **Eliminar productos**: Remueve productos del inventario.

## Estructura del Proyecto

/inventory_management
|--/static
|--/templates
|--main.py
|--forms.py
|--requirements.txt
|--README.md

