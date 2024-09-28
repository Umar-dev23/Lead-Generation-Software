import time
import sys
import os
import io
import re
import csv
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from py_lead_generation.src.engines.base import BaseEngine
from py_lead_generation.src.engines.abstract import AbstractEngine
from py_lead_generation.src.misc.utils import get_coords_by_location

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class GoogleMapsEngine(BaseEngine, AbstractEngine):
    '''
    GoogleMapsEngine

    [EDITABLE] SCROLL_TIME_DURATION_S - scroll time duration to view the search results, preferably should be not less than 150, for testing purposes can be decreased

    [EDITABLE] SLEEP_PER_SCROLL_S - amount of seconds to wait before each scroll of search results so that google maps does not output endless loading ~ aka simulate human-like activity, preferable should be not less than 5

    Usage:

    engine = GoogleMapsEngine(*args, **kwargs)

    await engine.run()

    await engine.save_to_csv()

    print(engine.entries)
    '''

    BASE_URL = 'https://www.google.com/maps/search/{query}/@{coords},{zoom}z/data=!3m1!4b1?entry=ttu'
    FIELD_NAMES = ['Title', 'Address', 'PhoneNumber', 'WebsiteURL', 'GoogleMapsURL', 'PlaceLat', 'PlaceLang']
    FILENAME = 'google_maps_leads.csv'

    SLEEP_PER_SCROLL_S = 2
    SCROLL_TIME_DURATION_S = 200

    def __init__(self, query: str, location: str, zoom: int | float = 12) -> None:
        '''
        query: str - what are you looking for? e.g., gym
        location: str - where are you looking for that query? e.g., Astana
        zoom: int | float - google maps zoom e.g., 8.75

        Creates GoogleMapsEngine instance
        '''
        self._entries = []
        self.zoom = zoom
        self.query = query
        self.location = location
        self.coords = get_coords_by_location(self.location)
        self.search_query = f'{self.query}%20{self.location}'
        self.url = self.BASE_URL.format(
            query=self.search_query, coords=','.join(map(str, self.coords)), zoom=self.zoom
        )
        self.browser = None
        self.page = None

    async def init_browser(self, hidden=True):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=hidden)
        self.page = await self.browser.new_page()

    async def shut_browser(self):
        if self.browser:
            await self.browser.close()

    async def search(self):
        if not self.page:
            raise ValueError('Initialize the browser before searching by await *.init_browser()')

        await self.page.goto(self.url)
        await self._get_search_results_urls()

    async def _get_search_results_urls(self) -> list[str]:
        '''
        Goes through the search results for GoogleMapsEngine.SCROLL_TIME_DURATION_S seconds

        Waits for GoogleMapsEngine.SLEEP_PER_SCROLL_S seconds so that GoogleMaps will not output endless load, aka simulate human-like activity

        Or scrapes the results urls, once they are no more results
        '''
        async def hover_search_results() -> None:
            '''
            Hovers on leftbar, where search results are located

            Needed so that scroll function is used properly - not on the map but on the search results div
            '''
            leftbar = await self.page.query_selector('[role="main"]')
            await leftbar.hover()
            await asyncio.sleep(0.5)

        async def scroll_and_sleep(delta_y: int = 1000) -> None:
            '''
            delta_y: int = 1000 pixel units to scroll down along y-axis

            Scrolls down by delta_y and waits for GoogleMapsEngine.SCROLL_TIME_DURATION_S seconds
            '''
            await self.page.mouse.wheel(0, delta_y)
            await asyncio.sleep(self.SLEEP_PER_SCROLL_S)

        async def end_locator_is_present() -> bool:
            '''
            Returns end_locator as boolean value, which correlates with the possible end of the search results

            Once end_locator is Truthy, aka ElementHandle, it means that there is nothing more to scroll
            '''
            end_locator = await self.page.query_selector('.m6QErb.tLjsW.eKbjU')
            return bool(end_locator)

        async def scrape_urls() -> list[str]:
            '''
            Should be called once page is being scrolled all the way down (end_locator found) or GoogleMapsEngine.SCROLL_TIME_DURATION_S duration limit is exceeded

            Returns list[str] typed scraped urls list using query_selector
            '''
            urls = []
            link_elements = await self.page.query_selector_all('a.hfpxzc')
            for link_element in link_elements:
                url = await link_element.get_attribute('href')
                urls.append(url)
            return urls

        await hover_search_results()
        start_scroll_time = time.time()

        while True:
            await scroll_and_sleep()
            finish_scroll_time = time.time()
            if (await end_locator_is_present()) or (finish_scroll_time - start_scroll_time > self.SCROLL_TIME_DURATION_S):
                break

        urls = await scrape_urls()
        return urls


    def extract_lat_lang_from_url(self, url: str) -> tuple[str, str]:
        # Check if the URL matches the pattern of place URL
        if '!3d' in url and '!4d' in url:
           match = re.search(r'!3d([-.\d]+)!4d([-.\d]+)', url)
        else:
           match = re.search(r'@([-.\d]+),([-.\d]+),', url)
       
        if match:
           return match.groups()
        else:
           return 'No Info', 'No Info'


    def _parse_data_with_soup(self, html: str, url: str) -> list[str]:
        '''
        html: str - HTML representation of the page to parse
        url: str - The URL of the Google Maps page

        Returns list[str] typed parsed data - [title, addr, phone, website, url, place_lat, place_lang]
        '''
        soup = BeautifulSoup(html, 'html.parser')
        data = []

        # Extract Title
        title = soup.select_one('.DUwDvf.lfPIob')
        data.append(title.get_text() if title else 'No Info')

        # Extract Address
        address = soup.select_one('[data-item-id="address"] .Io6YTe')
        data.append(address.get_text() if address else 'No Info')

        # Extract Phone Number
        phone = soup.select_one('[data-tooltip="Copy phone number"] .Io6YTe')
        data.append(phone.get_text() if phone else 'No Info')

        # Extract Website
        website = soup.select_one('[data-item-id="authority"] .Io6YTe')
        data.append(website.get_text() if website else 'No Info')

        # Add URL
        data.append(url)
        
        # Extract latitude and longitude from the main URL
        main_lat, main_lang = self.extract_lat_lang_from_url(self.url)


        # Extract latitude and longitude for each place URL
        place_lat, place_lang = self.extract_lat_lang_from_url(url)
        data.append(place_lat)
        data.append(place_lang)
        print("Main Latitude:", main_lat)
        print("Main Longitude:", main_lang)
        print("Place Latitude:", place_lat)
        print("Place Longitude:", place_lang)
    
        return data

    async def run(self):
       if not self.page:
           raise ValueError('Initialize the browser before running by await *.init_browser()')

       await self.search()
       urls = await self._get_search_results_urls()

       with open('google_maps_leads.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(self.FIELD_NAMES)  # Write the header row

        # Extract main latitude and longitude from the initial URL
        main_lat, main_lang = self.extract_lat_lang_from_url(self.url)

        for url in urls:
            await self.page.goto(url)
            html = await self.page.content()
            data = self._parse_data_with_soup(html, url)  # Pass URL to parser

            # Extract place latitude and longitude from the place URL
            place_lat, place_lang = self.extract_lat_lang_from_url(url)

            # Convert lat/lng values to floats and round to 1 decimal place for comparison
            main_lat_rounded = round(float(main_lat), 1)
            main_lang_rounded = round(float(main_lang), 1)
            place_lat_rounded = round(float(place_lat), 1)
            place_lang_rounded = round(float(place_lang), 1)

            # Check if both latitude and longitude match up to the first decimal place
            if (main_lat_rounded == place_lat_rounded and
                main_lang_rounded == place_lang_rounded):
                
                # If both lat/lng match, save the data
                print("Extracted ", [d.encode('utf-8', 'replace').decode('utf-8', 'replace') for d in data])
                self._entries.append(data)
                writer.writerow(data)  # Save each entry immediately after extraction
            else:
                # If either lat or lng doesn't match, skip saving
                print(f"Skipping data for {url} due to mismatch in lat/lng.")


    def save_to_csv(self, filename=None):
        filename = filename or self.FILENAME
        if not self._entries:
            raise NotImplementedError("Entries are empty, call .run() method first to save them")

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.FIELD_NAMES)
            writer.writerows(self._entries)
