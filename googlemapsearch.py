import bokeh
import numpy as np
import pandas as pd
import requests
from bokeh.models import (HoverTool, BoxSelectTool, BoxZoomTool,
                          TapTool, PanTool, ResetTool, WheelZoomTool,
                          GMapPlot, GMapOptions, DataRange1d,
                          glyphs, Legend, ColumnDataSource
                          )
from bokeh.palettes import Spectral6
from bokeh.plotting import figure, output_file, show
from bokeh.plotting import gmap
from bokeh.resources import CDN, INLINE
from bokeh.embed import file_html
from time import sleep
from scipy.ndimage import zoom

BOKEH_RESOURCES=CDN


""" use your own Google Maps (places) API token her"""
gapi = "asdfasdf"

# start parameters for location
cities = ["odense", "copenhagen"]
latitude = 55.396976
longitude = 10.383065

# initial radius in meter, max 60 hits (google default)
radius = 10000
# extended radius in meter in order to overcome the 60 hits limits
extended_radius = 100  # meter
search_type = "restaurant"
search_keyword = "thai"

# Initialize lists for relevant groups
restaurants = []
rating = []
reviews = []
price_level = []
address = []
place_id = []
lat = []
lng = []


def nearby_search(gapi, place_id, restaurants, rating, price_level, address, lat, lng, reviews):
    nbs_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    if search_keyword:
        nbs_key = "keyword=" + search_keyword + " " + search_type.replace(" ", "%20")
    else:
        nbs_key = "keyword=" + search_type.replace(" ", "%20")

    nbs_other = "&key=" + gapi
    nbs_nextpage = ""

    for place in range(len(place_id)):
        # For each place_id, search nearby within extended radius and add if they're non duplicates
        nbs_location = "location={},{}&radius=" + str(extended_radius) + "&type=" + search_type + "&".format(lat[place], lng[place])
        nbs_gurl = nbs_base + nbs_location + nbs_key + nbs_other
        nbs_response = requests.get(nbs_gurl).json()

        # loop through each page of nearby search
        for response in nbs_response["results"]:
            # If the place_of the current result is not in the place_id list, then add to list
            if response["place_id"] not in place_id:
                print("nbs response add", response["name"])

                rating.append(response["rating"]) if "rating" in response else rating.append(-1)
                restaurants.append(response["name"]) if "name" in response else restaurants.append(np.nan)
                reviews.append(response["user_ratings_total"]) if "user_ratings_total" in response else reviews.append(
                    -1)
                price_level.append(response["price_level"]) if "price_level" in response else price_level.append(-1)
                address.append(response["vicinity"]) if "vicinity" in response else address.append(np.nan)
                place_id.append(response["place_id"]) if "place_id" in response else place_id.append(np.nan)
                lat.append(response["geometry"]["location"]["lat"]) if "geometry" in response else lat.append(np.nan)
                lng.append(response["geometry"]["location"]["lng"]) if "geometry" in response else lng.append(np.nan)

            if "next_page_token" in nbs_response:
                # sleep random to load
                sleep(np.random.normal(5, 0.1, 1))
                nbs_nextpage = "&pagetoken=" + nbs_response["next_page_token"]
                nbs_gurl = nbs_base + nbs_other + nbs_nextpage

                for request in requests.get(nbs_gurl).json()["results"]:
                    if request["place_id"] not in place_id:
                        print("nbs request add", request["name"])

                        rating.append(request["rating"]) if "rating" in request else rating.append(-1)
                        restaurants.append(request["name"]) if "name" in request else restaurants.append(np.nan)
                        reviews.append(
                            request["user_ratings_total"]) if "user_ratings_total" in request else reviews.append(-1)
                        price_level.append(request["price_level"]) if "price_level" in request else price_level.append(
                            -1)
                        address.append(request["vicinity"]) if "vicinity" in request else address.append(np.nan)
                        place_id.append(request["place_id"]) if "place_id" in request else place_id.append(np.nan)
                        lat.append(request["geometry"]["location"]["lat"]) if "geometry" in request else lat.append(
                            np.nan)
                        lng.append(request["geometry"]["location"]["lng"]) if "geometry" in request else lng.append(
                            np.nan)
            else:
                print("nearby search for next page not found in {}, response: {}".format(place, nbs_response["status"]))
                break

    return [place_id, restaurants, rating, price_level, address, lat, lng, reviews]



