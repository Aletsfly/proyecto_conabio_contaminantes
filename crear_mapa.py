#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un mapa de antenas ÚNICAS sobre la división política de
México. Carga un archivo CSV, elimina duplicados, corrige la proyección de
coordenadas (CRS) y las visualiza sobre un mapa de estados con etiquetas.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

def main():
    """Función principal del script."""
    
    print("--- Iniciando script de análisis geoespacial ---")

    # --- 1. Definir Rutas y Crear Directorio de Salida ---
    ruta_base = '.'
    ruta_datos = os.path.join(ruta_base, 'data')
    ruta_salida = os.path.join(ruta_base, 'output')

    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)
        print(f"Directorio de salida creado en: {ruta_salida}")

    ruta_estados = os.path.join(ruta_datos, 'dest22gw_c', 'dest22cw.shp')
    ruta_csv = os.path.join(ruta_datos, 'datos_consolidados_ordenados_concoords.csv')

    # --- 2. Cargamos y Procesamos los Datos ---
    try:
        print(f"Cargando shapefile de estados desde: {ruta_estados}")
        estados_gdf = gpd.read_file(ruta_estados)
        print(f"Shapefile cargado correctamente. Su CRS es: {estados_gdf.crs.name}")
        
        print(f"Cargando datos de antenas desde: {ruta_csv}")
        puntos_df = pd.read_csv(ruta_csv)
        print(f"Se cargaron {len(puntos_df)} filas en total desde el CSV.")

        puntos_df.drop_duplicates(subset=['antena', 'latitud', 'longitud'], inplace=True)
        print(f"Después de eliminar duplicados, quedan {len(puntos_df)} antenas únicas.")

        # --------------------------------------------------------------------------
        # --- IMPORTANTE A RECORDAR: Corregimos la Proyección de Coordenadas (CRS) ---
        # 1. Creamos el GeoDataFrame especificando que sus coordenadas originales
        #    están en grados (lat/lon), que corresponde al CRS "EPSG:4326".
        puntos_gdf = gpd.GeoDataFrame(
            puntos_df, 
            geometry=gpd.points_from_xy(puntos_df.longitud, puntos_df.latitud),
            crs="EPSG:4326"
        )
        print(f"Puntos creados con su CRS original: {puntos_gdf.crs.name}")

        # 2. Re-proyectamos (transformamos) los puntos al mismo CRS que el mapa de México.
        puntos_gdf = puntos_gdf.to_crs(estados_gdf.crs)
        print(f"Puntos re-proyectados exitosamente al CRS del mapa.")
        # --------------------------------------------------------------------------

        print(f"Datos de {len(puntos_gdf)} antenas únicas listos para el mapa.")

    except KeyError as e:
        print(f"\nERROR: No se encontró la columna {e} en tu archivo CSV.")
        print("Por favor, revisa el código y asegúrate de que los nombres de las columnas ('antena', 'longitud', 'latitud') sean correctos.")
        return
    except Exception as e:
        print(f"\nERROR: Ocurrió un error en el procesamiento de datos. Detalle: {e}")
        return

    # --- 3. Generamos el Mapa ---
    print("Generando el mapa base...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    estados_gdf.plot(ax=ax, color='#e0e0e0', edgecolor='black')
    puntos_gdf.plot(ax=ax, color='red', markersize=25, label='Antenas')

    # --- 3.5. Añadimos Etiquetas para cada Antena ---
    print("Añadiendo etiquetas de las antenas al mapa...")
    for idx, row in puntos_gdf.iterrows():
        plt.text(
            row.geometry.x + 10000, # Pequeño desfase en METROS
            row.geometry.y,
            row.antena,
            fontsize=7,
            ha='left',
            va='center',
            color='black'
        )

    # --- 4. Estilizamos y Guardamos el Mapa ---
    ax.set_title(f'{len(puntos_gdf)} Antenas Únicas en México', fontsize=20)
    ax.set_xlabel('Longitud (Metros)')
    ax.set_ylabel('Latitud (Metros)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    ruta_mapa_salida = os.path.join(ruta_salida, 'mapa_antenas_final.png')
    
    try:
        plt.savefig(ruta_mapa_salida, dpi=300, bbox_inches='tight')
        print(f"Mapa guardado exitosamente en: {ruta_mapa_salida}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el mapa. Detalle: {e}")

    print("Mostrando mapa en una ventana. Cierra la ventana para finalizar el script.")
    plt.show()

    print("--- Script finalizado ---")


if __name__ == "__main__":
    main()