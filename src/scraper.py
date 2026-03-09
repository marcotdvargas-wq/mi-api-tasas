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
            "merchantCheck": True, # Solo comerciantes verificados (más real)
            "page": 1,
            "rows": 10,
            "payTypes": [], # Puedes poner ["Mercadopago"] o ["Banesco"] si quieres ser más específico
            "publisherType": "merchant", # Solo anunciantes profesionales
            "tradeType": "BUY"
        }
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        
        # En lugar de promediar todos, tomamos los 5 mejores precios 
        # que suelen ser los más cercanos a lo que ves en apps como Monitor
        prices = [float(adv['adv']['price']) for adv in data['data']]
        
        if not prices: return None
        
        # Opcional: Si quieres que sea un poco más alto (más "paralelo"), 
        # podemos tomar el precio máximo de los primeros 5 en lugar del promedio.
        top_prices = prices[:5]
        return round(max(top_prices), 2) 
        
    except Exception as e:
        print(f"Error obteniendo Binance: {e}")
        return None
