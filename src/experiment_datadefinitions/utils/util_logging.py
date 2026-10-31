import asyncio
import logging
import sys
import threading

from nicegui import ui

logger = logging.getLogger(__name__)


def init_logging() -> None:
    # or run with PYTHONASYNCIODEBUG=1
    asyncio.get_running_loop().set_debug(True)

    if False:

        def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
            logger.error(
                "thread %s crashed",
                args.thread.name if args.thread else "?",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),  # type: ignore[arg-type]
            )

        threading.excepthook = _thread_excepthook
        sys.excepthook = lambda *a: logger.error("uncaught", exc_info=a)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger("asyncio").setLevel(logging.DEBUG)


class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log, level: int = logging.NOTSET) -> None:
        self.element = element
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)

            def color_style() -> str:
                for levelno, color in (
                    (logging.ERROR, "text-red"),
                    (logging.WARNING, "text-orange"),
                    (logging.INFO, "text-blue"),
                ):
                    if record.levelno >= levelno:
                        return color
                return "text-gray"

            self.element.push(line=msg, classes=color_style())
        except Exception:
            self.handleError(record)
