from __future__ import annotations

import dataclasses
import enum
import logging
import typing

logger = logging.getLogger(__file__)


class MessageVerb(enum.IntEnum):
    REGISTER = 1
    SET_REQUEST = 2
    NOTIFY = 3


@dataclasses.dataclass(frozen=True)
class Message:
    topic: str
    """
    Example: /uart/aligna5/status
    """

    verb: MessageVerb
    """
    Example: REGISTER/SET_REQUEST/NOTIFY
    """

    topic_value: typing.Any
    """
    All topic_value for the same topic are required to be of the same type.
    """
