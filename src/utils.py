from enum import Enum


class ParsingTags(Enum):
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"

    @classmethod
    def getTag(cls, tag: str):
        return cls.__members__.get(tag.upper())

class ParsingZones(Enum):
    NORMAL = 1
    RESTRICTED = 2
    PRIORITY = 0.9999
    BLOCKED = 99999999999999

    @classmethod
    def getZone(cls, zone: str):
        return cls.__members__.get(zone.upper())

class ParsingColors(Enum):
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
    PINK = "#E994D7"

    @classmethod
    def getColor(cls, color: str):
        return cls.__members__.get(color.upper())
