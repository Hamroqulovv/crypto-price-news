import requests
import logging
from datetime import datetime, timedelta
import os



COINBASE_BASE_URL = os.getenv("COINBASE_BASE_URL")

logger = logging.getLogger(__name__)

# Cache for exchange rates (30 seconds - real-time)
_rate_cache = {
    "uzs": {"rate": 12850, "updated": None},
    "rub": {"rate": 95, "updated": None}
}

def get_real_prices(coins):
    """
    Kripto narxlarini olish - Coinbase va boshqa ishonchli manbalardan
    Juda past narxlarni ham to'g'ri ko'rsatadi
    """
    results = []
    
    # Real valyuta kurslarini yangilash
    usd_to_uzs = get_uzs_rate()
    usd_to_rub = get_rub_rate()
    
    logger.info(f"📊 Kurslar: 1 USD = {usd_to_uzs} UZS, {usd_to_rub} RUB")
    
    for coin in coins:
        coin = coin.upper().strip()
        price_data = None
        source = None
        
        # 1. COINBASE (USD va RUB) - eng ishonchli
        price_data, source = get_from_coinbase(coin)
        
        # 2. COINMARKETCAP (ikkinchi tanlov) - API kalit bilan
        if not price_data:
            price_data, source = get_from_coinmarketcap(coin)
            if price_data:
                price_data = {"usd": price_data, "rub": None}
        
        # 3. BINANCE (uchinchi tanlov)
        if not price_data:
            price_data, source = get_from_binance(coin)
            if price_data:
                price_data = {"usd": price_data, "rub": None}
        
        # 4. COINGECKO (fallback)
        if not price_data:
            price_data, source = get_from_coingecko(coin)
            if price_data:
                price_data = {"usd": price_data, "rub": None}
        
        if price_data and price_data["usd"] and price_data["usd"] > 0:
            price_usd = price_data["usd"]
            
            # RUB: Coinbase'dan yoki hisoblash
            price_rub = price_data.get("rub")
            if not price_rub:
                price_rub = price_usd * usd_to_rub
            
            # Juda past narxlar uchun maxsus formatting
            # Agar narx 0.01 dan kichik bo'lsa, ko'proq raqam ko'rsatamiz
            usd_precision = 8 if price_usd < 0.01 else 4
            
            results.append({
                "usd": price_usd,  # Raw qiymat
                "usd_formatted": f"{price_usd:.{usd_precision}f}",  # Formatted string
                "uzs": round(price_usd * usd_to_uzs, 2),
                "rub": round(price_rub, 4),  # RUB uchun ham 4 raqam
                "source": source
            })
            logger.info(f"✅ {coin}: ${price_usd:.8f} ({source})")
        else:
            logger.error(f"❌ {coin}: topilmadi")
            results.append(None)
    
    return results


def get_from_coinbase(coin):
    """
    Coinbase Spot Price API - USD, RUB va boshqa valyutalarda
    https://api.coinbase.com/v2/prices/{coin}-USD/spot
    """
    try:
        # USD narxini olamiz
        url_usd = f"{COINBASE_BASE_URL}/{coin}-USD/spot"
        response_usd = requests.get(url_usd, timeout=10)
        
        if response_usd.status_code == 200:
            data_usd = response_usd.json()
            
            if "data" in data_usd and "amount" in data_usd["data"]:
                price_usd = float(data_usd["data"]["amount"])
                
                if price_usd > 0:
                    # RUB narxini ham olamiz (Coinbase'ning o'z kursi)
                    price_rub = None
                    try:
                        url_rub = f"{COINBASE_BASE_URL}/{coin}-RUB/spot"
                        response_rub = requests.get(url_rub, timeout=5)
                        if response_rub.status_code == 200:
                            data_rub = response_rub.json()
                            if "data" in data_rub and "amount" in data_rub["data"]:
                                price_rub = float(data_rub["data"]["amount"])
                    except:
                        pass
                    
                    return {"usd": price_usd, "rub": price_rub}, "Coinbase"
        
    except Exception as e:
        logger.debug(f"Coinbase error for {coin}: {e}")
    
    return None, None