for city in cities:
    # request setup
    textsearch_base = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    if search_keyword:
        textsearch_query = "query=" + search_keyword + " " + search_type + " {}&".format(city).replace(" ", "%20")
    else:
        textsearch_query = "query=" + search_type + " {}&".format(city).replace(" ", "%20")

    textsearch_location = "location=" + str(latitude) + "," + str(longitude) + "&radius=" + str(radius) + "&type=" + search_type + "&"
    textsearch_other = "&key=" + gapi
    textsearch_nextpage = ""
    textsearch_google_url = textsearch_base + textsearch_query + textsearch_location + textsearch_other
    textsearch_response = requests.get(textsearch_google_url).json()

    #print(textsearch_google_url)
    print("Starting text search...")

    for page in range(0, 5):
        print("textsearch page {}".format(page))
        print("page {}".format(page) + " total places: {}".format(len(place_id)))

        # loop through initial list
        for init_results in textsearch_response["results"]:
            if init_results["place_id"] not in place_id:
                print("add " + search_keyword + " " + search_type, init_results["name"])

                rating.append(init_results["rating"]) if "rating" in init_results else rating.append(-1)
                restaurants.append(init_results["name"]) if "name" in init_results else restaurants.append(np.nan)
                reviews.append(
                    init_results["user_ratings_total"]) if "user_ratings_total" in init_results else reviews.append(-1)
                price_level.append(
                    init_results["price_level"]) if "price_level" in init_results else price_level.append(-1)
                address.append(init_results["vicinity"]) if "vicinity" in init_results else address.append(np.nan)
                place_id.append(init_results["place_id"]) if "place_id" in init_results else place_id.append(np.nan)
                lat.append(init_results["geometry"]["location"]["lat"]) if "geometry" in init_results else lat.append(
                    np.nan)
                lng.append(init_results["geometry"]["location"]["lng"]) if "geometry" in init_results else lng.append(
                    np.nan)

        # extend with nearby search
        place_id, restaurants, rating, price_level, address, lat, lng, reviews = nearby_search(gapi, place_id,
                                                                                               restaurants, rating,
                                                                                               price_level, address,
                                                                                               lat, lng,
                                                                                               reviews)

        # go to next page
        if "next_page_token" in textsearch_response:
            sleep(np.random.normal(5, 0.1, 1))
            textsearch_nextpage = "&pagetoken=" + textsearch_response["next_page_token"]
            textsearch_google_url = textsearch_base + textsearch_other + textsearch_nextpage
            textsearch_response = requests.get(textsearch_google_url).json()
            # print("response: {}".format(textsearch_response))
        else:
            print("textsearch next page not found in {}, response: {}".format(page, textsearch_response["status"]))
            break

    print("text search done...")

    data_textsearch = {"Name": restaurants, "Rating": rating, "Reviews": reviews,
                       "Price level": price_level, "Address": address, "Place ID": place_id,
                       "lat": lat, "lng": lng}
    df_textsearch = pd.DataFrame(data=data_textsearch)
    df_textsearch.to_csv(search_keyword + "_" + search_type + ".csv")

    print(len(data_textsearch["Name"]),
          len(data_textsearch["Rating"]),
          len(data_textsearch["Reviews"]),
          len(data_textsearch["Price level"]),
          len(data_textsearch["Address"]),
          len(data_textsearch["Place ID"]))


# google map styles:
all_off = """[
    {
        "featureType": "all",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    }
]"""

styles = """[{"featureType":"administrative",
              "elementType":"all",
              "stylers":[{"visibility":"off"},{"lightness":33}]},
             {"featureType":"landscape", 
              "elementType":"all", 
              "stylers":[{"color":"#f2e5d4"}]},
             {"featureType":"poi.park", 
              "elementType":"geometry",
              "stylers":[{"color":"#c5dac6"}]},
             {"featureType":"poi.park",
              "elementType":"labels", 
              "stylers":[{"visibility":"off"},{"lightness":20}]},
             {"featureType":"road",
              "elementType":"all",
              "stylers":[{"lightness":20}]},
             {"featureType":"road.highway",
              "elementType":"geometry",
              "stylers":[{"color":"#c5c6c6"}]},
             {"featureType":"road.arterial",
              "elementType":"geometry", 
              "stylers":[{"color":"#e4d7c6"}]}, 
             {"featureType":"road.local",
              "elementType":"geometry",
              "stylers":[{"color":"#fbfaf7"}]},
             {"featureType":"water",
              "elementType":"all", 
              "stylers":[{"visibility":"off"},{"color":"#acbcc9"}]}]"""

location_source = ColumnDataSource(
    data=dict(
        restaurants=df_textsearch['Name'],
        rating=df_textsearch['Rating'],
        price_level=df_textsearch['Price level'],
        reviews=df_textsearch['Reviews'],
        lat=df_textsearch['lat'],
        lon=df_textsearch['lng'],
    ))


output_file(search_keyword + "_" + search_type + ".html", mode="inline")
map_options = GMapOptions(lat=latitude, lng=longitude, map_type="terrain", zoom=14, styles=all_off)
plot = figure()
plot = gmap(google_api_key=gapi, map_options=map_options)
plot.title.text = search_keyword + "_" + search_type
circle = glyphs.Circle(x="lon", y="lat", size=10, fill_color=Spectral6[0], fill_alpha=0.8, line_color=None)

plot.add_glyph(location_source, circle)
plot.width = 1024
plot.height = 768

# default already set
#plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())

# you can add additional layers
# circle_m = glyphs.Circle(x="lon", y="lat", fill_color="purple",size=10)
# legend = Legend(legends=[("add somethíng else from results",[cpm])])
# plot.add_layout(legend)

plot.add_tools(HoverTool(tooltips=[('Restaurants', '@restaurants'),
                                   ('Rating', '@rating'),
                                   ('Reviews', '@reviews'),
                                   ('Price level', '@price_level'), ]))

show(plot)
