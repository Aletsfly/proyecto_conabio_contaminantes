#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para inspeccionar los nombres de los estados contenidos
en el archivo shapefile de CONABIO y guardar el resultado en un archivo de texto.
"""

import geopandas as gpd
import os
import unicodedata

def limpiar_texto(texto):
    """
    Función para normalizar los nombres de los estados (quitar acentos,
    convertir a minúsculas) para asegurar que coincidan.
    """
    if not isinstance(texto, str):
        return texto
    s = ''.join(c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn')
    return s.lower().strip()

# --- Definir las rutas ---
ruta_base = '.'
ruta_datos = os.path.join(ruta_base, 'data')
ruta_salida = os.path.join(ruta_base, 'output')
ruta_estados_shp = os.path.join(ruta_datos, 'dest22gw_c', 'dest22cw.shp')

# Crear la carpeta de salida si no existe
if not os.path.exists(ruta_salida):
    os.makedirs(ruta_salida)

# Ruta del archivo de reporte de salida
ruta_reporte = os.path.join(ruta_salida, 'reporte_nombres_estados.txt')

print(f"--- Inspeccionando el archivo: {ruta_estados_shp} ---")

try:
    # --- CAMBIO CLAVE: Forzamos la lectura con la codificación 'utf-8' ---
    # El error de caracteres sugiere que el archivo es UTF-8 pero no se detecta automáticamente.
    gdf_estados = gpd.read_file(ruta_estados_shp, encoding='utf-8')

    # --- Obtener los nombres de los estados ---
    nombres_originales = sorted(gdf_estados['NOMGEO'].unique())
    nombres_limpios = sorted(gdf_estados['NOMGEO'].apply(limpiar_texto).unique())

    # --- Escribir el reporte en un archivo .txt ---
    # Usamos 'with open' para manejar el archivo de forma segura
    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        f.write("--- REPORTE DE NOMBRES DE ESTADOS EN EL ARCHIVO DE CONABIO ---\n")
        f.write(f"Archivo inspeccionado: {ruta_estados_shp}\n")
        
        f.write("\n>>> LISTA DE NOMBRES DE ESTADOS (ORIGINALES):\n")
        for nombre in nombres_originales:
            f.write(f"- {nombre}\n")
            
        f.write("\n>>> LISTA DE NOMBRES DE ESTADOS (DESPUÉS DE LA LIMPIEZA):\n")
        f.write("Estos son los nombres que deben coincidir en tu archivo CSV.\n")
        for nombre in nombres_limpios:
            f.write(f"- {nombre}\n")
            
        f.write("\n--- FIN DEL REPORTE ---\n")
    
    print(f"\nReporte guardado exitosamente en: {ruta_reporte}")
    print("Por favor, abre ese archivo para ver la lista completa de estados.")

except Exception as e:
    print(f"\nERROR: No se pudo leer el archivo shapefile o escribir el reporte. Verifica las rutas. Detalle: {e}")