def get_from_coinmarketcap(coin):
    """
    CoinMarketCap API - ikkinchi tanlov (CoinGecko o'rniga)
    """
    try:
        # Check for API key
        COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
        if not COINMARKETCAP_API_KEY:
            logger.debug("CoinMarketCap API key not found in environment variables")
            return None, None
        
        # Kriptovalyuta symbol mapping
        # Ba'zi tokenlar uchun symbol mapping kerak
        SYMBOL_MAPPING = {
            "NOT": "NOT",      # Notcoin
            "POLY": "MATIC",   # Polygon (MATIC)
            "RENDER": "RNDR",  # Render Token
            "TON": "TON",      # The Open Network
            "BTC": "BTC",
            "ETH": "ETH", 
            "SOL": "SOL",
            "DOGE": "DOGE",
            "XRP": "XRP",
            "ADA": "ADA",
            "BNB": "BNB",
            "USDT": "USDT",
            "USDC": "USDC",
            "SHIB": "SHIB",
            "TRX": "TRX",
            "DOT": "DOT",
            "MATIC": "MATIC",
            "LINK": "LINK",
            "UNI": "UNI",
            "LTC": "LTC",
            "BCH": "BCH",
            "AVAX": "AVAX",
            "XLM": "XLM",
            "ATOM": "ATOM",
            "ETC": "ETC",
            "FIL": "FIL",
            "HBAR": "HBAR",
            "VET": "VET",
            "ALGO": "ALGO",
            "ICP": "ICP",
            "NEAR": "NEAR",
            "APT": "APT",
            "SUI": "SUI",
            "ARB": "ARB",
            "OP": "OP",
            "PEPE": "PEPE",
            "WLD": "WLD",
            "JUP": "JUP",
            "BONK": "BONK",
            "WIF": "WIF",
            "PYTH": "PYTH",
            "FLOKI": "FLOKI",
            "RUNE": "RUNE",
            "GRT": "GRT",
            "IMX": "IMX",
            "INJ": "INJ",
            "TIA": "TIA",
            "SEI": "SEI",
            "FET": "FET",
            "SAND": "SAND",
            "MANA": "MANA",
            "AXS": "AXS",
            "XMR": "XMR",
            "STX": "STX",
        }
        
        # Symbol mapping or original symbol
        symbol = SYMBOL_MAPPING.get(coin, coin)
        
        # CoinMarketCap API endpoint
        COINMARKETCAP_URL = os.getenv("COINMARKETCAP_URL")
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }
        params = {
            'symbol': symbol,
            'convert': 'USD'
        }
        
        logger.debug(f"CoinMarketCap: Requesting price for {coin} (symbol: {symbol})")
        
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug uchun ma'lumot
            logger.debug(f"CoinMarketCap response status: {response.status_code}")
            
            # Check if data exists
            if 'data' in data and symbol in data['data']:
                coin_data = data['data'][symbol]
                
                # Har doim birinchi elementni olish
                if isinstance(coin_data, list) and len(coin_data) > 0:
                    coin_info = coin_data[0]
                    
                    if 'quote' in coin_info and 'USD' in coin_info['quote']:
                        price = coin_info['quote']['USD'].get('price')
                        
                        if price is not None and price > 0:
                            logger.info(f"✅ CoinMarketCap: {coin} narxi: ${price}")
                            return float(price), "CoinMarketCap"
                        else:
                            logger.debug(f"CoinMarketCap: {coin} uchun narx topilmadi yoki 0")
            
            # Agar symbol mapping bilan topilmasa, original symbol bilan urinib ko'ramiz
            if symbol != coin:
                logger.debug(f"CoinMarketCap: {symbol} bilan topilmadi, {coin} bilan urinib ko'ramiz")
                params['symbol'] = coin
                response = requests.get(COINMARKETCAP_URL, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and coin in data['data']:
                        coin_data = data['data'][coin]
                        
                        if isinstance(coin_data, list) and len(coin_data) > 0:
                            coin_info = coin_data[0]
                            
                            if 'quote' in coin_info and 'USD' in coin_info['quote']:
                                price = coin_info['quote']['USD'].get('price')
                                
                                if price is not None and price > 0:
                                    logger.info(f"✅ CoinMarketCap: {coin} narxi: ${price}")
                                    return float(price), "CoinMarketCap"
        
        elif response.status_code == 400:
            logger.debug(f"CoinMarketCap: Symbol {symbol} not found (400 error)")
        elif response.status_code == 401:
            logger.warning("CoinMarketCap: Invalid API key (401 error)")
        elif response.status_code == 429:
            logger.debug("CoinMarketCap: Rate limit exceeded (429 error)")
        elif response.status_code == 404:
            logger.debug(f"CoinMarketCap: {symbol} not found (404 error)")
        else:
            logger.debug(f"CoinMarketCap: Unexpected status code {response.status_code}")
        
    except requests.exceptions.Timeout:
        logger.debug(f"CoinMarketCap timeout for {coin}")
    except requests.exceptions.RequestException as e:
        logger.debug(f"CoinMarketCap request error for {coin}: {e}")
    except Exception as e:
        logger.debug(f"CoinMarketCap error for {coin}: {e}")
    
    return None, None


def get_from_binance(coin):
    """
    Binance Spot API - global bozor narxlari
    """
    try:
        BINANCE_URL = os.getenv("BINANCE_URL")

        symbol = f"{coin}USDT"
        
        response = requests.get(BINANCE_URL, params={"symbol": symbol}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data.get("price", 0))
            if price > 0:
                return price, "Binance"
        
    except Exception as e:
        logger.debug(f"Binance error for {coin}: {e}")
    
    return None, None


def get_from_coingecko(coin):
    """
    CoinGecko API - fallback manba
    """
    
    # Coinlarning CoinGecko ID mapping
    COIN_IDS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "POLY": "matic-network",
        "TRX": "tron",
        "TON": "the-open-network",
        "NOT": "notcoin",
        "USDT": "tether",
        "USDC": "usd-coin",
        "SHIB": "shiba-inu",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "PEPE": "pepe",
        "ARB": "arbitrum",
        "OP": "optimism",
        "NEAR": "near",
        "APT": "aptos",
        "SUI": "sui",
        "STX": "blockstack",
        "INJ": "injective-protocol",
        "TIA": "celestia",
        "SEI": "sei-network",
        "FET": "fetch-ai",
        "RENDER": "render-token",
        "RNDR": "render-token",
        "GRT": "the-graph",
        "IMX": "immutable-x",
        "RUNE": "thorchain",
        "ATOM": "cosmos",
        "FIL": "filecoin",
        "HBAR": "hedera-hashgraph",
        "VET": "vechain",
        "ALGO": "algorand",
        "ICP": "internet-computer",
        "SAND": "the-sandbox",
        "MANA": "decentraland",
        "AXS": "axie-infinity",
        "XLM": "stellar",
        "XMR": "monero",
        "ETC": "ethereum-classic",
        "WLD": "worldcoin-wld",
        "JUP": "jupiter-exchange-solana",
        "BONK": "bonk",
        "WIF": "dogwifcoin",
        "PYTH": "pyth-network",
        "FLOKI": "floki",
    }
    
    coin_id = COIN_IDS.get(coin, coin.lower())
    
    try:
        COINGECKO_URL = os.getenv("COINGECKO_URL")

        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "false"
        }

        response = requests.get(COINGECKO_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            
            if coin_id in data and "usd" in data[coin_id]:
                price = float(data[coin_id]["usd"])
                if price > 0:
                    return price, "CoinGecko"
        
    except Exception as e:
        logger.debug(f"CoinGecko error for {coin}: {e}")
    
    return None, None


def get_uzs_rate():
    """
    Real-time USD → UZS kursi (O'zbekiston Markaziy Banki)
    Cache: 30 soniya (har 30 soniyada yangilanadi - REAL-TIME)
    """
    global _rate_cache
    
    now = datetime.now()
    cache = _rate_cache["uzs"]
    
    # Cache mavjud va 30 soniyadan kam bo'lsa
    if cache["updated"] and (now - cache["updated"]) < timedelta(seconds=30):
        return cache["rate"]
    
    try:
        # CBU rasmiy API
        UZS_RATE_URL = os.getenv("UZS_RATE_URL")
        response = requests.get(UZS_RATE_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for currency in data:
                if currency.get("Ccy") == "USD":
                    rate = float(currency.get("Rate", 12850))
                    
                    # Cache'ni yangilash
                    _rate_cache["uzs"] = {"rate": rate, "updated": now}
                    logger.info(f"✅ UZS kurs yangilandi: {rate}")
                    return rate
    
    except Exception as e:
        logger.warning(f"UZS kurs olishda xato: {e}")
    
    # Default qiymat
    return cache["rate"]


def get_rub_rate():
    """
    Real-time USD → RUB kursi (Rossiya Markaziy Banki)
    Cache: 30 soniya (har 30 soniyada yangilanadi - REAL-TIME)
    """
    global _rate_cache
    
    now = datetime.now()
    cache = _rate_cache["rub"]
    
    # Cache mavjud va 30 soniyadan kam bo'lsa
    if cache["updated"] and (now - cache["updated"]) < timedelta(seconds=30):
        return cache["rate"]
    
    try:
        # CBR rasmiy API
        RUB_RATE_URL = os.getenv("RUB_RATE_URL")
        response = requests.get(RUB_RATE_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "Valute" in data and "USD" in data["Valute"]:
                rate = float(data["Valute"]["USD"]["Value"])
                
                # Cache'ni yangilash
                _rate_cache["rub"] = {"rate": rate, "updated": now}
                logger.info(f"✅ RUB kurs yangilandi: {rate}")
                return rate
    
    except Exception as e:
        logger.warning(f"RUB kurs olishda xato: {e}")
    
    # Default qiymat
    return cache["rate"]


# TEST FUNCTION
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("🚀 CRYPTO PRICE CHECKER - MULTI-SOURCE INTEGRATION")
    print("="*60)
    
    # Check if CoinMarketCap API key is available
    cmc_api_key = os.environ.get('COINMARKETCAP_API_KEY')
    if cmc_api_key:
        print(f"✅ CoinMarketCap API key found: {cmc_api_key[:10]}...")
    else:
        print("⚠️  CoinMarketCap API key not found in environment variables")
        print("   Set it with: export COINMARKETCAP_API_KEY='your-api-key'")
        print("   Yoki python kodida: os.environ['COINMARKETCAP_API_KEY'] = 'your-key'")
    
    # Test coinlar
    test_coins = ["BTC", "ETH", "SOL", "TON", "DOGE", "NOT", "SHIB"]
    
    print(f"\n🔍 Testing {len(test_coins)} coins...\n")
    print("Ketma-ketlik: 1. Coinbase → 2. CoinMarketCap → 3. Binance → 4. CoinGecko")
    print()
    
    results = get_real_prices(test_coins)
    
    print("\n" + "="*60)
    print("📊 NATIJALAR:")
    print("="*60 + "\n")
    
    for i, coin in enumerate(test_coins):
        if results[i]:
            r = results[i]
            print(f"💰 {coin} ({r.get('source', 'Unknown')})")
            print(f"   💵 USD: ${r['usd']:,.8f}")
            print(f"   🇺🇿 UZS: {r['uzs']:,} so'm")
            print(f"   🇷🇺 RUB: {r['rub']:,.2f} ₽")
            print()
        else:
            print(f"❌ {coin}: TOPILMADI\n")
    
    print("="*60)