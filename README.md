# ArcGIS REST Query 

A simple library that can download a layer from a map in an 
ArcGIS web service and convert it to something useful,
like GeoJSON.

## Usage

```python
>>> import arcgis
>>> arc = arcgis.ArcGIS("http://www.pathtomapserver:6080/", "FOLDER_OF_PROJECTS", "MAP_DATA_I_WANT")
>>> layer_id = 1
>>> arc.get(layer_id)
```

This assumes you've inspected your ArcGIS services endpoint to know what to look for.
ArcGIS DOES publish json files enumerating the endpoints you can query, so autodiscovery
could be possible further down the line.

## Installation

*I should package this on pip soon enough, but for now...*
```bash
# Create a virtual environment (pip install virtualenv if you don't have it already)
virtualenv python-arcgis-rest-query
cd python-arcgis-rest-query
. bin/activate
git clone git@github.com:Schwanksta/python-arcgis-rest-query repo
cd repo
pip install -r requirements.txt
```

## From the command line

You can also use the included arcgis-get utility, like so:

*Note: this query will take a long time, so maybe try one of the other examples below?*
```bash
./arcgis-get.py http://tigerweb.geo.census.gov/ Basemaps CommunityTIGER 9 > ~/Desktop/railroads.geojson
```

This will download a Railroads layer from the US Census' TIGER dataset. 

The size of that file brings up a good point: you should run `--count_only` before downloading an entire dataset, so you can see what you're in store for. 

```bash
$ ./arcgis-get.py http://tigerweb.geo.census.gov/ Basemaps CommunityTIGER 9 --count_only
182149
```
Since we go in batches of 1,000, you're in for over 180 queries to the API.

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

You can also do WHERE filtering from the command line. For example, if you want to get the Census' state shape for just Florida
and display it on geojson.io, you could do:

```bash
./arcgis-get.py --where="NAME = 'Florida'" http://tigerweb.geo.census.gov/ Basemaps CommunityTIGER 28 | geojsonio
```
![florida](https://cloud.githubusercontent.com/assets/20067/5001808/ee233ff6-69c7-11e4-9c3e-245aba847bb5.png)

## Potential pitfalls:

Since you can only query in batches of 1,000, and sometimes these are millions of records, these operations could take a long time. Currently there's no status indicator on the CLI, so run `--count_only` first to see how long you might wait.
