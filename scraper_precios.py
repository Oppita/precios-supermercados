#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de extracción de precios de supermercados colombianos
Genera un archivo JSON compatible con Unity
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de productos y URLs
PRODUCTOS = {
    "aceite de oliva sublime 500ml": {
        "exito": "https://www.exito.com/aceite-de-oliva-lata-500-ml-358701/p",
        "jumbo": "https://www.jumbocolombia.com/sublime-aceite-de-oliva-x-500-ml/p?idsku=22337",
        "carulla": "https://www.carulla.com/aceite-de-oliva-lata-500-ml-358701/p"
    }
    # Aquí puedes agregar más productos siguiendo el mismo formato
    # "otro producto": {
    #     "exito": "url_exito",
    #     "jumbo": "url_jumbo", 
    #     "carulla": "url_carulla"
    # }
}

# Selectores CSS para cada supermercado
SELECTORES = {
    "exito": [
        'p[class*="ProductPrice_container__price"]',
        '.ProductPrice_container__price',
        '[data-testid="price"]'
    ],
    "carulla": [
        'p[class*="ProductPrice_container__price"]',
        '.ProductPrice_container__price',
        '[data-testid="price"]'
    ],
    "jumbo": [
        'div[class*="price"]',
        '.tiendasjumboqaio-product-price-breakdown-0-x-price',
        '[class*="price-breakdown"]'
    ]
}

def configurar_driver():
    """Configura y retorna el driver de Chrome"""
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error configurando driver: {e}")
        return None

def limpiar_precio(texto_precio):
    """Limpia y convierte el texto del precio a número"""
    if not texto_precio:
        return None
    
    # Remover caracteres no numéricos excepto punto y coma
    texto_limpio = texto_precio.replace('$', '').replace('&nbsp;', '').replace('\xa0', '').strip()
    texto_limpio = ''.join(c for c in texto_limpio if c.isdigit() or c in '.,')
    
    # Manejar formato colombiano (punto como separador de miles, coma como decimal)
    if ',' in texto_limpio and '.' in texto_limpio:
        # Formato: 1.234,56 o 1,234.56
        if texto_limpio.rindex('.') > texto_limpio.rindex(','):
            # Formato americano: 1,234.56
            texto_limpio = texto_limpio.replace(',', '')
        else:
            # Formato europeo: 1.234,56
            texto_limpio = texto_limpio.replace('.', '').replace(',', '.')
    elif ',' in texto_limpio:
        # Solo coma - podría ser decimal o separador de miles
        partes = texto_limpio.split(',')
        if len(partes[-1]) <= 2:  # Probablemente decimal
            texto_limpio = texto_limpio.replace(',', '.')
        else:  # Probablemente separador de miles
            texto_limpio = texto_limpio.replace(',', '')
    elif '.' in texto_limpio:
        # Solo punto - mantener como está
        pass
    
    try:
        precio = float(texto_limpio)
        return int(precio) if precio.is_integer() else precio
    except (ValueError, AttributeError):
        print(f"No se pudo convertir '{texto_precio}' → '{texto_limpio}' a número")
        return None

def extraer_precio_supermercado(driver, supermercado, url, timeout=10):
    """Extrae el precio de un supermercado específico"""
    try:
        print(f"  Accediendo a {supermercado}: {url}")
        driver.get(url)
        
        # Esperar a que la página cargue
        time.sleep(3)
        
        # Intentar diferentes selectores
        precio_element = None
        for selector in SELECTORES.get(supermercado, []):
            try:
                precio_element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if precio_element and precio_element.text.strip():
                    break
            except:
                continue
        
        if not precio_element:
            # Fallback: buscar cualquier elemento que contenga precio
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            posibles_precios = soup.find_all(text=lambda t: t and '$' in str(t) and any(c.isdigit() for c in str(t)))
            
            if posibles_precios:
                precio_text = posibles_precios[0].strip()
            else:
                print(f"    ❌ No se encontró precio en {supermercado}")
                return None
        else:
            precio_text = precio_element.text.strip()
        
        precio = limpiar_precio(precio_text)
        if precio and precio > 0:
            print(f"    ✅ Precio encontrado: ${precio:,.0f}")
            return precio
        else:
            print(f"    ❌ Precio inválido: '{precio_text}'")
            return None
            
    except Exception as e:
        print(f"    ❌ Error extrayendo precio de {supermercado}: {e}")
        return None

def extraer_todos_los_precios():
    """Extrae precios de todos los productos y supermercados"""
    driver = configurar_driver()
    if not driver:
        print("❌ No se pudo configurar el driver de Chrome")
        return None
    
    resultados = []
    
    try:
        for nombre_producto, urls_supermercados in PRODUCTOS.items():
            print(f"\n📦 Procesando: {nombre_producto}")
            
            precios_producto = {}
            
            for supermercado, url in urls_supermercados.items():
                precio = extraer_precio_supermercado(driver, supermercado, url)
                precios_producto[supermercado] = precio if precio else 0
            
            # Solo agregar si encontramos al menos un precio válido
            if any(precio > 0 for precio in precios_producto.values()):
                resultados.append({
                    "producto": nombre_producto,
                    "precios": precios_producto
                })
                print(f"  ✅ Producto agregado con {sum(1 for p in precios_producto.values() if p > 0)} precios")
            else:
                print(f"  ⚠️  No se encontraron precios válidos para {nombre_producto}")
    
    finally:
        driver.quit()
    
    return resultados

def generar_json(datos, archivo_salida="precios.json"):
    """Genera el archivo JSON con los datos extraídos"""
    if not datos:
        print("❌ No hay datos para generar JSON")
        return False
    
    # Estructura final del JSON
    json_final = {
        "metadata": {
            "fecha_actualizacion": datetime.now().isoformat(),
            "version": "1.0",
            "descripcion": "Precios de supermercados colombianos"
        },
        "entries": datos
    }
    
    try:
        # Guardar con formato legible
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(json_final, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON generado exitosamente: {archivo_salida}")
        print(f"📊 Total de productos: {len(datos)}")
        
        # Mostrar resumen
        for item in datos:
            precios_validos = sum(1 for p in item['precios'].values() if p > 0)
            print(f"  • {item['producto']}: {precios_validos}/3 precios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando JSON: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando extracción de precios...")
    print("=" * 50)
    
    # Extraer precios
    datos = extraer_todos_los_precios()
    
    if datos:
        # Generar JSON
        if generar_json(datos):
            print(f"\n🎉 Proceso completado exitosamente!")
            print(f"📁 Archivo generado: precios.json")
            
            # Mostrar contenido para verificar
            try:
                with open("precios.json", 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                print(f"\n📋 Vista previa del JSON:")
                print(json.dumps(contenido, ensure_ascii=False, indent=2))
            except:
                print("No se pudo mostrar vista previa")
        else:
            print("❌ Error generando el archivo JSON")
    else:
        print("❌ No se pudieron extraer datos")
    
    print("\n" + "=" * 50)
    print("Proceso finalizado")

if __name__ == "__main__":
    main()
