def get_binance_p2p_rates():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True, 
            "page": 1,
            "rows": 10,
            "transAmount": "1000", # Filtro de 1000 bolívares como en tu foto
            "publisherType": "merchant",
            "tradeType": "BUY"
        }
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        
        # Obtenemos todos los precios de la lista
        all_prices = [float(adv['adv']['price']) for adv in data['data']]
        
        # Lógica solicitada: Ignorar el 1ro, tomar 2do, 3ro y 4to
        # En Python los índices empiezan en 0, así que:
        # [0] es el 1ro, [1] el 2do, [2] el 3ro, [3] el 4to.
        if len(all_prices) >= 4:
            seleccionados = all_prices[1:4] # Esto toma los índices 1, 2 y 3
            promedio = sum(seleccionados) / len(seleccionados)
            return round(promedio, 2)
        elif len(all_prices) > 0:
            # Si por alguna razón hay menos de 4, promediamos lo que haya
            return round(sum(all_prices) / len(all_prices), 2)
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo Binance: {e}")
        return None



