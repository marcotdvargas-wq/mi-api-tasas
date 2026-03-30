import requests
from bs4 import BeautifulSoup

def get_bcv_rates():
    try:
        url = "https://www.bcv.org.ve/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer Dólar
        tasa_usd = soup.find(id="dolar").find("strong").text.strip()
        usd = float(tasa_usd.replace(',', '.'))
        
        # Extraer Euro
        tasa_eur = soup.find(id="euro").find("strong").text.strip()
        eur = float(tasa_eur.replace(',', '.'))
        
        return {"usd": usd, "eur": eur}
    except Exception as e:
        print(f"Error obteniendo BCV: {e}")
        return {"usd": None, "eur": None}

def get_binance_p2p_rate(trade_type="BUY"):
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True, 
            "page": 1,
            "rows": 10,
            "transAmount": "10000",
            "publisherType": "merchant",
            "tradeType": trade_type
        }
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        
        # Obtener todos los precios
        all_prices = [float(adv['adv']['price']) for adv in data['data']]
        
        # Tomar los resultados 2, 3 y 4 (índices 1, 2 y 3 en Python)
        if len(all_prices) >= 4:
            seleccionados = all_prices[1:4] 
            promedio = sum(seleccionados) / len(seleccionados)
            return round(promedio, 2)
        elif len(all_prices) > 0:
            return round(sum(all_prices) / len(all_prices), 2)
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo Binance VES ({trade_type}): {e}")
        return None

def get_binance_zinli_rate(trade_type="SELL"):
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        payload = {
            "fiat": "USD",
            "page": 1,
            "rows": 10,
            "tradeType": trade_type,
            "asset": "USDT",
            "countries": [],
            "payTypes": ["Zinli"],
            "publisherType": None,
            "transAmount": "1000" # <--- 🔥 ¡AQUÍ ESTÁ EL FILTRO QUE PEDISTE!
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if data and data.get("data"):
            # Tomamos el promedio de los anuncios 2, 3 y 4
            ads = data["data"]
            if len(ads) >= 4:
                prices = [float(ad["adv"]["price"]) for ad in ads[1:4]]
                return round(sum(prices) / len(prices), 3)
            elif len(ads) > 0:
                return float(ads[0]["adv"]["price"])
    except Exception as e:
        print(f"Error obteniendo Zinli ({trade_type}): {e}")
    return None
