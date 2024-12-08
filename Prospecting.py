import requests
import time
import csv
import pandas as pd
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
            "radius": 1000,  # Radius in meters
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


def search_Type(location, type):
    results = []
    next_page_token = None

    while True:

        params = {
            "location": location,
            "radius": 1000,  # Radius in meters
            "type": type,  # Place type
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
        time.sleep(3)  # Recommended delay

    return results



def fetch_Details(place_id):
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website,formatted_address,rating,user_ratings_total,opening_hours,reviews",
        "key": API_KEY,
    }

    try:
        response = requests.get(DETAILS_URL, params=params)
        response.raise_for_status()
        result = response.json().get("result", {})

        # Extract reviews
        reviews = result.get("reviews", [])
        relevant_reviews = [
            {
                "author_name": review.get("author_name", "Anonymous"),
                "rating": review.get("rating", "N/A"),
                "time": review.get("time", "N/A"),
                "text": review.get("text", "No review text"),
                "relative_time_description": review.get("relative_time_description", "N/A"),
            }
            for review in reviews
        ]

        return {
            "name": result.get("name", "N/A"),
            "formatted_phone_number": result.get("formatted_phone_number", "N/A"),
            "website": result.get("website", "N/A"),
            "formatted_address": result.get("formatted_address", "N/A"),
            "rating": result.get("rating", "N/A"),
            "user_ratings_total": result.get("user_ratings_total", "N/A"),
            "opening_hours": "; ".join(result.get("opening_hours", {}).get("weekday_text", [])),
            "reviews": relevant_reviews,  # Default sorted by relevance
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for place_id {place_id}: {e}")
        return {
            "name": "N/A",
            "formatted_phone_number": "N/A",
            "website": "N/A",
            "formatted_address": "N/A",
            "rating": "N/A",
            "user_ratings_total": "N/A",
            "opening_hours": "N/A",
            "reviews": [],
        }


def save_to_csv(businesses, filename="hvac_companies.csv", businessType=''):
    data = []

    for business in businesses:
        place_id = business.get("place_id")
        details = fetch_Details(place_id)
        name = details.get("name")
        formatted_phone_number = details.get("formatted_phone_number")
        formatted_address = details.get("formatted_address", "N/A")
        rating = details.get("rating", "N/A")
        user_ratings_total = details.get("user_ratings_total", "N/A")
        opening_hours = details.get("opening_hours")
        website = details.get("website", "N/A")
        reviews = "; ".join([review.get("text", "") for review in details.get("reviews", [])])
        # Add the business data to the list
        data.append({
            "place_id": place_id,
            "business_type": businessType,
            "name": name,
            "formatted_phone_number": formatted_phone_number,
            "website": website,
            "formatted_address": formatted_address,
            "rating": rating,
            "user_ratings_total": user_ratings_total,
            "opening_hours": opening_hours,
            "reviews": reviews
        })
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='place_id', keep='first')
    # Write the DataFrame to CSV without duplicates
    df.to_csv(filename, index=False, encoding="utf-8")


def getAllBusinesses(coordinates_mesh, hvac_search, query):
    b_list = []  # List to store unique business objects
    for cord in coordinates_mesh:
        businesses = hvac_search(cord, query)  # Get the list of businesses for this coordinate
        b_list.extend(businesses)

    print("business list created")
    return b_list


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
    newYork = "40.712776,-74.005974"
    bs = search_Type(newYork, "plumber")
    path = "data/HVAC_Query/testPhoneEnrichement5.csv"
    save_to_csv(bs, path)

    file_path = 'data/Coordinates/nyc_full_grid_coordinates_1k.csv'  # Path to your CSV file
    coordinates_list = read_coordinates_from_csv(file_path)
    csvPath = "data/HVAC_Query/MeshSearch_Plumbers_NYC2.csv"




if __name__ == '__main__':
    main()
