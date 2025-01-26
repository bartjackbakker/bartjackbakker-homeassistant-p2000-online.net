from datetime import timedelta  # Voeg deze import toe
from homeassistant import config_entries
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_PROVINCIE, CONF_DISCIPLINES
import voluptuous as vol
import asyncio
import logging
import aiohttp
import async_timeout
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

class P2000Coordinator(DataUpdateCoordinator):
    """Coordinator to manage P2000 data updates."""

    def __init__(self, hass: HomeAssistant, provincie: str, discipline: str) -> None:
        """Initialize the P2000 coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="P2000",
            update_interval=timedelta(minutes=10),  # Gebruik datetime.timedelta
        )
        self.provincie = provincie
        self.discipline = discipline
        self.data = None  # Dit zal worden bijgewerkt met sensorwaarden

    async def _async_update_data(self):
        """Fetch the latest data from P2000."""
        url = f"https://www.p2000-online.net/p2000.py?{self.provincie.lower()}=1"
        meldingen = []
        _LOGGER.debug("Fetching data for P2000: url=%s", url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                # Parse the HTML
                _LOGGER.debug("tabel is opgehaald")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")

        if len(table) < 2:
            print("Expected at least two tables in the HTML.")

        # Get the rows of the second table
        table = table[1].find_all('tr')
        #looping through the HTML table to scrape the data
        for tr in table:
            td = tr.find_all('td')
            if not td:
                continue
            if td[0].text:
                melding = {
                'datum': td[0].text,
                'discipline' : td[1].text,
                'regio' : td[2].text,
                'melding' : td[3].text,
                'teams' : []
                }
                meldingen.append(melding)
            else:
                length = len(meldingen) -1
                meldingen[length]['teams'].append(td[3].text)

        for melding in meldingen:
            if melding['discipline'].lower() == self.discipline.lower():
                _LOGGER.debug("discipline: %s en config: %s" , meldingen[0]['discipline'], self.discipline)
                self.data = {
                    "datum": melding['datum'],
                    "discipline": melding['discipline'],
                    "regio": melding['regio'],
                    "melding": melding['melding'],
                    "teams": melding['teams'],
                }
                _LOGGER.debug("tabel: %s", self.data)
                return self.data
            else:
                continue
        return None