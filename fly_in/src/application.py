from __future__ import annotations
import pygame as pg
from fly_in.src.utils import Mode
from fly_in.src.parser import ParsingException, MultipleParsingExceptions
from fly_in.src.rendering.renderer import Renderer, RenderException
from fly_in.src.rendering.pngButton import PNGButton


class ApplicationException(Exception):
    """Exception raised when the application cannot continue."""

    def __init__(cls, msg: str = ""):
        """Initialize an application-level exception.

        Args:
            msg (str, optional): Error message. Defaults to "".
        """
        cls.msg = msg
        super().__init__(msg)

    def __str__(cls) -> str:
        """Return the exception message."""
        return cls.msg


class Application:
    """Coordinate the pygame event loop and renderer."""

    MODE: Mode = Mode.NONE
    __running = False
    __renderer: Renderer

    @classmethod
    def run(cls) -> None:
        """Initialize and run the pygame application loop.

        Raises:
            ApplicationException: If rendering or event handling fails.
        """
        cls.MODE = Mode.MENU
        try:
            cls.__renderer = Renderer()
            cls._change_mode(cls.MODE)
        except RenderException as e:
            raise ApplicationException(str(e))
        # application loop
        cls.__running = True
        while cls.__running:
            events = pg.event.get()
            try:
                cls._handle_events(events)
                cls.__renderer._update(cls.MODE)
                cls.__renderer._draw(cls.MODE)
                cls.__renderer.update_frame()
            except RenderException as e:
                raise ApplicationException(str(e))
        pg.quit()

    @classmethod
    def _handle_events(cls, events: list[pg.event.Event]) -> None:
        """Process window, keyboard, and active-button events.

        Args:
            events (list): Pygame events to process.
        """
        for event in events:
            if event.type == pg.QUIT:
                cls.__running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    cls.__running = False
        # click su bottoni attivi
        btn: PNGButton
        for btn in cls.__renderer.get_active_buttons():
            if btn.is_clicked(events):
                try:
                    cls._click(btn.name)
                    break
                except ApplicationException:
                    cls.__running = False

    @classmethod
    def _click(cls, event_name: str) -> None:
        """Apply the action represented by a clicked button.

        Args:
            event_name (str): Name of the clicked button.
        """
        _btn_names = [sp.name for sp in cls.__renderer.get_active_buttons()]
        try:
            if event_name in ["maps", "about"]:
                cls._change_mode(Mode.get(event_name))
            elif event_name == "back":
                cls._change_mode(cls.MODE.get_back())
            elif event_name == "quit":
                cls.__running = False
                return
            elif (
                cls.MODE == Mode.MAPS
                and event_name in set(_btn_names) - {"back"}
            ):
                cls._change_mode(Mode.LEVELS, event_name)
            elif (
                  cls.MODE == Mode.LEVELS
                  and event_name in set(_btn_names) - {"back"}
                 ):
                cls._change_mode(Mode.FLYING, event_name)
        except ApplicationException:
            raise ApplicationException("_click")

    @classmethod
    def _change_mode(cls, new_mode: Mode, clicked: str = "") -> None:
        """Switch the renderer to a new application mode.

        Args:
            new_mode (Mode): Mode to render.
            clicked (str, optional): Selected map or level name.
                Defaults to "".
        """
        cls.MODE = new_mode
        try:
            cls.__renderer.render_mode(cls.MODE, clicked)
        except (RenderException, ParsingException, MultipleParsingExceptions):
            raise ApplicationException("change_mode")
