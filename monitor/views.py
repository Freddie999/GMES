from django.shortcuts import render, redirect
import os
import folium
from folium import plugins
import ee
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse

# Create your views here.

## Trigger the authentication flow. You only need to do this once
ee.Authenticate()

# Initialize the library.
ee.Initialize()


# Define a method for displaying Earth Engine image tiles to folium map.
def add_ee_layer(self, eeImageObject, visParams, name):
    map_id_dict = ee.Image(eeImageObject).getMapId(visParams)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict["tile_fetcher"].url_format,
        attr="Map Data &copy; <a href='https://earthengine.google.com/'>Google Earth Engine</a>",
        name=name,
        overlay=True,
        control=True,
    ).add_to(self)


def home(request):

    # Add EE drawing method to folium.
    folium.Map.add_ee_layer = add_ee_layer

    # Fetch an elevation model.
    dem = ee.Image("USGS/SRTMGL1_003")

    # Set visualization parameters.
    visParams = {
        "min": 0,
        "max": 3000,
        "palette": ["225ea8", "41b6c4", "a1dab4", "ffffcc"],
    }

    # Create a folium map object.
    myMap = folium.Map(location=[5.256444, -0.65443], zoom_start=10, height=500)

    # Add the elevation model to the map object.
    myMap.add_ee_layer(dem, visParams, "DEM")

    # Add a layer control panel to the map.
    myMap.add_child(folium.LayerControl())

    # Display the map.
    myMap = myMap._repr_html_()
    context = {"myMap": myMap}
    return render(request, "monitor/home.html", context)


def plotchart():

    # Fetch a Landsat image.

    img = ee.Image("LANDSAT/LT05/C01/T1_SR/LT05_034033_20000913")

    # Select Red and NIR bands, scale them, and sample 500 points.

    samp_fc = img.select(["B3", "B4"]).divide(10000).sample(scale=30, numPixels=500)

    # Arrange the sample as a list of lists.

    samp_dict = samp_fc.reduceColumns(ee.Reducer.toList().repeat(2), ["B3", "B4"])

    samp_list = ee.List(samp_dict.get("list"))

    # Save server-side ee.List as a client-side Python list.

    samp_data = samp_list.getInfo()

    # Display a scatter plot of Red-NIR sample pairs using matplotlib.

    plt.scatter(samp_data[0], samp_data[1], alpha=0.2)

    plt.xlabel("Red", fontsize=12)

    plt.ylabel("NIR", fontsize=12)
    fig = plt.show()

    response = HttpResponse(content_type="image/png")
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(response)
    return response


# plotchart()
