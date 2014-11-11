# ArcGIS REST Query 

A simple library that can download a layer from a map in an 
ArcGIS web service and convert it to something useful,
like GeoJSON.

### TODO:
- Download all data (loop through with offsets until we get all the data)

## Usage:

```python
>>> import arcgis
>>> arc = arcgis.ArcGIS("http://www.pathtomapserver:6080/", "FOLDER_OF_PROJECTS", "MAP_DATA_I_WANT")
>>> layer_id = 1
>>> arc.get(layer_id)
```
Right now it will only download up to 1000 features from the layer, but it does return it as real,
honest-to-God GeoJSON.

You can also use the included arcgis-get utility, like so:

```bash
./arcgis-get.py http://tigerweb.geo.census.gov/ Basemaps CommunityTIGER 9 > ~/Desktop/railroads.json
```

This will download a Railroads layer from the US Census' TIGER dataset.

## Piping to geojsonio

If you install [geojsonio-cli](https://github.com/mapbox/geojsonio-cli/), you can pipe output directly to a viewable map.

```bash
npm install -g geojsonio-cli
```

Then, we could re-do the previous query:

```bash
./arcgis-get.py http://tigerweb.geo.census.gov/ Basemaps CommunityTIGER 9 | geojsonio
```

And get some glorious mapped output: 
![geojsonio-example](https://cloud.githubusercontent.com/assets/20067/4998565/6be2e4f8-69a7-11e4-8aa1-d735bd1a7dac.png)


This assumes you've inspected your ArcGIS services endpoint to know what to look for.
ArcGIS DOES publish json files enumerating the endpoints you can query, so autodiscovery
could be possible further down the line.
