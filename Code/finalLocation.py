
#requires a file with lon-lat only and ouput gives a file with updated address

import csv
from geopy.geocoders import Nominatim
import time

# Initialize the geolocator
geolocator = Nominatim(user_agent="geopy_example")

def reverse_geocode(latitude, longitude):
    try:
        location = geolocator.reverse((latitude, longitude), timeout=10)
        return location.address if location else "Address not found"
    except Exception as e:
        print(f"Error: {e}")
        return "Error fetching address"

# Input and output file paths
input_file = "lon-lat.csv"  # Replace with your actual input file name
output_file = "coordinates_with_address.csv"  # Output file

with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
    reader = csv.reader(infile, delimiter="\t")  # Assuming tab-separated file
    writer = csv.writer(outfile, delimiter="\t")
    
    # Add the new header row
    writer.writerow(["longitude", "latitude", "address"])
    
    for row in reader:
        try:
            # Split the longitude and latitude values
            lon_lat = row[0].split(",")
            longitude = float(lon_lat[0])
            latitude = float(lon_lat[1])
            
            # Get the address
            address = reverse_geocode(latitude, longitude)
            print(f"Processed: {latitude}, {longitude} -> {address}")
            writer.writerow([longitude, latitude, address])
            
            # Pause to avoid overwhelming the API
            time.sleep(1)
        except (ValueError, IndexError) as e:
            print(f"Skipping invalid row: {row} - Error: {e}")

print("Completed adding addresses to the file.")


#after completion add this data into formatted_data using python only