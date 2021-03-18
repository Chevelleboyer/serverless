from flask import Flask, request
from flask_cors import CORS, cross_origin
from botocore.client import Config
import boto3, json, datetime

app = Flask(__name__)
CORS(app, support_credentials=True)

cross_origin(support_credentials=True)
@app.route("/")
def hello():
	s3 = boto3.resource(
		's3',
		region_name='us-east-1',
		config=Config(signature_version='s3v4')
	)
	s3_client = boto3.client('s3',region_name='us-east-1', config=Config(signature_version='s3v4'))
	bucket = s3.Bucket('s3-bucket-cs493')
	bucket_contents = s3_client.list_objects(Bucket='s3-bucket-cs493')["Contents"]

	songs = []
	for obj in bucket_contents:
		url = s3_client.generate_presigned_url("get_object",
			Params={"Bucket": 's3-bucket-cs493', "Key": obj["Key"]}, ExpiresIn=5000,
		)
		songs.append(url)

	return {
		"statusCode": 200,
		"headers": {
			"Access-Control-Allow-Headers": "Content-Type",
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "OPTIONS,DELETE,PATCH,PUT,POST,GET",
		},
		"body": songs,
	}

@app.route("/genres")
def get_genres():
	ddb_client = boto3.client('dynamodb', region_name="us-west-2")
	genres = ddb_client.query(
		TableName="music",
		KeyConditionExpression='#pk = :pk',
		ExpressionAttributeNames={
			'#pk': 'pk'
		},
		ExpressionAttributeValues={
			':pk': { 'S': 'genre' },
		}
	)
	return json.dumps([genre["name"]["S"] for genre in genres["Items"]])

@app.route("/artists/for/genre")
def get_artists_for_genre():
	genre = request.args.get("genre")
	ddb_client = boto3.client('dynamodb', region_name="us-west-2")
	artists = ddb_client.query(
		TableName="music",
		KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
		ExpressionAttributeNames={
			'#pk': 'pk',
			"#sk": "sk",
		},
		ExpressionAttributeValues={
			':pk': { 'S': 'genre#'+genre },
			':sk': {'S': 'artist'},
		}
	)
	return json.dumps([artist["name"]["S"] for artist in artists["Items"]])

@app.route("/albums/for/artist")
def get_albums_for_artist():
	artist = request.args.get("artist")
	ddb_client = boto3.client('dynamodb', region_name="us-west-2")
	albums = ddb_client.query(
		TableName="music",
		KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
		ExpressionAttributeNames={
			'#pk': 'pk',
			"#sk": "sk",
		},
		ExpressionAttributeValues={
			':pk': { 'S': 'artist#'+artist },
			':sk': {'S': 'album'},
		}
	)
	return json.dumps([album["name"]["S"] for album in albums["Items"]])

@app.route("/songs/for/album")
def get_songs_for_album():
	album = request.args.get("album")
	ddb_client = boto3.client('dynamodb', region_name="us-west-2")
	songs = ddb_client.query(
		TableName="music",
		KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
		ExpressionAttributeNames={
			'#pk': 'pk',
			"#sk": "sk",
		},
		ExpressionAttributeValues={
			':pk': { 'S': 'album#'+album },
			':sk': {'S': 'song'},
		}
	)
	return json.dumps([song["name"]["S"] for song in songs["Items"]])

@app.route("/song")
def get_song():
	song = request.args.get("song")
	ddb_client = boto3.client('dynamodb', region_name="us-west-2")
	song_obj = ddb_client.query(
		TableName="music",
		KeyConditionExpression='#pk = :pk and #sk = :sk',
		ExpressionAttributeNames={
			'#pk': 'pk',
			"#sk": "sk",
		},
		ExpressionAttributeValues={
			':pk': { 'S': 'song' },
			':sk': {'S': song},
		}
	)

	s3_key = song_obj["Items"][0]["s3_key"]["S"]
	s3_client = boto3.client('s3',region_name='us-east-2', config=Config(signature_version='s3v4'))
	url = s3_client.generate_presigned_url("get_object",
		Params={"Bucket": 's3-bucket-cs493', "Key": s3_key}, ExpiresIn=5000,
	)

	return url

cross_origin(support_credentials=True)
@app.route("/play", methods=['POST'])
def play_song():
	client = boto3.client('sqs', region_name="us-east-1")
	response = client.send_message(
		QueueUrl="https://sqs.us-east-1.amazonaws.com/621940852840/pubsubqueue",
		MessageBody=json.dumps(request.json)
	)
	return ""



