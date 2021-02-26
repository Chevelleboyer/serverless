import boto3, json

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = s3.Bucket('s3-bucket-cs493')
bucket_contents = bucket.objects.all()

music = {}

payload = []
for obj in bucket_contents:
	song_url = s3_client.generate_presigned_url('get_object',Params={'Bucket':bucket.name,'Key':obj.key}, ExpiresIn=10000000)
	info = obj.key.split("/")
	if len(info) > 2:
		payload.append([info[0], info[1], info[2], song_url])

for artist, album, song, song_url in payload:
	if artist in music:
		if album in music[artist]:
			music[artist][album][song] = song_url
		else:
			music[artist][album] = {song: song_url}
	else:
		music[artist] = {album: {song: song_url}}
