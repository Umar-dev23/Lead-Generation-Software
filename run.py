import argparse
import asyncio
from py_lead_generation.src.google_maps.engine import GoogleMapsEngine

async def main(query, location, zoom):
    # Create an instance of the engine with the required arguments
    engine = GoogleMapsEngine(query=query, location=location, zoom=int(12))

    try:
        # Initialize the browser and perform the search
        await engine.init_browser(hidden=False)  # Set hidden=True if you want headless mode
        await engine.search()

        # Run the engine to populate entries
        await engine.run()

        # Save results to CSV
        engine.save_to_csv('leads.csv')
    finally:
        # Ensure browser is always closed
        await engine.shut_browser()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Google Maps search.')
    parser.add_argument('--search_query', required=True, help='The search query')
    parser.add_argument('--location', required=True, help='The location for search')
    parser.add_argument('--zoom', default='12', help='Optional zoom level for Google Maps')
    args = parser.parse_args()
    asyncio.run(main(args.search_query, args.location, args.zoom))