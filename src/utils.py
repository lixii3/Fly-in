from enum import Enum


class ParsingTags(Enum):
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"

    def getTag(tag: str):
        match tag:
            case 'start_hub': return ParsingTags.START_HUB
            case 'end_hub': return ParsingTags.END_HUB
            case 'hub': return ParsingTags.HUB
            case 'connection': return ParsingTags.CONNECTION
            case _: return None

class ParsingZones(Enum):
    NORMAL = 1
    RESTRICTED = 2
    PRIORITY = 0.9999
    BLOCKED = 99999999999999

    def getZone(zone: str):
        match zone:
            case 'normal': return ParsingZones.NORMAL
            case 'restricted': return ParsingZones.RESTRICTED
            case 'priority': return ParsingZones.PRIORITY
            case 'blocked': return ParsingZones.BLOCKED
            case _: return None

class ParsingColors(Enum):
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    WHITE = "#FFFFFF"
    PINK = "#E994D7"

    def getColor(color: str):
        match color:
            case 'red': return ParsingColors.RED
            case 'green': return ParsingColors.GREEN
            case 'blue': return ParsingColors.BLUE
            case 'yellow': return ParsingColors.YELLOW
            case 'pink': return ParsingColors.PINK
            case 'white': return ParsingColors.WHITE
            case _: return None
