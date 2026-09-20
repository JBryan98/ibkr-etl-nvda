import logging
import threading
from datetime import datetime

from ibapi.contract import Contract

from IBKRApi import IBKRApi
from ohlcv_repository import save_ohlcv

logger = logging.getLogger(__name__)

def ohlcv_etl(connection, time_from: datetime, time_to: datetime):
    symbols = ["NVDA", "SOXQ"]
    app = IBKRApi()
    app.connect("127.0.0.1",4002,99)
    threading.Thread(target=app.run,daemon=True).start()
    try:
        if not app.connected_event.wait(timeout=60):
            raise TimeoutError("Tiempo de espera agotado, no se pudo conectar a la API de IBKR")
        req_id = 1
        for symbol in symbols:
            symbol_contract = get_contract(symbol)
            app.get_historical_data(req_id, time_from, time_to, symbol_contract)
            req_id += 1
        if not app.data:
            logger.info("No se recibieron datos históricos de IBKR para el rango %s - %s",time_from,time_to)
            return 0
        total_rows_inserted = save_ohlcv(connection,app.data)
        return total_rows_inserted
    finally:
        app.disconnect()

def get_contract(symbol: str) -> Contract:
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.primaryExchange = "NASDAQ"
    contract.exchange = "SMART"
    contract.currency = "USD"
    return contract