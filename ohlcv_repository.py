from psycopg2.extras import execute_values, RealDictCursor


def save_ohlcv(connection, data):
    query = """
INSERT INTO ohlcv (
            symbol,
            timeframe,
            date,
            open,
            high,
            low,
            close,
            volume
        )
        VALUES %s
        ON CONFLICT (symbol, timeframe, date) DO NOTHING
    """

    values = [
        (
            ohlcv["symbol"],
            ohlcv["timeframe"],
            ohlcv["date"],
            ohlcv["open"],
            ohlcv["high"],
            ohlcv["low"],
            ohlcv["close"],
            ohlcv["volume"]
        )
        for ohlcv in data
    ]

    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        execute_values(
            cursor,
            query,
            values
        )
        return cursor.rowcount