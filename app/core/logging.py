# app/core/logging.py
import sys
import logging
import structlog
from app.core.config import settings

# Statik servis adını eklemek için özel processor
def add_service_name(logger, method_name, event_dict):
    event_dict["service"] = settings.PROJECT_NAME
    return event_dict

def setup_logging():
    """
    Sentiric Governance standartlarına uygun, ortama duyarlı loglama kurar.
    Geliştirme: Renkli, insan odaklı konsol logları.
    Üretim: Makine tarafından işlenebilir JSON logları.
    """
    log_level = settings.LOG_LEVEL.upper()

    # Python'ın standart logging sistemini temel al
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Tüm loglarda bulunacak ortak işlemciler
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_service_name,  # <- BURASI GÜNCEL
    ]

    # Ortama göre son işlemciyi (renderer) seç
    if settings.ENV == "development":
        # Geliştirme ortamı için renkli log
        final_processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Üretim ortamı için JSON log
        final_processor = structlog.processors.JSONRenderer()

    # Tam işlemci zincirini oluştur
    processors = shared_processors + [final_processor]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Uygulama başlangıcında loglamayı kur
setup_logging()

# Uygulama boyunca kullanılacak logger nesnesi
logger = structlog.get_logger("sentiric_knowledge_service")
