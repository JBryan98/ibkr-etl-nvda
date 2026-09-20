import logging
from datetime import datetime, timezone

from database import get_connection
from etl import ohlcv_etl
from etl_metadata_repository import get_last_successful_run, create_etl_run, mark_etl_success, mark_etl_failure

logger = logging.getLogger(__name__)

def run_ohlcv_scheduler():
    logger.info("Inicializando workflow")
    with get_connection() as conn:
        last_run = get_last_successful_run(conn)
        time_from = last_run["time_to"]
        # El script esta planeado ejecutarse a partir de las 9pm UTC que representa 5pm NY y 4pm para Perú
        time_to = datetime.now(timezone.utc)

        run_id = create_etl_run(
            conn,
            time_from,
            time_to
        )

        conn.commit()

        try:
            total_ohlcv_inserted = ohlcv_etl(
                conn,
                time_from,
                time_to
            )
            mark_etl_success(conn, run_id, total_ohlcv_inserted)
            conn.commit()
            logger.info("Workflow finalizado con éxito")
        except Exception as e:
            # 1. Si ocurre un error durante el ETL, se hace rollback de la transacción y se registrar el error en la tabla etl_metadata
            conn.rollback()
            logger.info("Error en el workflow, aplicando rollback %s", str(e))

            # 2. Registrar la falla en los metadatos y asegurar el commit de la transacción para que el estado de la ejecución quede registrado
            try:
                mark_etl_failure(conn, run_id, str(e))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error("No se pudo actualizar el estado FAILED del registro %s en la tabla etl_metadata: %s", run_id, str(e))
            raise
