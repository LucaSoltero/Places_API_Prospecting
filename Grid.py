import csv
import math
import numpy as np


def generate_full_coverage_grid(center_lat, center_lon, square_side_km, circle_radius_km):
    """
    Generate a grid of latitude and longitude points that ensures full coverage of the square by circles.

    Parameters:
    - center_lat: Latitude of the square's center.
    - center_lon: Longitude of the square's center.
    - square_side_km: Side length of the square in kilometers.
    - circle_radius_km: Radius of each circle in kilometers.

    Returns:
    - List of (latitude, longitude) tuples.
    """
    # Constants
    km_per_degree_lat = 111  # Approximation of km per degree latitude

    # Calculate latitude and longitude adjustments
    lat_adjustment = square_side_km / 2 / km_per_degree_lat
    lon_adjustment = square_side_km / 2 / (km_per_degree_lat * math.cos(math.radians(center_lat)))

    # Grid spacing (must be <= diameter to ensure coverage)
    spacing_km = circle_radius_km * 2
    lat_spacing = spacing_km / km_per_degree_lat
    lon_spacing = spacing_km / (km_per_degree_lat * math.cos(math.radians(center_lat)))

    # Generate the grid of points
    lat_points = np.arange(center_lat - lat_adjustment, center_lat + lat_adjustment + lat_spacing, lat_spacing)
    lon_points = np.arange(center_lon - lon_adjustment, center_lon + lon_adjustment + lon_spacing, lon_spacing)

    grid_points = [(lat, lon) for lat in lat_points for lon in lon_points]

    return grid_points


def write_coordinates_to_csv(coordinates, filename="coordinates.csv"):
    """
    Write a list of latitude and longitude pairs to a CSV file.

    Parameters:
    - coordinates: List of tuples, where each tuple contains (latitude, longitude).
    - filename: Name of the CSV file to save. Default is 'coordinates.csv'.
    """
    # Define the header for the CSV file
    header = ["Latitude", "Longitude"]

    # Write to the CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write header
        writer.writerows(coordinates)  # Write all coordinates

    print(f"Coordinates successfully written to {filename}.")


def main():
    # Parameters
    center_lat = 40.712776  # NYC latitude
    center_lon = -74.005974  # NYC longitude
    square_side_km = 50  # Side length of the square
    circle_radius_km = 2  # Radius of each circle
    # Generate the grid
    grid = generate_full_coverage_grid(center_lat, center_lon, square_side_km, circle_radius_km)
    # Write to CSV
    write_coordinates_to_csv(grid, "data/Coordinates/nyc_full_coverage_grid.csv")


if __name__ == '__main__':
    main()
