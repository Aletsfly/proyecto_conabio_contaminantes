#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un mapa coroplético que muestra el promedio del contaminante
PM2.5 por estado, uniendo los datos mediante la Clave de Entidad (CVEGEO)
y mostrando dicha clave como etiqueta en el mapa.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import unicodedata
import matplotlib.patheffects as path_effects

def limpiar_texto(texto):
    """
    Función para normalizar los nombres de los estados para el mapeo inicial.
    """
    if not isinstance(texto, str):
        return texto
    s = ''.join(c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn')
    return s.replace('_', ' ').lower().strip()

def main():
    """Función principal del script."""
    
    print("--- Iniciando script de mapa coroplético por Clave de Entidad ---")

    # --- 1. Definir Rutas ---
    ruta_base = '.'
    ruta_datos = os.path.join(ruta_base, 'data')
    ruta_salida = os.path.join(ruta_base, 'output')
    
    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)

    ruta_estados_shp = os.path.join(ruta_datos, 'dest22gw_c', 'dest22cw.shp')
    ruta_csv = os.path.join(ruta_datos, 'datos_consolidados_ordenados_concoords.csv')
    
    contaminante_a_analizar = 'pm25'

    # --- 2. Cargar y Preparar Datos ---
    try:
        print("Cargando y preparando datos de contaminación...")
        df_contaminantes = pd.read_csv(ruta_csv)
        
        df_contaminantes[contaminante_a_analizar] = pd.to_numeric(df_contaminantes[contaminante_a_analizar], errors='coerce')
        df_contaminantes.dropna(subset=[contaminante_a_analizar], inplace=True)
        
        df_contaminantes['estado_limpio'] = df_contaminantes['estado'].apply(limpiar_texto)
        
        mapa_cve_ent = {
            'aguascalientes': '01', 'baja california': '02', 'baja california sur': '03',
            'campeche': '04', 'coahuila de zaragoza': '05', 'colima': '06',
            'chiapas': '07', 'chihuahua': '08', 'ciudad de mexico': '09',
            'durango': '10', 'guanajuato': '11', 'guerrero': '12',
            'hidalgo': '13', 'jalisco': '14', 'mexico': '15',
            'michoacan de ocampo': '16', 'morelos': '17', 'nayarit': '18',
            'nuevo leon': '19', 'oaxaca': '20', 'puebla': '21',
            'queretaro': '22', 'quintana roo': '23', 'san luis potosi': '24',
            'sinaloa': '25', 'sonora': '26', 'tabasco': '27', 'tamaulipas': '28',
            'tlaxcala': '29', 'veracruz de ignacio de la llave': '30', 'yucatan': '31',
            'zacatecas': '32',
            'cdmx': '09', 'monterrey': '19', 'coahuila': '05', 'estado de mexico': '15'
        }
        df_contaminantes['cve_ent'] = df_contaminantes['estado_limpio'].map(mapa_cve_ent)
        df_contaminantes.dropna(subset=['cve_ent'], inplace=True)
        
        print("Calculando promedios por Clave de Entidad...")
        promedios_por_estado = df_contaminantes.groupby('cve_ent')[contaminante_a_analizar].mean().reset_index()

        print("\nCargando shapefile de estados de México...")
        gdf_estados = gpd.read_file(ruta_estados_shp, encoding='utf-8')
        
        # --- PASO DE DIAGNÓSTICO (OPCIONAL) ---
        # print("\nColumnas disponibles en el shapefile de estados:")
        # print(gdf_estados.columns)
        
    except Exception as e:
        print(f"ERROR: No se pudieron cargar o procesar los archivos de datos. Detalle: {e}")
        return

    # --- 3. Fusionar Datos por Clave de Entidad ---
    print("\nFusionando los datos de promedios con el mapa de estados usando la clave...")
    
    # --- CORRECCIÓN APLICADA AQUÍ ---
    # Se usa 'CVEGEO' que es la columna correcta identificada en el paso de diagnóstico.
    columna_clave_shapefile = 'CVEGEO' 

    mapa_final_gdf = gdf_estados.merge(
        promedios_por_estado,
        left_on=columna_clave_shapefile,  # Columna del shapefile
        right_on='cve_ent', # Columna que creamos en nuestro CSV
        how='left'
    )

    # --- 4. Generar el Mapa Coroplético ---
    print("Generando el mapa...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    mapa_final_gdf.plot(
        column=contaminante_a_analizar, cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True,
        missing_kwds={"color": "lightgrey", "edgecolor": "black", "hatch": "///", "label": "Sin datos"},
        legend_kwds={'label': f"Promedio de {contaminante_a_analizar.upper()} (µg/m³)", 'orientation': "horizontal"}
    )

    # --- 4.5. Añadir Etiquetas con la Clave de Entidad ---
    print("Añadiendo etiquetas con la clave de entidad al mapa...")
    for idx, row in mapa_final_gdf.iterrows():
        # Nos aseguramos de usar la misma columna correcta para la etiqueta.
        etiqueta = row[columna_clave_shapefile]
        punto_etiqueta = row.geometry.representative_point()
        plt.text(x=punto_etiqueta.x, y=punto_etiqueta.y, s=etiqueta, fontsize=8, ha='center', va='center', color='black',
                 path_effects=[path_effects.withStroke(linewidth=2, foreground='white')])

    # --- 5. Estilizar y Guardar el Mapa ---
    ax.set_title(f'Promedio de Contaminación por {contaminante_a_analizar.upper()} en México (por Clave de Entidad)', fontsize=18)
    ax.set_axis_off()

    ruta_mapa_salida = os.path.join(ruta_salida, f'mapa_coropletico_{contaminante_a_analizar}_con_claves.png')
    
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

