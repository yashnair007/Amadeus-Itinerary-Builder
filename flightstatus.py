from amadeus import Client, ResponseError

amadeus = Client(
    client_id='Replace with client id',
    client_secret='Replace with secret id'
)

try:
    '''
    Returns flight status of a given flight
    '''
    response = amadeus.schedule.flights.get(carrierCode='6E',
                                            flightNumber='1325',
                                            scheduledDepartureDate='2024-06-24')
    flight_status = response.data

    # Print structured output
    for flight in flight_status:
        flight_info = flight['flightPoints']
        print(f"Departure Airport: {flight_info[0]['iataCode']}")
        print(f"Scheduled Departure: {flight_info[0]['departure']['timings'][0]['value']}")
        print(f"Arrival Airport: {flight_info[1]['iataCode']}")
        print(f"Scheduled Arrival: {flight_info[1]['arrival']['timings'][0]['value']}")
        print('-' * 40)
except ResponseError as error:
    raise error
