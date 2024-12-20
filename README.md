## This repo contains three files:

# 1. Prospecting: 
Calls Google Places API and queries for plumbing companies. Since Places only returns up to 60 results from an API call in a given radius, I wrote a script that generates around 200 points within a 50X50km rectangle around New York City. Prospecting iterates through this coordinates list and calls the API for each point in the grid, maximizing data extraction.

  See below how doing a singlular api call across a large rarius only returns 60 results missing out on many businesses
 ![radius_query](https://github.com/user-attachments/assets/47a0b368-281b-4bf9-b9cd-41f980c26232)

# 2. Grid: 
The grid creates a 50X50km square around a city's given coordinates (in this example, NYC) and populates the square with search points. It assumes that each circle has a radius of 2km and ensures the entire area of the rectangle is covered. 

see below for grid search example:
![grid_query](https://github.com/user-attachments/assets/bb61193f-88c8-4915-97b6-cd8ed82f333c)


# 3. Discovery: 
Reveals the results of the data extraction. It seems that the process can be optimized as only around 1200 businesses were returned despite searching around 200 coordinate points in the city. That being said the positioning of some of the points (say in the ocean) is a waste thus there is defintly room for improvement with better search point placement. 

This is a rough draft of the project, and it seems like a lot more data can be extracted with a more optimized grid search approach.  

Raw data can be found in data folder.

Best,
Luca 
