# Install the Python library from https://pypi.org/project/amadeus
from amadeus import Client, ResponseError
import datetime
import requests

# Initialize the Amadeus client
amadeus = Client(
    client_id='iA77WQAn7CBuARZF6Brki3he7HkVLOjv',
    client_secret='5Z3yzVw25M6cd80u'
)

def search_flights(source, destination, departure_date):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=source,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1
        ).data
        return response[:10]  # Limit to 10 flight options
    except ResponseError as error:
        print(f"Error fetching flights: {error}")
        return None

def search_hotels(city_code):
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        ).data
        return response
    except ResponseError as error:
        print(f"Error fetching hotels: {error}")
        return None

def get_checkin_links(airline_code):
    try:
        response = amadeus.reference_data.urls.checkin_links.get(airlineCode=airline_code)
        return response.data
    except ResponseError as error:
        print(f"Error fetching check-in links: {error}")
        return None

def search_places_to_visit(query, near_location):
    url = "https://api.foursquare.com/v3/places/search"

    params = {
        "query":'Parks',
        "near": 'Dubai,UAE',
        "open_now": "true",
        "sort": "DISTANCE"
    }

    headers = {
        "Accept": "application/json",
        "Authorization": "fsq3tfa7HZcsDmAiCyMwWD3lg9TSJssSOWOgQDDRGO+EVAw="
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses

        data = response.json()

        if 'results' in data:
            results = data['results']
            places = []
            for place in results:
                name = place.get('name', 'N/A')
                address = place.get('location', {}).get('address', 'N/A')
                category = place.get('categories', [{'name': 'N/A'}])[0]['name']
                places.append({"name": name, "address": address, "category": category})
            return places
        else:
            print("No results found.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching places to visit: {e}")
        return None

def generate_itinerary(source, destination, travel_date, stay_days):
    travel_date = datetime.datetime.strptime(travel_date, "%Y-%m-%d")
    return_date = travel_date + datetime.timedelta(days=stay_days)
    
    # Fetch flights to destination
    flights_to_destination = search_flights(source, destination, travel_date.strftime('%Y-%m-%d'))
    
    # Fetch flights from destination
    flights_from_destination = search_flights(destination, source, return_date.strftime('%Y-%m-%d'))
    
    # Fetch hotels
    hotels = search_hotels(destination)
    
    # Fetch places to visit
    places_to_visit = search_places_to_visit("tourist attractions", destination)
    
    # Create the itinerary
    itinerary = f"Travel Itinerary from {source} to {destination}:\n\n"
    
    # Add flights to destination
    itinerary += "Available Flights to Destination:\n"
    if flights_to_destination:
        for flight in flights_to_destination:
            itinerary += f"- Flight {flight['id']}\n"
            for itinerary_flight in flight['itineraries']:
                for segment in itinerary_flight['segments']:
                    itinerary += f"  {segment['departure']['iataCode']} -> {segment['arrival']['iataCode']}\n"
                    itinerary += f"    Departure: {segment['departure']['at']}\n"
                    itinerary += f"    Arrival: {segment['arrival']['at']}\n"
                    itinerary += f"    Carrier: {segment['carrierCode']} {segment['number']}\n"
                    
                    # Get online check-in links
                    checkin_links = get_checkin_links(segment['carrierCode'])
                    if checkin_links:
                        for link in checkin_links:
                            itinerary += f"    Online Check-in: {link['href']}\n"
    else:
        itinerary += "  No flights found.\n"
    itinerary += "\n"
    
    # Add hotels
    itinerary += "Available Hotels:\n"
    if hotels:
        for hotel in hotels:
            itinerary += f"Hotel Name: {hotel['name']}\n"
            itinerary += f"Hotel ID: {hotel['hotelId']}\n"
            itinerary += f"Postal Code: {hotel['address'].get('postalCode', 'N/A')}\n"
            itinerary += f"Country Code: {hotel['address']['countryCode']}\n"
            itinerary += f"Latitude: {hotel['geoCode']['latitude']}\n"
            itinerary += f"Longitude: {hotel['geoCode']['longitude']}\n"
            itinerary += '-' * 40 + "\n"
    else:
        itinerary += "  No hotels found.\n"
    itinerary += "\n"
    
    # Add places to visit
    itinerary += "Places to Visit:\n"
    if places_to_visit:
        for place in places_to_visit:
            itinerary += f"Name: {place['name']}\n"
            itinerary += f"Address: {place['address']}\n"
            itinerary += f"Category: {place['category']}\n"
            itinerary += '-' * 40 + "\n"
    else:
        itinerary += "  No places found.\n"
    itinerary += "\n"
    
    # Add return flights
    itinerary += "Return Flights:\n"
    if flights_from_destination:
        for flight in flights_from_destination:
            itinerary += f"- Flight {flight['id']}\n"
            for itinerary_flight in flight['itineraries']:
                for segment in itinerary_flight['segments']:
                    itinerary += f"  {segment['departure']['iataCode']} -> {segment['arrival']['iataCode']}\n"
                    itinerary += f"    Departure: {segment['departure']['at']}\n"
                    itinerary += f"    Arrival: {segment['arrival']['at']}\n"
                    itinerary += f"    Carrier: {segment['carrierCode']} {segment['number']}\n"
    else:
        itinerary += "  No flights found.\n"
    
    return itinerary

# Example usage
source = 'RUH'  # Riyadh IATA code
destination = 'DXB'  # Kozhikode IATA code
travel_date = '2024-06-25'
stay_days = 2

itinerary = generate_itinerary(source, destination, travel_date, stay_days)
print(itinerary)
