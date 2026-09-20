import logging
import threading

import time
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from ibapi import contract
from ibapi.client import EClient
from ibapi.common import BarData
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper

logger = logging.getLogger(__name__)

class IBKRApi(EClient, EWrapper):
    def __init__(self) -> None:
        EClient.__init__(self, self)
        self.data: list[dict] = []
        self.contracts: dict[int, Contract] = {}
        self.request_events: dict[int, threading.Event] = {}
        self.connected_event = threading.Event()

    def nextValidId(self, orderId: int):
        logger.info("Conexión API establecida. nextValidId=%s",orderId)
        self.connected_event.set()

    def error(self, reqId: int, errorCode: int, *args):
        logger.error("Error: reqId=%s, errorCode=%s, details=%s", reqId, errorCode, args)


    def get_historical_data(self, reqId: int, time_from: datetime, time_to: datetime, current_contract: Contract):
        self.contracts[reqId] = current_contract
        self.request_events[reqId] = threading.Event()
        # 1. Calculamos cuánto días hay exactamente entre el checkpoint y el momento actual
        delta_days = (time_to - time_from).days
        # Le damos un margen de seguridad sumando 1 o asegurando al menos 1 día
        duration_days = max(delta_days, 1) + 1
        duration_str = f"{duration_days} D"

        ny_time = time_to.astimezone(ZoneInfo("America/New_York"))
        end_date_str = ny_time.strftime("%Y%m%d %H:%M:%S") + " America/New_York"

        logger.info("Solicitando a IBKR desde %s hasta %s (Duración: %s)", time_from, end_date_str, duration_str)
        self.reqHistoricalData(
            reqId=reqId,
            contract=current_contract,
            endDateTime=end_date_str,
            durationStr=duration_str, # Tomar en cuenta que solo toma en cuenta lunes a viernes, no fines de semana
            barSizeSetting="1 hour",
            whatToShow="TRADES",
            useRTH=1,
            formatDate=2, # Retornará fechas en UTC
            keepUpToDate=False,
            chartOptions=[]
        )
        event = self.request_events[reqId]
        if not event.wait(timeout=60):
            raise TimeoutError(f"Timeout esperando datos históricos para {current_contract.symbol}")

    # Callback que se llama cuando se recibe un dato histórico
    def historicalData(self, reqId: int, bar: BarData):
        current_contract = self.contracts[reqId]
        bar_dict = {
            "symbol": current_contract.symbol,
            "timeframe": "intraday",
            "date": datetime.fromtimestamp(int(bar.date), tz = timezone.utc),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        }
        logger.info("Recibido dato histórico: %s", bar_dict)
        self.data.append(bar_dict)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        logger.info(
            "Descarga finalizada. reqId=%s, start=%s, end=%s",
            reqId,
            start,
            end
        )
        event = self.request_events.get(reqId)
        if event:
            event.set()

