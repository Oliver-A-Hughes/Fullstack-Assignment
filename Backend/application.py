from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
import pymongo
import random
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS (app)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.trackDB             # select the database
race_tracks = db.raceTracks     # select the track collection
suggestions = db.suggestions    # select the suggestions collection

@app.route("/api/v1.0/racetracks", methods=["GET"])
def display_tracks():
    #Pagination properties.
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    page_start = (page_size * (page_num-1))

    #Sorting properties.
    sort_by = "name"
    order = pymongo.ASCENDING
    if request.args.get('sort'):
        sort_by = str(request.args.get('sort'))
    if request.args.get('order'):
        if str(request.args.get('order')) == 'descending':
            order = pymongo.DESCENDING

    #Filter properties.
    category = None
    value = None
    if request.args.get('category'):
        category = str(request.args.get('category'))
    if request.args.get('value'):
        value = str(request.args.get('value'))
  
    data_to_return = []

    #Get applicable data if a filter has been applied
    if category != None and value != None:
        for track in race_tracks.find( { category: { "$regex": value } }, \
            {"name":1, "location":1, "country":1, "type":1, "events":1, "length":1, "turns":1, "imageURL":1}) \
            .sort(sort_by, order).skip(page_start).limit(page_size):
            track['_id'] = str(track['_id'])
            for event in track['events']:
                event['_id'] = str(event['_id'])
            data_to_return.append(track)

    #Get all data if no filter has been applied
    else:
        for track in race_tracks.find( {}, \
            {"name":1, "location":1, "country":1, "type":1, "events":1, "length":1, "turns":1, "imageURL":1}) \
            .sort(sort_by, order).skip(page_start).limit(page_size):
            track['_id'] = str(track['_id'])
            for event in track['events']:
                event['_id'] = str(event['_id'])
            data_to_return.append(track)

    return make_response(jsonify(data_to_return),200)

@app.route("/api/v1.0/racetracks/names", methods=["GET"])
def get_all_track_names():

    data_to_return = []
    for track in race_tracks.find( {}, \
            {"name":1}) \
                .sort("name", pymongo.ASCENDING):
            track['_id'] = str(track['_id'])
            data_to_return.append(track)
    
    return make_response(jsonify(data_to_return),200)

@app.route("/api/v1.0/racetracks/total", methods=['GET'])
def number_of_tracks():
    #Sorting properties.
    sort_by = "name"
    order = pymongo.ASCENDING
    if request.args.get('sort'):
        sort_by = str(request.args.get('sort'))
    if request.args.get('order'):
        if str(request.args.get('order')) == 'descending':
            order = pymongo.DESCENDING

    #Filter properties.
    category = None
    value = None
    if request.args.get('category'):
        category = str(request.args.get('category'))
    if request.args.get('value'):
        value = str(request.args.get('value'))
  
    data_to_return = []

    #Get applicable data if a filter has been applied
    if category != None and value != None:
        for track in race_tracks.find( { category: { "$regex": value } }, \
            {"name":1, "location":1, "country":1, "type":1, "events":1}) \
            .sort(sort_by, order):
            track['_id'] = str(track['_id'])
            for event in track['events']:
                event['_id'] = str(event['_id'])
            data_to_return.append(track)

    #Get all data if no filter has been applied
    else:
        for track in race_tracks.find( {}, \
            {"name":1, "location":1, "country":1, "type":1, "events":1}) \
            .sort(sort_by, order):
            track['_id'] = str(track['_id'])
            for event in track['events']:
                event['_id'] = str(event['_id'])
            data_to_return.append(track)
    total = []
    total.append({"total": len(data_to_return)})
    return make_response(jsonify(total),200)

@app.route("/api/v1.0/racetracks/random", methods=['GET'])
def get_random_track():
    tracks = []
    data_to_return = []
    for track in race_tracks.find( {}, \
            {"name":1, "location":1, "country":1, "type":1, "events":1, 
            "length":1, "turns":1, "imageURL":1}):
            track['_id'] = str(track['_id'])
            for event in track['events']:
                event['_id'] = str(event['_id'])
            tracks.append(track)
    tracks_limit = len(tracks) - 1
    random_track = random.randint(0, tracks_limit)
    data_to_return.append(tracks[random_track])
    
    return make_response(jsonify(data_to_return),200)

