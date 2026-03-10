import json
import os
from datetime import datetime
from src.scraper import get_bcv_rates, get_binance_p2p_rate

def main():
    print("Iniciando actualización táctica...")
    
    # 1. Intentar leer el precio anterior para calcular la variación
    last_price = 0
    if os.path.exists('data/rates.json'):
        with open('data/rates.json', 'r') as f:
            try:
                old_data = json.load(f)
                last_price = old_data.get('binance_p2p', 0)
            except: 
                last_price = 0

    # 2. Obtener los nuevos datos llamando a los nombres correctos
    bcv = get_bcv_rates()
    current_binance = get_binance_p2p_rate()
    
    # 3. Calcular variación porcentual
    variacion = 0
    if last_price > 0 and current_binance:
        variacion = round(((current_binance - last_price) / last_price) * 100, 2)

    # 4. Crear el JSON final
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
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%59:00"),
        "config": {
            "currency": "VES",
            "unit": "Bs."
        }
    }
    
    # Guardar archivo
    os.makedirs('data', exist_ok=True)
    with open('data/rates.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"¡Actualizado! Binance: {current_binance} ({variacion}%)")

if __name__ == "__main__":
    main()
