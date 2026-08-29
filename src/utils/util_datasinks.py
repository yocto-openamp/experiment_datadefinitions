import logging

from . import util_observer

logger = logging.getLogger(__file__)


def logger_sink(observer: util_observer.Observer) -> None:

    def observer_callback(message: util_observer.Message) -> None:
        logger.info(f"{message.verb}({message.topic}, {message.topic_value})")

    observer.register_observer_callback(callback=observer_callback)
