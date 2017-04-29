#!/usr/bin/env python
import argparse
import json
import logging
import sys
from math import asin, cos, floor, sqrt
from random import uniform

import numpy
import requests

import pg
# from nltk.cluster.kmeans import KMeansClusterer

logging.basicConfig(format="%(asctime)-15s ::: %(message)s", stream=sys.stderr, level=logging.DEBUG)

def get_location_viewport(gmapskey, location):
    res = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}'.format(location.replace(" ","+"), gmapskey)).json()
    res = res['results'][0]['geometry']['viewport']
    return {
        "left":res['southwest']['lat'],
        "bottom":res['southwest']['lng'],
        "right":res['northeast']['lat'],
        "top":res['northeast']['lng'],
    }

def day_and_time_to_week_time(day, time):
    return (day or 0)*24*60 + int(time or 0)/100*60 + int(time or 0)%100

def period_to_week_time(period):
    return [
        day_and_time_to_week_time(period['open']['day'], period['open']['time']),
        day_and_time_to_week_time(period['open']['day'], period['close']['time']),
    ]

def get_locations_in_viewport(conn, viewport):
    sql = """
        SELECT ST_AsGeoJSON(location)::json AS loc,
            body->>'name' AS name,
            body->'opening_hours'->'periods' AS periods
        FROM results
        WHERE has_details=TRUE AND location && ST_MakeEnvelope({bottom},{left},{top},{right},4326)
    """.format(**viewport)
    logging.info("running" + sql)
    result = conn.query(sql)
    for loc, name, periods in result.getresult():
        #print loc, name, periods, "\n"
        yield {"loc":loc,"name":name, "periods":periods}

def filter_locations_by_open_time(locations, open_on_day, open_on_hour):
    #First compute the time we want to filter by. Only locations that are open during this time will be returned
    time_of_interest = day_and_time_to_week_time(open_on_day, open_on_hour)
    #we have a time we are interested in filter by it
    for location in locations:
        #print location['name'], location['periods']
        period = (location.get('periods')or[{}])[0] or {}
        if not period.get('open') or not period.get('close'):
            continue
        periods = [period_to_week_time(d) for d in location['periods']]
        periods = [p for p in periods if p[0]<=time_of_interest and p[1] >=time_of_interest]
        if not periods: continue
        yield location

# def latlng_distance(u, v):
#     lon1, lat1 = u
#     lon2, lat2 = v
#     p = 0.017453292519943295
#     a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
#     return 12742 * asin(sqrt(a))

# def do_kmeans(locations):
#     number_of_clusters = len(locations)/4
#     vectors = [numpy.array(l['loc']['coordinates']) for l in locations]
#     clusterer = KMeansClusterer(number_of_clusters, latlng_distance, avoid_empty_clusters=True) #repeats=10
#     logging.info("starting k-means with {} clusters and {} data points".format(number_of_clusters, len(locations)))
#     clusters = clusterer.cluster(vectors, True, trace=False)
#     means = [m.tolist() for m in clusterer.means()]
#     means = [[m[0],m[1],0] for m in means]
#     for c in clusters:
#       means[c][2] += 1
#     return means

def do_jitter(locations, viewport):
    jit_amount_lng = abs(viewport['left']-viewport['right'])*0.01
    jit_amount_lat = abs(viewport['top']-viewport['bottom'])*0.01
    locations = [l['loc']['coordinates'] for l in locations]
    locations = [[
        l[0] + uniform(jit_amount_lng*0.1, jit_amount_lng),
        l[1] + uniform(jit_amount_lat*0.1, jit_amount_lat),
    1] for l in locations]
    return locations

def main(args):
    viewport = get_location_viewport(args.gmapskey, args.location)
    conn = pg.DB(dbname="polygon")
    locations = list(get_locations_in_viewport(conn, viewport))
    logging.info("found {} locations in viewport".format(len(locations)))
    conn.close()
    if args.day is not None and args.time is not None:
        locations = list(filter_locations_by_open_time(locations, args.day, args.time))
    logging.info("found {} locations during {}".format(len(locations), args.time))
    #means = do_kmeans(locations)
    means = do_jitter(locations, viewport)
    print json.dumps({
        "kmeans":means,
        "day":args.day,
        "time":args.time,
        "viewport":viewport,
        "avgValue":numpy.mean([m[2] for m in means])
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='minifies location data with k-means')
    parser.add_argument('--gmapskey', help='Google Maps places API key. Used to get bounding box.',required=True)
    parser.add_argument('--location', help='name of location to make heatmap of',required=True)
    parser.add_argument('--day', help='filters locations to only those open on specified day (0-6)',type=int)
    parser.add_argument('--time', help='filters locations to only those on the given hour (0000-2400)',type=int)
    args = parser.parse_args()
    main(args)
