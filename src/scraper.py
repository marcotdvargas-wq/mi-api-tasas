import requests
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def limpiar_tasa_bcv(texto):
    # 1. Quita espacios, 2. Quita el punto de mil (ej. 1.006 -> 1006), 3. Cambia coma por punto decimal
    limpio = texto.strip().replace('.', '').replace(',', '.')
    return round(float(limpio), 4)

def get_bcv_rates():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Cache-Control': 'no-cache'
    }

    # INTENTO 1: Directo a la web oficial del BCV (Actualización inmediata)
    try:
        url = "https://www.bcv.org.ve/"
        response = requests.get(url, headers=headers, verify=False, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')

        tasa_usd = soup.find(id="dolar").find("strong").text
        usd = limpiar_tasa_bcv(tasa_usd)

        tasa_eur = soup.find(id="euro").find("strong").text
        eur = limpiar_tasa_bcv(tasa_eur)

        if usd > 0 and eur > 0:
            return {"usd": usd, "eur": eur}
    except Exception as e:
        print(f"Aviso: Falló scraping directo a bcv.org.ve: {e}")

    # INTENTO 2 (Respaldo): API bcv.today si la web del BCV no responde
    try:
        r1 = requests.get("https://bcv.today/api/v1/rate.json", headers=headers, timeout=10)
        if r1.status_code == 200:
            data = r1.json()
            usd = round(float(data["USD"]), 4)
            eur = round(float(data["EUR"]), 4)
            if usd > 0 and eur > 0:
                return {"usd": usd, "eur": eur}
    except Exception as e:
        print(f"Aviso: Falló respaldo 1 (bcv.today): {e}")

    # INTENTO 3 (Respaldo): API Crom Studio
    try:
        r2 = requests.get("https://datos.cromstudio.com.ve/tasa", headers=headers, timeout=10)
        if r2.status_code == 200:
            tasas = r2.json().get("tasas", {})
            usd = round(float(tasas["USD"]), 4)
            eur = round(float(tasas["EUR"]), 4)
            if usd > 0 and eur > 0:
                return {"usd": usd, "eur": eur}
    except Exception as e:
        print(f"Error obteniendo BCV en todas las fuentes: {e}")

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
            "transAmount": "30000",
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
