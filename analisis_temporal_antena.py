#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un gráfico de series temporales de un contaminante
para una antena específica.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def main():
    """Función principal del script."""
    
    # --- PARÁMETROS DE ANÁLISIS (Puedes cambiar estos valores) ---
    antena_seleccionada = 't 21'
    contaminante_a_analizar = 'pm25'
    
    print(f"--- Iniciando script de series temporales para la antena '{antena_seleccionada}' ---")

    # --- 1. Definir Rutas ---
    ruta_base = '.'
    ruta_datos = os.path.join(ruta_base, 'data')
    ruta_salida = os.path.join(ruta_base, 'output')
    
    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)
        print(f"Directorio de salida creado en: {ruta_salida}")

    ruta_csv = os.path.join(ruta_datos, 'datos_consolidados_ordenados_concoords.csv')

    # --- 2. Cargar y Preparar Datos ---
    try:
        print(f"Cargando datos desde: {ruta_csv}")
        df = pd.read_csv(ruta_csv)
        
        # --- PASO CLAVE: Convertir la columna 'date' a formato de fecha ---
        # El formato 'coerce' convertirá cualquier fecha inválida en NaT (Not a Time)
        df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d', errors='coerce')
        
        # Eliminamos filas con fechas inválidas o sin datos del contaminante
        df.dropna(subset=['date', contaminante_a_analizar], inplace=True)
        
        # Forzamos la columna del contaminante a ser numérica
        df[contaminante_a_analizar] = pd.to_numeric(df[contaminante_a_analizar], errors='coerce')
        df.dropna(subset=[contaminante_a_analizar], inplace=True)
        
        # Filtramos los datos para quedarnos solo con la antena seleccionada
        df_antena = df[df['antena'] == antena_seleccionada].copy()
        
        # Verificamos si encontramos datos para la antena
        if df_antena.empty:
            print(f"\nERROR: No se encontraron datos para la antena '{antena_seleccionada}'.")
            print("Verifica que el nombre sea correcto y que existan registros para ella en el CSV.")
            return

        # Ordenamos los datos por fecha para que el gráfico de línea sea correcto
        df_antena.sort_values('date', inplace=True)

        print(f"Se encontraron {len(df_antena)} registros para la antena '{antena_seleccionada}'.")
        
    except Exception as e:
        print(f"ERROR: No se pudieron cargar o procesar los archivos de datos. Detalle: {e}")
        return

    # --- 3. Generar el Gráfico de Líneas ---
    print("Generando el gráfico de series temporales...")
    fig, ax = plt.subplots(figsize=(15, 7))

    ax.plot(df_antena['date'], df_antena[contaminante_a_analizar], marker='o', linestyle='-', label=contaminante_a_analizar.upper())

    # --- 4. Estilizar el Gráfico ---
    # Formatear el eje de fechas para que sea legible
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate() # Rota las fechas para evitar que se solapen

    ax.set_title(f'Variación de {contaminante_a_analizar.upper()} en la Antena "{antena_seleccionada}"', fontsize=16)
    ax.set_xlabel('Fecha')
    ax.set_ylabel(f'Nivel de {contaminante_a_analizar.upper()}')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Añadir una línea horizontal con el promedio
    promedio = df_antena[contaminante_a_analizar].mean()
    ax.axhline(y=promedio, color='r', linestyle='--', label=f'Promedio ({promedio:.2f})')
    ax.legend()

    # --- 5. Guardar y Mostrar el Gráfico ---
    ruta_grafico_salida = os.path.join(ruta_salida, f'tendencia_temporal_{antena_seleccionada}_{contaminante_a_analizar}.png')
    
    try:
        plt.savefig(ruta_grafico_salida, dpi=300, bbox_inches='tight')
        print(f"Gráfico guardado exitosamente en: {ruta_grafico_salida}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico. Detalle: {e}")

    print("Mostrando gráfico en una ventana. Cierra la ventana para finalizar el script.")
    plt.show() 
    
    print("--- Script finalizado ---")


if __name__ == "__main__":
    main()
