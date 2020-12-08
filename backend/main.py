import sparql
from flask import Flask, jsonify, request
import os
import math
import random
import colorsys

# SPARQL getters.
def generateHSLAtoRGBAColors(saturation, lightness, alpha, amount):
    colors = []
    huedelta = math.trunc(360 / amount)

    for i in range(amount):
        hue = i * huedelta
        decConversion = colorsys.hsv_to_rgb(hue/360, saturation/100, lightness/100)
        rgbastring = "rgba("
        for j in range(3):
            rgbastring += str(round(decConversion[j] * 255)) + ","
        rgbastring += str(alpha) + ")"
        colors.append(rgbastring)

    return colors

class PLQueries():

    def __init__(self):
        self.endpoint = "http://dbpedia.org/sparql/"

    def businesses(self, lat, lng, range):
        range = 20 - int(range) # Client gives us value from 0-18 (0 is zoomed out, 18 is zoomed in).

        query = """
            select distinct sample(?lat) sample(?lng) str(?name) str(?comment)
            where {{
                ?it rdf:type dbo:Software .
                ?it dbo:developer ?dev .

                ?dev dbo:locationCity ?loc .
                ?dev rdfs:label ?name .
                ?dev rdfs:comment ?comment .

                ?loc geo:long ?lng .
                ?loc geo:lat  ?lat .

                FILTER(?lng >= {lng} - {range})
                FILTER(?lng <= {lng} + {range})

                FILTER(?lat >= {lat} - {range})
                FILTER(?lat <= {lat} + {range})

                FILTER(LANGMATCHES(LANG(?name), "en"))
                FILTER(LANGMATCHES(LANG(?comment), "en"))
           }}
            order by ?dev
            limit 100
        """.format(lat=lat, lng=lng, range=range)

        result = sparql.query(self.endpoint, query)
        rows = [sparql.unpack_row(row) for row in result]
        return  rows

    def programming_languages(self, lat, lng, range):
        range = 20 - int(range) # Client gives us value from 0-18 (0 is zoomed out, 18 is zoomed in).

        # NOTE: Grabbing only the TOP FIVE most popular in the specified area.
        query = """
            select distinct replace(str(?name), "\\\\(programming language\\\\)", "") count(?pl) as ?count
            where {{
                ?it dbo:developer ?dev .
                ?it dbo:programmingLanguage ?pl .

                ?pl rdfs:label ?name .

                ?dev dbo:locationCity ?loc .
                ?loc geo:long ?lng .
                ?loc geo:lat  ?lat .

                FILTER(?lng >= {lng} - {range})
                FILTER(?lng <= {lng} + {range})

                FILTER(?lat >= {lat} - {range})
                FILTER(?lat <= {lat} + {range})

                FILTER(LANGMATCHES(LANG(?name), "en"))
            }}
            order by desc(?count)
            limit 5
        """.format(lat=lat, lng=lng, range=range)

        result = sparql.query(self.endpoint, query)
        rows = [sparql.unpack_row(row) for row in result]

        colors = generateHSLAtoRGBAColors(random.randint(20, 80) + (random.randint(0, 999) * 0.001), random.randint(20, 80) + (random.randint(0, 999) * 0.001), 1.0, 5)
        random.shuffle(colors)

        # Format data in special way for frontend.
        return {
                "labels": list(map(lambda row: row[0], rows)),
                "datasets": [{
                    "data": list(map(lambda row: row[1], rows)),
                    "backgroundColor": colors,
                }]
        }

# Server startup code.

app = PLQueries()
server = Flask(__name__)

f = open("./frontend/index.html", mode="r")
indexHTML = f.read()
f.close()

# HTTP routes

@server.route("/")
def hello():
    return indexHTML

@server.route("/programming_languages", methods=['POST'])
def programming_languages():
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    range = request.form.get("range")
    return jsonify(app.programming_languages(lat, lng, range))

@server.route("/businesses", methods=['POST'])
def businesses():
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    range = request.form.get("range")
    return jsonify(app.businesses(lat, lng, range))
