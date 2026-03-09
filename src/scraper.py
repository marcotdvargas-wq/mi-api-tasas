import requests
from bs4 import BeautifulSoup

def get_bcv_rate():
    try:
        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # El BCV usa IDs específicos para cada moneda
        tasa = soup.find(id="dolar").find("strong").text.strip()
        return float(tasa.replace(',', '.'))
    except Exception as e:
        print(f"Error obteniendo BCV: {e}")
        return None

def get_binance_p2p_rate():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True,
            "page": 1,
            "rows": 5, # Bajamos a 5 para agarrar solo los más competitivos
            "tradeType": "BUY", # "BUY" para el usuario significa "SELL" para el comerciante (tasa alta)
            "transAmount": "500" # Filtramos para que ignore anuncios de 10 o 20 Bs que bajan el promedio
        }
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        
        # En lugar de promedio, tomamos el SEGUNDO o TERCER mejor precio 
        # para evitar "anuncios anzuelo" muy baratos
        prices = [float(adv['adv']['price']) for adv in data['data']]
        
        if not prices: return None
        
        # Opción A: El precio más alto de los primeros 5
        tasa_referencia = max(prices) 
        
        # Opción B: Si aún es bajo, sumamos un pequeño % de comisión operativa (opcional)
        # tasa_referencia = tasa_referencia * 1.005 

        return round(tasa_referencia, 2)
    except Exception as e:
        print(f"Error obteniendo Binance: {e}")
        return None
