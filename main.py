import json
import os
from datetime import datetime, timezone, timedelta
from src.scraper import get_bcv_rates, get_binance_p2p_rate

def main():
    print("Iniciando actualización de tasas, historial y radar 24h...")
    
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

    # ========================================================
    # 5. EL ARCHIVO PRINCIPAL (rates.json) - INTACTO
    # ========================================================
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
    # 6. EL HISTORIAL DIARIO (historial.json) - INTACTO
    # ========================================================
    today_str = now_vzla.strftime("%Y-%m-%d")
    
    if current_binance and bcv.get("usd"):
        historial_path = 'data/historial.json'
        historial_data = {}
        
        if os.path.exists(historial_path):
            with open(historial_path, 'r') as f:
                try:
                    historial_data = json.load(f)
                except:
                    pass
                    
        historial_data[today_str] = {
            "bcv_usd": bcv.get("usd"),
            "binance_p2p": current_binance,
            "hora_registro": now_vzla.strftime("%I:%M %p") 
        }
        
        with open(historial_path, 'w') as f:
            json.dump(historial_data, f, indent=4)

    # ========================================================
    # 7. NUEVO: EL RADAR ESTADÍSTICO (tendencias_24h.json)
    # ========================================================
    if current_binance:
        tendencias_path = 'data/tendencias_24h.json'
        tendencias_data = {}
        
        # Leemos el archivo si ya existe para no borrar lo anterior
        if os.path.exists(tendencias_path):
            with open(tendencias_path, 'r') as f:
                try:
                    tendencias_data = json.load(f)
                except:
                    pass
        
        # Obtenemos solo la hora y minuto (Ej: "14:20")
        hora_str = now_vzla.strftime("%H:%M")
        
        # Si es un día nuevo, creamos el bloque para ese día
        if today_str not in tendencias_data:
            tendencias_data[today_str] = {}
            
        # Guardamos el precio exacto en esa hora exacta
        tendencias_data[today_str][hora_str] = current_binance
        
        with open(tendencias_path, 'w') as f:
            json.dump(tendencias_data, f, indent=4)
            
    # ========================================================
    
    print(f"¡Actualizado! Binance: {current_binance} ({variacion}%)")

if __name__ == "__main__":
    main()
