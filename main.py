import json
import os
from datetime import datetime, timezone, timedelta
from src.scraper import get_bcv_rates, get_binance_p2p_rate, get_binance_zinli_rate

def main():
    print("Iniciando actualización de tasas y radares (Doble Agente VES y ZINLI)...")
    
    vzla_tz = timezone(timedelta(hours=-4))
    now_vzla = datetime.now(vzla_tz)
    
    # 1. Leer precio anterior de rates.json para calcular variación
    last_price = 0
    if os.path.exists('data/rates.json'):
        with open('data/rates.json', 'r') as f:
            try:
                old_data = json.load(f)
                last_price = old_data.get('binance_p2p', 0)
            except: 
                last_price = 0

    # 2. Scrapers Doble Agente (Compra y Venta)
    bcv = get_bcv_rates()
    
    # VES (Bolívares)
    current_binance_buy = get_binance_p2p_rate("BUY")   # El Clásico (Comprar USDT)
    current_binance_sell = get_binance_p2p_rate("SELL") # El Nuevo (Vender USDT)
    
    # ZINLI
    current_zinli_sell = get_binance_zinli_rate("SELL") # El Clásico
    current_zinli_buy = get_binance_zinli_rate("BUY")   # El Nuevo
    
    # 3. Calcular variación porcentual (Para VES clásico)
    variacion = 0
    if last_price > 0 and current_binance_buy:
        variacion = round(((current_binance_buy - last_price) / last_price) * 100, 2)

    # 4. EL ARCHIVO PRINCIPAL (rates.json) - INTACTO PARA TU CALCULADORA
    output = {
        "bcv": {
            "usd": bcv.get("usd") if bcv else None,
            "eur": bcv.get("eur") if bcv else None
        },
        "binance_p2p": current_binance_buy, # Sigue 100% igual
        "binance_zinli": current_zinli_sell, # Sigue 100% igual
        
        # Inyectamos los nuevos datos por si nuestra App Táctica los necesita rápido
        "binance_p2p_sell": current_binance_sell, 
        "binance_zinli_buy": current_zinli_buy,
        
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
        
    # 5. EL HISTORIAL DIARIO (historial.json) - INTACTO
    today_str = now_vzla.strftime("%Y-%m-%d")
    hora_str = now_vzla.strftime("%H:%M")
    
    if current_binance_buy and bcv and bcv.get("usd"):
        historial_path = 'data/historial.json'
        historial_data = {}
        if os.path.exists(historial_path):
            with open(historial_path, 'r') as f:
                try: historial_data = json.load(f)
                except: pass
                    
        historial_data[today_str] = {
            "bcv_usd": bcv.get("usd"),
            "binance_p2p": current_binance_buy,
            "hora_registro": now_vzla.strftime("%I:%M %p") 
        }
        with open(historial_path, 'w') as f:
            json.dump(historial_data, f, indent=4)

    # Función auxiliar para guardar múltiples radares sin repetir código
    def save_tendencia(file_name, rate):
        if not rate: return
        path = f'data/{file_name}'
        data = {}
        if os.path.exists(path):
            with open(path, 'r') as f:
                try: data = json.load(f)
                except: pass
        
        if today_str not in data: data[today_str] = {}
        data[today_str][hora_str] = rate
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    # 6. GUARDAR TODOS LOS RADARES HISTÓRICOS (SEPARADOS)
    save_tendencia('tendencias_24h.json', current_binance_buy)         # El Clásico de Compra VES
    save_tendencia('tendencias_venta_24h.json', current_binance_sell)   # NUEVO: Radar Venta VES
    
    save_tendencia('tendencias_zinli_24h.json', current_zinli_sell)     # El Clásico de Zinli
    save_tendencia('tendencias_zinli_compra_24h.json', current_zinli_buy) # NUEVO: Radar Compra Zinli
            
    print(f"¡Actualizado! VES(Buy): {current_binance_buy} | VES(Sell): {current_binance_sell}")
    print(f"¡Actualizado! ZINLI(Sell): {current_zinli_sell} | ZINLI(Buy): {current_zinli_buy}")

if __name__ == "__main__":
    main()
