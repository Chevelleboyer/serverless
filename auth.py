from firebase_admin import credentials, auth
import firebase_admin, json, os


c = credentials.Certificate("notes-auth-67b0c-firebase-adminsdk-o5o8e-6845f9b277.json")
app = firebase_admin.initialize_app(c)

def handler(event, context):
	token_id = event["headers"]["Authorization"]

	if not token_id:
		return generatePolicy(False)
	try:
		it_works = auth.verify_id_token(token_id)['uid']
		return generatePolicy(True)
	except:
		return generatePolicy(False)

def generatePolicy(allow):
	return {
		"principalId": "token",
		"policyDocument": {
			"Version":"2012-10-17",
			"Statement": {
				"Action": "execute-api:Invoke",
				"Effect": "Allow" if allow else "Deny",
				"Resource": "*",
			},
		},
	}