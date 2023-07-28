"""Apart Concept Amplifier Media Player Entity."""
from __future__ import annotations
import logging

from apart_concept import APart
from serial import SerialException
import time

from homeassistant import core
import voluptuous as vol

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_URL,
    CONF_NAME,
    CONF_TYPE,
    STATE_OFF,
    STATE_ON,
)

from .const import (
    DEFAULT_NAME,
    DOMAIN
)

from homeassistant.core import HomeAssistant, ServiceCall
#import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import DeviceInfo


_LOGGER = logging.getLogger(__name__)
_VALID_STATES = [
    STATE_ON,
    STATE_OFF,
    "true",
    "false"
]


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
    }
)

SERVICE_SET_SOURCENAME = "set_source_name"

# async def async_setup_entry(
#     hass: HomeAssistant,
#     config_entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> None:
#     """Set up the Apart platform."""
#     port = config_entry.data[CONF_PORT]

#     apart = hass.data[DOMAIN][config_entry.entry_id][APART_OBJECT]
#     sources = _get_sources(config_entry)
#    entities = []

async def async_setup_entry(hass, entry):
    """Set up the media player platform."""
    
    sourceidlist = {"A", "B", "C", "D"}
    platform = entity_platform.async_get_current_platform()


    # This will call Entity.set_sleep_timer(sleep_time=VALUE)
    platform.async_register_entity_service(
        SERVICE_SET_SOURCENAME,
        {
            vol.Required('sourceid'): vol.In(["A", "B", "C", "D"]),

            vol.Required('sourcename'): cv.string
        },
        "set_source_name",
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    """Connect"""
    url = config[CONF_URL]
    name = config[CONF_NAME]
    platform = entity_platform.EntityPlatform(hass=hass, logger=_LOGGER, domain=DOMAIN, platform_name="apart_concept", platform=None, scan_interval=3, entity_namespace="media_player")

    platform.async_register_entity_service(
        SERVICE_SET_SOURCENAME,
        {
            vol.Required('sourceid'): vol.In(["A", "B", "C", "D"]),

            vol.Required('sourcename'): cv.string
        },
        "set_source_name",
    )
    media_player = ApartMedia(url, name);
    
    hass.data[DOMAIN][url] = media_player
    async_add_entities([media_player], True)




class ApartMedia(MediaPlayerEntity):
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, url, name):
        """Initialize new Apart"""
        self._apart = APart(url)

        self._source_ids = ["A", "B", "C", "D"]; # Static list of the strings sent in requests
        self._source_names =["A", "B", "C", "D"]; # This list is updated on first power up after hass restart to the actual names on unit

        self._unique_id = url
        self._name = name

        self._state = None
        self._volume = None
        self._source = None
        self._update_success = True
        self._got_names = False;


    def update(self):
        """Retrieve latest state."""
        try:
            o =  self._apart.get_info()
            
        except SerialException:
            self._update_success = False
            _LOGGER.warning("Could not update Apart %d", self._name)
            return
        if not o:
            self._update_success = False
            return
        self._state = STATE_OFF if o.standby else STATE_ON
        self._volume = o.musicvolume/100
        self._source = self._source_names[self._source_ids.index(o.source)]

        if not o.standby:
            if not self._got_names:
                self._source_names[0] = self._apart.get_source_name("A");
                self._source_names[1] = self._apart.get_source_name("B");
                self._source_names[2] = self._apart.get_source_name("C");
                self._source_names[3] = self._apart.get_source_name("D");
                self._got_names = True;
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="Apart",
            model="Concept",
            name=self.name,
        )

    @property
    def name(self):
        """Return the name of the zone."""
        return self._name
    
    @property
    def unique_id(self):
        """Return unique ID for this device."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the zone."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        if self._volume is None:
            return None
        return self._volume

    @property
    def media_title(self):
        """Return the current source as medial title."""
        return self._source;

    @property
    def source(self):
        """Return the current input source of the device."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_names

    def select_source(self, source):
        """Select input source."""
        self._apart.set_source(self._source_ids[self._source_names.index(source)])
        return 

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self._apart.set_volume(volume*100)  

    def set_source_name(self, sourceid, sourcename):
        #_LOGGER.warning("Calling service_speed_up")
        # TODO: Check if sourceid is A B C D somehow its midnight I dunno how to do that
        #self._source_names[sourceid] = sourcename;
        self._apart.set_source_name(sourceid, sourcename);


    def turn_on(self):
        """Turn the media player on."""
        self._state = STATE_ON
        self._apart.set_power(True)

    def turn_off(self):
        """Turn the media player off."""
        self._state = STATE_OFF
        self._apart.set_power(False)

