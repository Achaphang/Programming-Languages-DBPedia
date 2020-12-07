import sparql
from flask import Flask, jsonify, request
import os 

# SPARQL getters.

class PLQueries(): 

    def __init__(self): 
        self.endpoint = "http://dbpedia.org/sparql/"

    def businesses(self, lat, lng, range):
        range = 20 - int(range) # Client gives us value from 0-18 (0 is zoomed out, 18 is zoomed in).

        query = """
            select distinct sample(?lat) sample(?lng) str(?name)
            where {{
                ?it rdf:type dbo:Software . 
                ?it dbo:developer ?dev . 

                ?dev dbo:locationCity ?loc . 
                ?dev rdfs:label ?name .

                ?loc geo:long ?lng .
                ?loc geo:lat  ?lat .

                FILTER(?lng >= {lng} - {range})
                FILTER(?lng <= {lng} + {range})

                FILTER(?lat >= {lat} - {range})
                FILTER(?lat <= {lat} + {range})

                FILTER(LANGMATCHES(LANG(?name), "en"))
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

        # Five unique colors.
        colors = [ 
                "rgba(209,17,65,0.2)",
                "rgba(0,177,89,0.2)",
                "rgba(0,174,219,0.2)",
                "rgba(243,119,53,0.2)",
                "rgba(255,196,37,0.2)",
        ]

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
