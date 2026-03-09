import json
import os
from datetime import datetime
from src.scraper import get_bcv_rates, get_binance_p2p_rate

def main():
    print("Iniciando actualización de tasas...")
    
    # Obtenemos el diccionario con las dos tasas del BCV
    bcv = get_bcv_rates()
    binance = get_binance_p2p_rate()
    
    output = {
        "bcv": {
            "usd": bcv["usd"],
            "eur": bcv["eur"]
        },
        "binance_p2p": binance,
        "last_update": datetime.now().isoformat(),
        "config": {
            "currency": "VES",
            "unit": "Bs."
        }
    }
    
    os.makedirs('data', exist_ok=True)
    
    with open('data/rates.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print("¡Archivo rates.json actualizado con éxito!")

if _-name-_ == "__main__":
    main()

