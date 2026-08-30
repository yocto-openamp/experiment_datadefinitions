import logging

from utils_observer.util_message import Message
from utils_observer.util_observer import Observer, Registration

logger = logging.getLogger(__file__)


def logger_sink(observer: Observer) -> None:

    def observer_callback(message: Message) -> None:
        logger.info(f"{message.verb.name}({message.topic}, {message.topic_value})")

    observer.register_as_observer(
        registration=Registration(
            topic="/",
            callback=observer_callback,
        )
    )