@app.route("/api/v1.0/racetracks/<string:track_id>", methods=["GET"])
def display_one_track(track_id):
    error = validate_trackID(track_id)
    if error != None:
        return error

    track = race_tracks.find_one({'_id':ObjectId(track_id)}, {"name":1, "location":1, "country":1, "type":1, 
                                                                "length":1, "turns":1, "events":1, "imageURL":1})
    data_to_return = []
    track['_id'] = str(track['_id'])
    for event in track['events']:
        event['_id'] = str(event['_id'])
    data_to_return.append(track) 
    return make_response( jsonify( data_to_return ), 200 )

@app.route("/api/v1.0/racetracks", methods=["POST"])
def add_track():
    #Check all required information is in form.
    form_error = validate_track_form(request.form)
    if form_error != None:
        return form_error

    #Get track values from form.
    new_track = { "_id" : ObjectId(),
                   "name" : request.form["name"],
                   "location" : request.form["location"],
                   "country" : request.form["country"],
                   "type" : request.form["type"],
                   "turns" : request.form["turns"],
                   "length" : request.form["length"],
                   "imageURL" : request.form["imageURL"],
                   "events" : []
                 }
    
    #Add race track to the database and return the track URL.
    new_track_id = race_tracks.insert_one(new_track)
    new_track_link = "http://localhost:5000/api/v1.0/racetracks/" + str(new_track_id.inserted_id)
    return make_response( jsonify({"url": new_track_link} ), 201)

@app.route("/api/v1.0/racetracks/<string:track_id>", methods=["PUT"])
def edit_track(track_id):
    #Check TrackID is valid and all required information is in form.
    track_error = validate_trackID(track_id)
    if track_error != None:
        return track_error
    form_error = validate_track_form(request.form)
    if form_error != None:
        return form_error

    #Get updated values for race track
    race_tracks.update_one({"_id" :ObjectId(track_id)},{
            "$set" : {"name" : request.form["name"],
                      "location" : request.form["location"],
                      "country" : request.form["country"],
                      "type" : request.form["type"],
                      "turns" : request.form["turns"],
                      "length" : request.form["length"],
                      "imageURL": request.form["imageURL"]
                    }
    })

    #Return URL of updated race track
    edited_track_link = "http://localhost:5000/api/v1.0/racetracks/" + track_id 
    return make_response (jsonify ( {"url":edited_track_link} ),200)   

@app.route("/api/v1.0/racetracks/<string:track_id>", methods=["DELETE"])
def delete_track(track_id):
    error = validate_trackID(track_id)
    if error != None:
        return error

    race_tracks.delete_one( { "_id" : ObjectId(track_id) } )
    return make_response( jsonify( {} ),204)

@app.route("/api/v1.0/racetracks/<string:track_id>/events", methods=["GET"])
def display_events(track_id):
    error = validate_trackID(track_id)
    if error != None:
        return error

    #Filter properties.
    category = None
    value = None
    if request.args.get('category'):
        category = str(request.args.get('category'))
    if request.args.get('value'):
        value = str(request.args.get('value'))

    data_to_return = []
    track = race_tracks.find_one( {"_id" : ObjectId(track_id)}, {"events" : 1, "_id" : 0})

    #Get applicable data if a filter has been applied
    if category != None and value != None:
        for event in track["events"]:
            event["_id"] = str(event["_id"])
            if event[category] == value:
                data_to_return.append(event)

    #Get all data if not filter has been applied
    else:
        for event in track["events"]:
            event["_id"] = str(event["_id"])
            data_to_return.append(event)

    #Sort the gathered data by date (earliest first)
    data_to_return.sort(key=sort_events_by_date)
    return make_response( jsonify (data_to_return),200)

@app.route("/api/v1.0/racetracks/<string:track_id>/events/<string:event_id>", methods=["GET"])
def display_one_event(track_id, event_id,):
    #Check TrackID and EventID are valid.
    track_error = validate_trackID(track_id)
    if track_error != None:
        return track_error
    event_error = validate_eventID(event_id)
    if event_error != None:
        return event_error

    data_to_return =[]

    #Retrieve event.
    track = race_tracks.find_one( { "events._id" : ObjectId(event_id) }, { "_id" : 0, "events.$" : 1 } )    
    track['events'][0]['_id'] = str(track['events'][0]['_id'])
    data_to_return.append(track)
    return make_response( jsonify( data_to_return ), 200)

