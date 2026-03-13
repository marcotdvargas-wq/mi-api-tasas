import json
import os
from datetime import datetime, timezone, timedelta
from src.scraper import get_bcv_rates, get_binance_p2p_rate

def main():
    print("Iniciando actualización de tasas y registro de historial...")
    
    # 1. Configurar la hora exacta de Venezuela (UTC-4)
    vzla_tz = timezone(timedelta(hours=-4))
    now_vzla = datetime.now(vzla_tz)
    
    # 2. Intentar leer el precio anterior de rates.json
    last_price = 0
    if os.path.exists('data/rates.json'):
        with open('data/rates.json', 'r') as f:
            try:
                old_data = json.load(f)
                last_price = old_data.get('binance_p2p', 0)
            except: 
                last_price = 0

    # 3. Obtener los nuevos datos del scraper
    bcv = get_bcv_rates()
    current_binance = get_binance_p2p_rate()
    
    # 4. Calcular variación porcentual
    variacion = 0
    if last_price > 0 and current_binance:
        variacion = round(((current_binance - last_price) / last_price) * 100, 2)

    # 5. Guardar el archivo principal (rates.json) - EXACTAMENTE COMO ANTES
    output = {
        "bcv": {
            "usd": bcv.get("usd"),
            "eur": bcv.get("eur")
        },
        "binance_p2p": current_binance,
        "cambio_p2p": {
            "porcentaje": f"{variacion}%",
            "estado": "subio" if variacion > 0 else "bajo" if variacion < 0 else "estable",
            "simbolo": "▲" if variacion > 0 else "▼" if variacion < 0 else "▬"
        },
        "last_update": now_vzla.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {
            "currency": "VES",
            "unit": "Bs."
        }
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/rates.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    # ========================================================
    # 6. NUEVA FUNCIÓN: EL HISTORIAL (El Diario del Robot)
    # ========================================================
    if current_binance and bcv.get("usd"):
        # Obtenemos la fecha de hoy en formato YYYY-MM-DD (Ej: 2026-03-13)
        today_str = now_vzla.strftime("%Y-%m-%d")
        historial_path = 'data/historial.json'
        
        historial_data = {}
        # Leemos el historial viejo si ya existe
        if os.path.exists(historial_path):
            with open(historial_path, 'r') as f:
                try:
                    historial_data = json.load(f)
                except:
                    pass
                    
        # Anotamos en la libreta el dato de hoy.
        # Al correr a las 10:00 PM, se guardará este valor.
        historial_data[today_str] = {
            "bcv_usd": bcv.get("usd"),
            "binance_p2p": current_binance,
            "hora_registro": now_vzla.strftime("%I:%M %p") # Ej: 10:00 PM
        }
        
        # Guardamos la libreta
        with open(historial_path, 'w') as f:
            json.dump(historial_data, f, indent=4)
            
    # ========================================================
    
    print(f"¡Actualizado! Binance: {current_binance} ({variacion}%)")

if __name__ == "__main__":
    main()
