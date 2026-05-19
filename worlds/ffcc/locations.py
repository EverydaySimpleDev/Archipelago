from typing import Dict, List

from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import Location, Region

class FFCCLocationData(NamedTuple):
    """

    :param code: The unique code identifier for the location.
    :param region: The name of the region where the location resides.
    :param stage_id: The ID of the stage where the location resides.
    :param bit: The bit in memory that is associated with the location. This is combined with other location data to
    determine where in memory to determine whether the location has been checked. If the location is a special type,
    this bit is ignored.
    :param address: For certain location types, this variable contains the address of the byte with the check bit for
    that location. Defaults to `None`.
    :param object_id: the object / location in game that will be replaced. Defaults to `None`.
    """

    code: Optional[int]
    region: str
    stage_id: int
    bit: int
    address: Optional[int] = None
    object_id: Optional[int] = None

class FFCCLocation(Location):
    """
    :param player: The ID of the player whose world the location is in.
    :param name: The name of the location.
    :param parent: The location's parent region.
    :param data: The data associated with this location.
    """

    game: str = "Final Fantasy Crystal Chronicles"

    def __init__(self, player: int, name: str, parent: Region, data: FFCCLocationData | None = None):
        address = None if data.code is None else FFCCLocation.get_apid(data.code)
        super().__init__(player, name, address=address, parent=parent)

        self.code = data.code
        self.region = data.region
        self.stage_id = data.stage_id
        self.bit = data.bit
        self.address = self.address
        self.object_id = data.object_id

    @staticmethod
    def get_apid(code: int) -> int:
        """
        Compute the Archipelago ID for the given location code.

        :param code: The unique code for the location.
        :return: The computed Archipelago ID.
        """
        base_id: int = 2326528
        return base_id + code

LOCATION_TABLE: dict[str, FFCCLocationData] = {

    "Living Room - Frog Ring (Behind Window)": FFCCLocationData(0, "Living Room", 0x07, 1, 0xde30, 19),

}

location_groups = {
    "Living Room": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Living Room"],
}