@app.route("/api/v1.0/inbox/events", methods=["GET"])
def get_event_suggestions():
    data_to_return = []
    for event in suggestions.find( { "suggestionType": { "$regex": "Event" } }, \
            {"suggestionType":1, "track":1, "trackID":1, "event":1, "series":1, "date":1, "time":1, "notes":1}):
            event['_id'] = str(event['_id'])
            data_to_return.append(event)

    return make_response(jsonify(data_to_return),200)

@app.route("/api/v1.0/inbox/events/<string:event_id>", methods=["GET"])
def get_single_event_suggestion(event_id):
    event = suggestions.find_one({'_id':ObjectId(event_id)}, {"event":1, "series":1, "date":1, "time":1, "notes":1})
    data_to_return = []
    event['_id'] = str(event['_id'])
    data_to_return.append(event) 
    return make_response( jsonify( data_to_return ), 200 )

@app.route("/api/v1.0/inbox/tracks/<string:track_id>", methods=["GET"])
def get_single_track_suggestion(track_id):
    track = suggestions.find_one({'_id':ObjectId(track_id)}, {"name":1, "location":1, "country":1, "type":1, 
                                                                "length":1, "turns":1, "imageURL":1})
    data_to_return = []
    track['_id'] = str(track['_id'])
    data_to_return.append(track) 
    return make_response( jsonify( data_to_return ), 200 )

@app.route("/api/v1.0/inbox/tracks", methods=["GET"])
def get_track_suggestions():
    data_to_return = []
    for track in suggestions.find( { "suggestionType": { "$regex": "Track" } }, \
            {"name":1, "location":1, "country":1, "type":1, "turns":1, "length":1, "imageURL":1}):
            track['_id'] = str(track['_id'])
            data_to_return.append(track)
    
    return make_response(jsonify(data_to_return),200)

@app.route("/api/v1.0/inbox/events", methods=["POST"])
def add_event_suggestion():
    #Get event suggestion from form.
    new_event_suggestion = { "_id" : ObjectId(),
                             "suggestionType": request.form["suggestionType"],
                             "track": request.form["trackName"],
                             "trackID": request.form["trackID"],
                             "event" : request.form["event"],
                             "series" : request.form["series"],
                             "date" : request.form["date"],
                             "time" : request.form["time"],
                             "notes" : request.form["notes"]
                 }
    
    #Add event suggestion to inbox. 
    new_suggestion_id = suggestions.insert_one(new_event_suggestion)
    new_event_suggestion_link = "http://localhost:5000/api/v1.0/inbox/events/" + str(new_suggestion_id.inserted_id)
    return make_response( jsonify({"url": new_event_suggestion_link} ), 201)

@app.route("/api/v1.0/inbox/tracks", methods=["POST"])
def add_track_suggestion():
   #Get track values from form.
    new_track_suggestion = { "_id" : ObjectId(),
                   "suggestionType": request.form["suggestionType"],
                   "name" : request.form["name"],
                   "location" : request.form["location"],
                   "country" : request.form["country"],
                   "type" : request.form["type"],
                   "turns" : request.form["turns"],
                   "length" : request.form["length"],
                   "imageURL" : request.form["imageURL"]
                 }
    #Add track suggestion to inbox. 
    new_suggestion_id = suggestions.insert_one(new_track_suggestion)
    new_track_suggestion_link = "http://localhost:5000/api/v1.0/inbox/tracks/" + str(new_suggestion_id.inserted_id)
    return make_response( jsonify({"url": new_track_suggestion_link} ), 201)

@app.route("/api/v1.0/inbox/tracks/<string:track_id>", methods=["DELETE"])
def delete_track_suggestion(track_id):
    suggestions.delete_one( { "_id" : ObjectId(track_id) } )
    return make_response( jsonify( {} ),204)

@app.route("/api/v1.0/inbox/events/<string:event_id>", methods=["DELETE"])
def delete_event_suggestion(event_id):
    suggestions.delete_one( { "_id" : ObjectId(event_id) } )
    return make_response( jsonify( {} ),204)

@app.route("/api/v1.0/racetracks/<string:track_id>/events", methods=["POST"])
def add_event(track_id):
    #Check TrackID is valid and all required information is in form.
    track_error = validate_trackID(track_id)
    if track_error != None:
        return track_error
    form_error = validate_event_form(request.form)
    if form_error != None:
        return form_error

    #Get event values from form.
    new_event = { "_id" : ObjectId(),
                   "event" : request.form["event"],
                   "series" : request.form["series"],
                   "date" : request.form["date"],
                   "time" : request.form["time"],
                   "notes" : request.form["notes"]
                 }
    
    #Add event to the race track and return the event URL. 
    race_tracks.update_one( { "_id" : ObjectId(track_id) }, {"$push" : { "events" : new_event } } )
    new_event_link = "http://localhost:5000/api/v1.0/racetracks/" + track_id + "/events/" + str(new_event['_id'])
    return make_response( jsonify( { "url" : new_event_link } ), 201 )

