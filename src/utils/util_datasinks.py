import logging

from . import util_observer

logger = logging.getLogger(__file__)


def logger_sink(observer: util_observer.Observer) -> None:

    def observer_callback(message: util_observer.Message) -> None:
        logger.info(f"{message.verb.name}({message.topic}, {message.topic_value})")

    observer.register_as_observer(
        registration=util_observer.Registration(
            topic="/",
            callback=observer_callback,
        )
    )
