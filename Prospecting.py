import requests
import time
import csv
from api_key import key

# Automating prospecting process for Avoca using Google Places API

SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
API_KEY = key


# NYC : "40.712776,-74.005974


def search_Query(query, location):
    results = []
    next_page_token = None

    while True:
        params = {
            "location": location,  # Example coordinates (Los Angeles, CA)
            "radius": 2000,  # Radius in meters
            "query": query,  # e.g., "HVAC services"
            "key": API_KEY,
        }

        if next_page_token:
            params["pagetoken"] = next_page_token

        # Make the API request
        response = requests.get(SEARCH_URL, params=params)
        data = response.json()

        # Collect results
        if "results" in data:
            results.extend(data["results"])

        # Handle next_page_token
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Delay before the next request (Google API may require a few seconds)
        time.sleep(3)  # Recommended delay

    return results


def search_plumberType(location):
    results = []
    next_page_token = None

    while True:

        params = {
            "location": location,
            "radius": 2000,  # Radius in meters
            "type": "plumber",  # Place type
            "key": API_KEY,
        }

        # Optional parameters for refining the search
        if next_page_token:
            params["pagetoken"] = next_page_token

        # Make the API request
        response = requests.get(SEARCH_URL, params=params)
        data = response.json()

        # Collect results
        if "results" in data:
            results.extend(data["results"])

        # Handle next_page_token
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Delay before the next request (Google API may require a few seconds)
        time.sleep(6)  # Recommended delay

    return results


def fetch_reviews(place_id, order="relevant"):
    params = {
        "place_id": place_id,
        "fields": "name,rating,reviews,formatted_address,opening_hours,website",
        "key": API_KEY,
    }

    try:
        response = requests.get(DETAILS_URL, params=params)
        response.raise_for_status()
        result = response.json().get("result", {})

        # Process reviews based on ordering preference
        reviews = result.get("reviews", [])
        if order == "recent":
            reviews = sorted(reviews, key=lambda r: r["time"], reverse=True)  # Most recent first

        # Return the full details, including ordered reviews
        result["reviews"] = reviews
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for place_id {place_id}: {e}")
        return {}


def getAllBusinesses(coordinates_mesh, hvac_search):
    seen_place_ids = set()  # A set to track the place_ids we've already encountered
    unique_businesses = []  # List to store unique business objects

    for cord in coordinates_mesh:
        businesses = hvac_search(cord)  # Get the list of businesses for this coordinate
        for business in businesses:
            place_id = business.get("place_id")  # Get the unique place_id for this business
            if place_id not in seen_place_ids:
                seen_place_ids.add(place_id)  # Add the place_id to the set
                unique_businesses.append(business)  # Add the business to the list
    return unique_businesses


def save_to_csv(businesses, filename="hvac_companies.csv", ):
    # Define CSV headers
    headers = ["place_id", "name", "formatted_address"
        , "rating", "user_ratings_total", "opening_hours", "website", "reviews", "recent_reviews"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write header row

        for business in businesses:
            place_id = business.get("place_id")
            details = fetch_reviews(place_id)
            details_recent = fetch_reviews(place_id, "recent")
            name = business.get("name")
            address = business.get("formatted_address", "N/A")
            rating = business.get("rating", "N/A")
            total_reviews = business.get("user_ratings_total", "N/A")
            opening_hours = "; ".join(business.get("opening_hours", {}).get("weekday_text", []))
            website = business.get("website", "N/A")
            reviews = "; ".join([review.get("text", "") for review in details.get("reviews", [])])
            recent_reviews = "; ".join([review.get("text", "") for review in details_recent.get("reviews", [])])
            writer.writerow([place_id, name, address, rating, total_reviews,
                             opening_hours, website, reviews, recent_reviews])


def read_coordinates_from_csv(file_path):
    coordinates = []  # List to store the coordinate pairs as strings
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if there is one
        for row in csv_reader:
            # Assuming the first column is longitude and the second column is latitude
            longitude = row[0]
            latitude = row[1]
            coordinate_string = f"{longitude}, {latitude}"  # Create the formatted string
            coordinates.append(coordinate_string)
    return coordinates


def main():

    file_path = 'data/mesh_search_coordinates/nyc_full_coverage_grid.csv'  # Path to your CSV file
    coordinates_list = read_coordinates_from_csv(file_path)
    csvPath = "data/MeshSearch_Plumbers_NYC.csv"
    save_to_csv(getAllBusinesses(coordinates_list, search_plumberType), csvPath)


if __name__ == '__main__':
    main()