@app.route("/api/v1.0/racetracks/<string:track_id>/events/<string:event_id>", methods=["PUT"])
def edit_event(track_id, event_id):
    #Check TrackID and EventID are valid then check all required information is in form.
    track_error = validate_trackID(track_id)
    if track_error != None:
        return track_error
    event_error = validate_eventID(event_id)
    if event_error != None:
        return event_error
    form_error = validate_event_form(request.form)
    if form_error != None:
        return form_error

    #Get edited event values from form.
    edited_event = {"events.$.event" : request.form["event"],
                   "events.$.series" : request.form["series"],
                   "events.$.date" : request.form["date"],
                   "events.$.time" : request.form["time"],
                   "events.$.notes" : request.form["notes"]
                 }
    
    #Edit event and return event URL
    race_tracks.update_one( { "events._id" : ObjectId(event_id) }, { "$set" : edited_event } )
    edited_event_url = "http://localhost:5000/api/v1.0/racetracks/" +  track_id + "/events/" + event_id 
    return make_response( jsonify( {"url":edited_event_url} ), 200)

@app.route("/api/v1.0/racetracks/<string:track_id>/events/<string:event_id>", methods=["DELETE"])
def delete_event(track_id, event_id):
    #Check TrackID is valid and all required information is in form.
    track_error = validate_trackID(track_id)
    if track_error != None:
        return track_error
    event_error = validate_eventID(event_id)
    if event_error != None:
        return event_error

    #Find the event and delete it from the database.
    race_tracks.update_one( { "_id" : ObjectId(track_id) }, { "$pull" : { "events" : { "_id" : ObjectId(event_id) } } } ) 
    return make_response( jsonify( {} ), 204)

def validate_trackID(track_id):
    # Check TrackID is correct length
    if len(track_id) != 24:
        return make_response(jsonify( {"error" : "track ID should be a 24 character hexadecimal string"}), 400)
    
    #Check TrackID is valid hexadecimal
    valid_hex = ['0','1','2','3','4','5','6','7','8','9',
                    'A','B','C','D','E','F',
                    'a','b','c','d','e','f']
    for value in track_id:
            if value not in valid_hex:
                return make_response(jsonify( {"error" : "track ID should be a 24 character hexadecimal string"}), 400)
    
    #Check track ID exists in database.
    track = race_tracks.find_one({'_id':ObjectId(track_id)})
    if track is None:
        return make_response(jsonify( {"error" : "invalid track ID"}),404)
    
    #If no errors are found return None
    return None

def validate_eventID(event_id):   
   # Check EventID is correct length. 
    if len(event_id) != 24:
        return make_response(jsonify( {"error" : "event ID should be a 24 character hexadecimal strings"}), 400)

    #Check EventID is valid hexadecimal.
    valid_hex = ['0','1','2','3','4','5','6','7','8','9',
                    'A','B','C','D','E','F',
                    'a','b','c','d','e','f']
    for value in event_id:
            if value not in valid_hex:
                return make_response(jsonify( {"error" : "event ID should be a 24 character hexadecimal string"}), 400)
    
    #Check event ID exists in database.
    track = race_tracks.find_one( { "events._id" : ObjectId(event_id) }, { "_id" : 0, "events.$" : 1 } )
    if track is None:
        return make_response(jsonify( {"error" : "invalid event ID"}),404)
 
    #If no errors are found return null
    return None

def validate_track_form(form):
    if "name" not in form or "location" not in form or "country" not in form or "type" not in form or "turns" not in form \
    or "length" not in form or "imageURL" not in form:
        return make_response( jsonify( { "error" : "Missing form data" } ), 404)
    else:
        return None

def validate_event_form(form):
    if "event" not in form or "series" not in form or "date" not in form or "time" not in form or "notes" not in form:
        return make_response( jsonify( { "error" : "Missing form data" } ), 404)
    else:
        return None

def sort_events_by_date(e):
     return e['date']



if __name__ == "__main__":
    app.run(debug=True)        