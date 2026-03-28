import json
import os
from datetime import datetime, timezone, timedelta
# Importamos la nueva función de zinli junto a las que ya tenías
from src.scraper import get_bcv_rates, get_binance_p2p_rate, get_binance_zinli_rate

def main():
    print("Iniciando actualización de tasas y radares (VES y ZINLI)...")
    
    vzla_tz = timezone(timedelta(hours=-4))
    now_vzla = datetime.now(vzla_tz)
    
    # 1. Intentar leer el precio anterior de rates.json para calcular variación
    last_price = 0
    if os.path.exists('data/rates.json'):
        with open('data/rates.json', 'r') as f:
            try:
                old_data = json.load(f)
                last_price = old_data.get('binance_p2p', 0)
            except: 
                last_price = 0

    # 2. Obtener los datos de los scrapers
    bcv = get_bcv_rates()
    current_binance = get_binance_p2p_rate()
    current_zinli = get_binance_zinli_rate() # <--- NUEVO RADAR ACTIVADO
    
    # 3. Calcular variación porcentual (Para VES)
    variacion = 0
    if last_price > 0 and current_binance:
        variacion = round(((current_binance - last_price) / last_price) * 100, 2)

    # ========================================================
    # 4. EL ARCHIVO PRINCIPAL (rates.json) - SEGURO Y PROTEGIDO
    # ========================================================
    output = {
        "bcv": {
            "usd": bcv.get("usd") if bcv else None,
            "eur": bcv.get("eur") if bcv else None
        },
        "binance_p2p": current_binance, # Tu app Tasa Fácil sigue usando esto sin problemas
        "binance_zinli": current_zinli, # <--- NUEVO DATO INYECTADO PARA TI
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
    # 5. EL HISTORIAL DIARIO (historial.json)
    # ========================================================
    today_str = now_vzla.strftime("%Y-%m-%d")
    hora_str = now_vzla.strftime("%H:%M")
    
    if current_binance and bcv and bcv.get("usd"):
        historial_path = 'data/historial.json'
        historial_data = {}
        if os.path.exists(historial_path):
            with open(historial_path, 'r') as f:
                try: historial_data = json.load(f)
                except: pass
                    
        historial_data[today_str] = {
            "bcv_usd": bcv.get("usd"),
            "binance_p2p": current_binance,
            "hora_registro": now_vzla.strftime("%I:%M %p") 
        }
        with open(historial_path, 'w') as f:
            json.dump(historial_data, f, indent=4)

    # ========================================================
    # 6. RADAR ESTADÍSTICO VES (tendencias_24h.json)
    # ========================================================
    if current_binance:
        tendencias_path = 'data/tendencias_24h.json'
        tendencias_data = {}
        if os.path.exists(tendencias_path):
            with open(tendencias_path, 'r') as f:
                try: tendencias_data = json.load(f)
                except: pass
        
        if today_str not in tendencias_data: tendencias_data[today_str] = {}
        tendencias_data[today_str][hora_str] = current_binance
        
        with open(tendencias_path, 'w') as f:
            json.dump(tendencias_data, f, indent=4)

    # ========================================================
    # 7. NUEVO: RADAR ESTADÍSTICO ZINLI (tendencias_zinli_24h.json)
    # ========================================================
    if current_zinli:
        zinli_path = 'data/tendencias_zinli_24h.json'
        zinli_data = {}
        if os.path.exists(zinli_path):
            with open(zinli_path, 'r') as f:
                try: zinli_data = json.load(f)
                except: pass
        
        if today_str not in zinli_data: zinli_data[today_str] = {}
        # Guardamos el precio exacto de Zinli (Ej: 1.025 USD)
        zinli_data[today_str][hora_str] = current_zinli
        
        with open(zinli_path, 'w') as f:
            json.dump(zinli_data, f, indent=4)
            
    print(f"¡Actualizado! VES: {current_binance} | ZINLI: {current_zinli}")

if __name__ == "__main__":
    main()
