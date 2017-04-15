#!/usr/bin/env python
import argparse
import requests
import pg
import numpy
from math import cos, asin, sqrt
from nltk.cluster.kmeans import KMeansClusterer

def get_location_viewport(gmapskey, location):
    res = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}'.format(location.replace(" ","+"), gmapskey)).json()
    res = res['results'][0]['geometry']['viewport']
    return {
        "left":res['southwest']['lat'],
        "bottom":res['southwest']['lng'],
        "right":res['northeast']['lat'],
        "top":res['northeast']['lng'],
    }

def convert_period_to_abs_week_time(period):
    return [
        period['open']['day']*24*60 + int(period['open']['time'])/100*60 + int(period['open']['time'])%100,
        period['close']['day']*24*60 + int(period['close']['time'])/100*60 + int(period['close']['time'])%100
    ]

def get_locations_in_viewport(conn, viewport):
    sql = """
        SELECT ST_AsGeoJSON(location)::json AS loc,
            body->>'name' AS name,
            body->'opening_hours'->'periods' AS periods
        FROM results
        WHERE has_details=TRUE AND location && ST_MakeEnvelope({bottom},{left},{top},{right},4326)
    """.format(**viewport)
    print "running", sql
    result = conn.query(sql)
    for loc, name, periods in result.getresult():
        #print loc, name, periods, "\n"
        yield {"loc":loc,"name":name, "periods":periods}

def filter_locations_by_open_time(locations, open_on_day, open_on_hour):
    #First compute the time we want to filter by. Only locations that are open during this time will be returned
    time_of_interest = None
    time_of_interest = open_on_day*24*60
    time_of_interest += int(open_on_hour)/100*60 + int(open_on_hour)%100
    #we have a time we are interested in filter by it
    for location in locations:
        periods = [convert_period_to_abs_week_time(d) for d in locations['periods']]
        periods = [p for p in periods if p[0]<=time_of_interest and p[1] >=time_of_interest]
        if not periods: continue
        yield location

def latlng_distance(u, v):
    lon1, lat1 = u
    lon2, lat2 = v
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))

def do_kmeans(locations, number_of_clusters):
    for l in locations:
        print l['loc']
    vectors = [numpy.array(l['loc']['coordinates']) for l in locations]
    clusterer = KMeansClusterer(number_of_clusters, latlng_distance) #repeats=10
    clusters = clusterer.cluster(vectors, True, trace=True)
    print 'As:', clusters
    print 'Means:', clusterer.means()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='minifies location data with k-means')
    parser.add_argument('--gmapskey', help='Google Maps places API key. Used to get bounding box.',required=True)
    parser.add_argument('--location', help='name of location to make heatmap of',required=True)
    parser.add_argument('--day', help='filters locations to only those open on specified day (0-6)',type=int)
    parser.add_argument('--time', help='filters locations to only those on the given hour (0000-2400)',type=int)
    parser.add_argument('--clusters', help='The number of k-means clusters',type=int, default=50)
    args = parser.parse_args()

    viewport = get_location_viewport(args.gmapskey, args.location)
    conn = pg.DB(dbname="polygon")
    locations = list(get_locations_in_viewport(conn, viewport))
    print "found {} locations in viewport".format(len(locations))
    conn.close()
    if args.day is not None and args.time is not None:
        locations = list(filter_locations_by_open_time(locations, args.day, args.time))
    do_kmeans(locations, args.clusters)
