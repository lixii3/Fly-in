from __future__ import annotations
from enum import Enum


class FlyInException(Exception):
    """Base exception for Fly-in application errors."""

    def __init__(self, msg: str) -> None:
        """Initialize a base application exception.

        Args:
            msg (str): Error message.
        """
        self.msg = msg

    def __str__(self) -> str:
        """Return the formatted exception message."""
        return f"FlyInException: {self.msg}"


class Tag(Enum):
    """Tags identifying map declarations."""

    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"

    @classmethod
    def get(cls, tag: str) -> "Tag" | None:
        """Convert a tag string to a tag enum member.

        Args:
            tag (str): Tag name to look up.

        Returns:
            Tag | None: Matching member, or None when unknown.
        """
        return cls.__members__.get(tag.upper())


class ZoneType(Enum):
    """Movement-cost categories for zones."""

    NORMAL = 1
    RESTRICTED = 2
    PRIORITY = 0.9999
    BLOCKED = 99999999999999

    @classmethod
    def get(cls, zone: str) -> "ZoneType" | None:
        """Convert a zone type string to an enum member.

        Args:
            zone (str): Zone type name to look up.

        Returns:
            ZoneType | None: Matching member, or None when unknown.
        """
        return cls.__members__.get(zone.upper())

    def getName(self) -> str:
        """Return the lower-case name used by rendering resources."""
        return self.name.lower()


class ParsingColors(Enum):
    """Colors accepted in map metadata."""

    RED = "#FF0000"
    MAGENTA = "#FF00FF"
    GREEN = "#008000"
    LIME = "#00FF00"
    BLUE = "#0000FF"
    CYAN = "#00B7FF"
    PURPLE = "#2E2BFA"
    YELLOW = "#FFFF00"
    GOLD = "#FFD700"
    ORANGE = "#FFA500"
    BROWN = "#A52A2A"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    PINK = "#E994D7"

    @classmethod
    def get(cls, color: str) -> "ParsingColors":
        """Convert a color name to an enum member.

        Args:
            color (str): Color name to look up.

        Returns:
            ParsingColors: Matching color, or white when unknown.
        """
        return cls.__members__.get(color.upper(), ParsingColors.WHITE)


class Mode(Enum):
    """Screens available in the application UI."""

    NONE = None
    MENU = "menu"
    MAPS = "maps"
    ABOUT = "about"
    LEVELS = "levels"
    FLYING = "flying"

    def get_back(self) -> Mode:
        """Return the UI mode shown when navigating back."""
        match self:
            case Mode.LEVELS:
                return Mode.MAPS
            case _:
                return self.MENU

    @classmethod
    def get(cls, mode: str) -> "Mode":
        """Convert a mode string to a mode enum member.

        Args:
            mode (str): Mode name to look up.

        Returns:
            Mode: Matching mode, or ``Mode.NONE`` when unknown.
        """
        return cls.__members__.get(mode.upper(), Mode.NONE)


class Action(Enum):
    """Actions a drone can perform during a turn."""

    MOVE = "MOVE"
    TRANSIT = "TRANSIT"
    WAIT = "WAIT"
    NONE = "NONE"
