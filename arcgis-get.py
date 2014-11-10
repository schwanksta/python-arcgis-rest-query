#!/usr/bin/env python

import arcgis
import argparse
import json

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Output an ArcGIS web layer as GeoJSON")
	parser.add_argument('url', type=str,
                   help='The base address of the ArcGIS web instance')
	parser.add_argument('folder', type=str,
                   help='The folder containing the map')
	parser.add_argument('map', type=str,
                   help='The map name')
	parser.add_argument('layer', type=int,
                   help='The layer id within the map')

	args = parser.parse_args()

	arc = arcgis.ArcGIS(args.url, args.folder, args.map)
	print json.dumps(arc.get(args.layer))