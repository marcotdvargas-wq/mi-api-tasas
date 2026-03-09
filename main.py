import json
import os
from datetime import datetime
from src.scraper import get_bcv_rate, get_binance_p2p_rate

def main():
    print("Iniciando actualización de tasas...")
    
    bcv = get_bcv_rate()
    binance = get_binance_p2p_rate()
    
    output = {
        "bcv": bcv,
        "binance_p2p": binance,
        "last_update": datetime.now().isoformat(),
        "currency": "VES",
        "symbol": "Bs."
    }
    
    # Asegurar que la carpeta data existe
    os.makedirs('data', exist_ok=True)
    
    with open('data/rates.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print("¡Archivo rates.json actualizado con éxito!")

if __name__ == "__main__":
    main()