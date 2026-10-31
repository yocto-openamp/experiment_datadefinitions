from __future__ import annotations

import asyncio
import dataclasses
import enum
import logging
import random
import typing

from .util_message import Message, MessageVerb

logger = logging.getLogger(__file__)


class ItemQuality(enum.StrEnum):
    UNKNOWN = "unknown"
    KNOWN = "known"
    IN_TRANSITION = "intransition"


@dataclasses.dataclass(slots=True)
class ObservableItem:
    topic: str
    topic_value: typing.Any
    quality: ItemQuality

    @property
    def quality_text(self) -> str:
        return self.quality.value


@dataclasses.dataclass(frozen=True)
class Registration:
    topic: str
    """
    Example: "/uart", "/m7"

    If we are "/uart", we only will get notifications from "/m7".
    If we are "", we will get notifications from everywhere.
    """

    callback: typing.Callable[[Message], None]


class Observer:
    def __init__(self) -> None:
        self.items: dict[str, ObservableItem] = {}
        """
        Key: topic
        """

        self.observer_registrations: list[Registration] = []

    def register_as_observer(
        self,
        registration: Registration,
    ) -> None:
        assert isinstance(registration, Registration)
        assert isinstance(registration.topic, str)

        self.observer_registrations.append(registration)

    def get_item(self, topic: str) -> ObservableItem:
        item = self.items.get(topic)
        assert item is not None
        return item

    async def set_quality_known(self, quality_int: int) -> None:
        """
        For demo purpose: set the all items to KNOWN randomly
        """
        quality = ItemQuality.KNOWN if quality_int else ItemQuality.UNKNOWN
        items = list(self.items.values())
        random.shuffle(items)
        for item in items:
            item.quality = quality
            await asyncio.sleep(0.2)

    def send_message(self, message: Message) -> None:
        assert isinstance(message, Message)
        assert isinstance(message.verb, MessageVerb)
        assert isinstance(message.topic, str)

        if message.verb == MessageVerb.SET_REQUEST:
            self._set_request(message=message)
            self._call_callbacks(message=message)
            return

        if message.verb == MessageVerb.REGISTER:
            self._register_topic(message=message)
            self._call_callbacks(message=message)
            return

        if message.verb == MessageVerb.NOTIFY:
            self._notify(message=message)
            self._call_callbacks(message=message)
            return

        raise ValueError(f"Unknown Verb {message.verb}!")

    def _register_topic(self, message: Message) -> None:
        msg = f"register_topic({message.topic}, {message.topic_value})"
        logger.info(msg)
        if message.topic in self.items:
            logger.error(f"{msg}: Already registered!")
            return

        self.items[message.topic] = ObservableItem(
            topic=message.topic,
            topic_value=message.topic_value,
            quality=ItemQuality.UNKNOWN,
        )

    def _set_request(self, message: Message) -> None:
        """
        Returns the value which has been set.
        """
        # logger.debug(f"set_request({message.topic}, {message.topic_value})")
        item = self.get_item(topic=message.topic)
        item.quality = ItemQuality.IN_TRANSITION

    def _notify(self, message: Message) -> None:
        # logger.debug(f"notify({message.topic}, {message.topic_value})")
        item = self.get_item(topic=message.topic)
        if item.topic_value != message.topic_value:
            item.topic_value = message.topic_value
        item.quality = ItemQuality.KNOWN

    def _call_callbacks(self, message: Message) -> None:
        for registration in self.observer_registrations:
            assert isinstance(registration, Registration)
            try:
                # if message.verb == EnumMessageVerb.NOTIFY:
                #     if message.topic.startswith(registration.topic):
                #         # Do not send back the notification to the source
                #         continue
                registration.callback(message)
            except Exception as e:
                logger.exception(msg="callback failed", exc_info=e)

    def get_queue(self, topic: str = "/") -> asyncio.Queue[Message]:
        """
        Convenience method for a queue interface.
        """
        queue = asyncio.Queue[Message]()

        def observer_callback(message: Message) -> None:
            queue.put_nowait(message)

        self.register_as_observer(
            registration=Registration(
                topic=topic,
                callback=observer_callback,
            )
        )
        return queue
