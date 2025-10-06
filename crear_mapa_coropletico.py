#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un mapa coroplético (de calor) que muestra el promedio
del contaminante PM2.5 por estado en México.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import unicodedata # Para limpiar los nombres de los estados
import matplotlib.patheffects as path_effects # Módulo para efectos de texto

def limpiar_texto(texto):
    """
    Función para normalizar los nombres de los estados (quitar acentos,
    reemplazar guiones bajos y convertir a minúsculas) para asegurar que coincidan.
    """
    if not isinstance(texto, str):
        return texto
    s = ''.join(c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn')
    # Reemplazar guiones bajos con espacios, convertir a minúsculas y quitar espacios extra
    return s.replace('_', ' ').lower().strip()

def main():
    """Función principal del script."""
    
    print("--- Iniciando script de mapa coroplético ---")

    # --- 1. Definir Rutas ---
    ruta_base = '.'
    ruta_datos = os.path.join(ruta_base, 'data')
    ruta_salida = os.path.join(ruta_base, 'output')
    
    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)
        print(f"Directorio de salida creado en: {ruta_salida}")

    ruta_estados_shp = os.path.join(ruta_datos, 'dest22gw_c', 'dest22cw.shp')
    ruta_csv = os.path.join(ruta_datos, 'datos_consolidados_ordenados_concoords.csv')
    
    contaminante_a_analizar = 'pm25'

    # --- 2. Cargar y Preparar Datos ---
    try:
        print("Cargando y preparando datos de contaminación...")
        df_contaminantes = pd.read_csv(ruta_csv)
        
        # Forzamos la columna del contaminante a ser numérica, convirtiendo errores a NaN
        df_contaminantes[contaminante_a_analizar] = pd.to_numeric(df_contaminantes[contaminante_a_analizar], errors='coerce')
        df_contaminantes.dropna(subset=[contaminante_a_analizar], inplace=True)
        
        df_contaminantes['estado_limpio'] = df_contaminantes['estado'].apply(limpiar_texto)
        
        # --- CORRECCIÓN MANUAL DE NOMBRES DE ESTADO ---
        print("Corrigiendo nombres de estado específicos (cdmx, monterrey, coahuila)...")
        reemplazos = {
            'cdmx': 'ciudad de mexico',
            'monterrey': 'nuevo leon',
            'coahuila': 'coahuila de zaragoza',
            'estado de mexico': 'mexico',
        }
        df_contaminantes['estado_limpio'] = df_contaminantes['estado_limpio'].replace(reemplazos)
        
        print("Calculando promedios por estado...")
        promedios_por_estado = df_contaminantes.groupby('estado_limpio')[contaminante_a_analizar].mean().reset_index()

        print("\nCargando shapefile de estados de México...")
        # Forzamos la lectura con la codificación 'utf-8' para leer acentos correctamente.
        gdf_estados = gpd.read_file(ruta_estados_shp, encoding='utf-8')
        
        gdf_estados['estado_limpio'] = gdf_estados['NOMGEO'].apply(limpiar_texto)
        
    except Exception as e:
        print(f"ERROR: No se pudieron cargar o procesar los archivos de datos. Detalle: {e}")
        return

    # --- 3. Fusionar Datos Geoespaciales y de Contaminación ---
    print("Fusionando los datos de promedios con el mapa de estados...")
    mapa_final_gdf = gdf_estados.merge(
        promedios_por_estado,
        on='estado_limpio',
        how='left'
    )

    # --- 4. Generar el Mapa Coroplético ---
    print("Generando el mapa...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    mapa_final_gdf.plot(
        column=contaminante_a_analizar,
        cmap='viridis',
        linewidth=0.8,
        ax=ax,
        edgecolor='0.8',
        legend=True,
        missing_kwds={
            "color": "lightgrey",
            "edgecolor": "black",
            "hatch": "///",
            "label": "Sin datos",
        },
        legend_kwds={
            'label': f"Promedio de {contaminante_a_analizar.upper()} (µg/m³)",
            'orientation': "horizontal"
        }
    )

    # --- 4.5. Añadir Etiquetas para cada Estado ---
    print("Añadiendo etiquetas de los estados al mapa...")
    # Usamos representative_point() para asegurar que la etiqueta quede DENTRO del polígono.
    for idx, row in mapa_final_gdf.iterrows():
        # Obtenemos el nombre original del estado para la etiqueta
        nombre_estado = row['NOMGEO']
        # Calculamos el punto representativo para la etiqueta
        punto_etiqueta = row.geometry.representative_point()
        
        plt.text(
            x=punto_etiqueta.x,
            y=punto_etiqueta.y,
            s=nombre_estado,
            fontsize=6,
            ha='center', # Alineación horizontal centrada
            va='center', # Alineación vertical centrada
            color='black',
            # Añadimos un borde blanco al texto para que sea legible sobre cualquier color
            path_effects=[path_effects.withStroke(linewidth=2, foreground='white')]
        )

    # --- 5. Estilizar y Guardar el Mapa ---
    ax.set_title(f'Promedio de Contaminación por {contaminante_a_analizar.upper()} en México', fontsize=18)
    ax.set_axis_off()

    ruta_mapa_salida = os.path.join(ruta_salida, f'mapa_coropletico_{contaminante_a_analizar}_etiquetado.png')
    
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

