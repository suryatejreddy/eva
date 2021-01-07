import asyncio
import json
import os
from flask import Flask, request, make_response, send_file
from flask_restful import Resource, Api
from src.server.eva_db_api import connect_async
from create_video import create_video_from_frames

app = Flask(__name__)
api = Api(app)

input = []


class RequestFrames(Resource):
    def post(self):
        
        params = request.get_json()
        #query = create_query(params)
        #query = 'SELECT id,data FROM MyVideo WHERE id < 5;'
        query1 = "CREATE UDF FastRCNNObjectDetector INPUT (Frame_Array NDARRAY (3, 256, 256)) OUTPUT (label TEXT(10)) TYPE Classification IMPL 'src/udfs/fastrcnn_object_detector.py';"
        query2 = "SELECT id, FastRCNNObjectDetector(data) FROM MyVideo WHERE id < 5;"
        #query_list = [query1, query2]
        query_list = [query2]
        frames = asyncio.run(get_frames(query_list))
        print(frames)
        print("calling create video")
        #video = create_video_from_frames(frames._batch)
        #response = make_response(frames.to_json(), 201)
        #curr_directory = os.getcwd()
        #video_path = os.path.join(curr_directory, video)
        #return send_file(video_path, 'video/mp4')
        return json.dumps({'video name': video})
        
async def get_frames(query_list):
    hostname = '0.0.0.0'
    port = 5432
	
    connection = await connect_async(hostname, port)
    cursor = connection.cursor()
    for query in query_list:
        print('Query: %s' % query)
        await cursor.execute_async(query)
        print("executed")
        response = await cursor.fetch_one_async()
        print("got response")
    return response
    

def create_query(req):
	query = "SELECT "
	
	for s in req['select']:
		query = query + s['text'] + ", "
	query = query[:len(query) - 2] + " FROM " + req['from']
	if req['where']:
		query = query + " WHERE "
		for s in req['where']:
			query = query + s['text'] + ", "
		query = query[:len(query) - 2]
	query = query + ";"
	
	return query
	  
api.add_resource(RequestFrames, '/api/queryeva')

if __name__ == '__main__':
    app.run(debug=True)
