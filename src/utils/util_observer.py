from __future__ import annotations

import asyncio
import dataclasses
import enum
import logging
import random
import typing

logger = logging.getLogger(__file__)


class EnumMessageVerb(enum.IntEnum):
    REGISTER = 1
    SET_REQUEST = 2
    NOTIFY = 3


@dataclasses.dataclass(frozen=True)
class Message:
    topic: str
    """
    Example: /uart/aligna5/status
    """

    verb: EnumMessageVerb
    """
    Example: REGISTER/SET_REQUEST/NOTIFY
    """

    topic_value: typing.Any
    """
    All topic_value for the same topic are required to be of the same type.
    """


class EnumItemQuality(enum.StrEnum):
    UNKNOWN = "unknown"
    KNOWN = "known"
    IN_TRANSITION = "intransition"


@dataclasses.dataclass(slots=True)
class ObservableItem:
    topic: str
    topic_value: typing.Any
    quality: EnumItemQuality

    @property
    def quality_text(self) -> str:
        return self.quality.value


class Observer:
    def __init__(self) -> None:
        self.items: dict[str, ObservableItem] = {}
        self.observer_callbacks: list[typing.Callable] = []
        self.notify_active = 0

    def register_observer_callback(
        self,
        callback: typing.Callable[[Message], None],
    ) -> None:
        self.observer_callbacks.append(callback)

    def register_with_value(self, message: Message) -> None:
        print(f"register_with_value({message.topic}, {message.topic_value}")
        if message.topic in self.items:
            logger.error(f"Already registered in observer: {message.topic}")
            return
        self.items[message.topic] = ObservableItem(
            topic=message.topic,
            topic_value=message.topic_value,
            quality=EnumItemQuality.UNKNOWN,
        )

    def get_item(self, topic: str) -> ObservableItem:
        item = self.items.get(topic)
        assert item is not None
        return item

    async def set_quality_known(self, quality_int: int) -> None:
        quality = EnumItemQuality.KNOWN if quality_int else EnumItemQuality.UNKNOWN
        items = list(self.items.values())
        random.shuffle(items)
        for item in items:
            item.quality = quality
            await asyncio.sleep(0.2)

    async def set_request(self, message: Message) -> typing.Any:
        """
        Returns the value which has been set.
        """
        logger.info(f"set_request({message.topic}, {message.topic_value})")
        item = self.get_item(topic=message.topic)
        # .value = value
        item.quality = EnumItemQuality.IN_TRANSITION
        self.notify_active += 1
        try:
            await asyncio.sleep(2)
        finally:
            self.notify_active -= 1
        if self.notify_active > 0:
            # Avoid cycling
            return
        self.notify(
            Message(
                topic=message.topic,
                verb=EnumMessageVerb.NOTIFY,
                topic_value=message.topic_value,
            )
        )
        return message.topic_value

    def notify(self, message: Message) -> None:
        logger.info(f"notify({message.topic}, {message.topic_value})")
        self.notify_active += 1
        try:
            item = self.get_item(topic=message.topic)
            if item.topic_value != message.topic_value:
                item.topic_value = message.topic_value
            item.quality = EnumItemQuality.KNOWN

            for callback in self.observer_callbacks:
                try:
                    callback(path=message.topic, value=message.topic_value)
                except Exception as e:
                    logger.exception(msg="callback failed", exc_info=e)
        finally:
            self.notify_active -= 1
