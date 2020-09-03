'''
Instructions:
	use command 'python [file_name]' to run application
	open local url in browser (use this url by default http://127.0.0.1:5000)
		/images - get first page of images
		/images?id=[id] - get detail of image
		/image?page=[page] - get images by page
		/search?searchterm=[searchItem] - image search by text 
'''

import requests
import requests_cache
import json

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

requests_cache.install_cache('photos_cache', backend='sqlite', expire_after=180)

url = 'http://interview.agileengine.com'
apiKey="23567b218376f79d9415"

def GetToken(url, apiKey):
	'''connect to api server and get token'''
	body={"apiKey": apiKey}
	headers = {'content-type': 'application/json'}
	response = requests.post(f'{url}/auth', data=json.dumps(body), headers=headers)
	if(response.ok):
		return response.json()['token']

@app.route('/images')
@app.route('/images/<id>')
@app.route('/images/<int:page>')
def GetApiPhotos(id = None, page = None):
	'''get images by page or get image details'''
	if 'id' in request.args:
		id = request.args['id']
		url_ = f'{url}/images/{id}' 
	elif 'page' in request.args:
		page = int(request.args['page'])
		url_ = f'{url}/images?page={page}'
	else:
		url_ = f'{url}/images'
	response = requests.get(url_, headers={'Authorization': f'Bearer {token}'})
	if(response.ok):
		return jsonify(response.json())

@app.route('/search')
@app.route('/search/<searchterm>')
def Search(searchterm = None):
	'''search by any text'''
	if 'searchterm' in request.args:
		searchTerm = request.args['searchterm']
	else:
		return "Please, provide searchTerm"
	try:
		results = []
		respons = requests.get(f'{url}/images', headers={'Authorization': f'Bearer {token}'})
		if(respons.ok):
			pageCount = int(respons.json()['pageCount'])
		for pageRange in range(1, pageCount):
			pages = requests.get(f'{url}/images?page={int(pageRange)}', headers={'Authorization': f'Bearer {token}'})
			pages = pages.json()
			for page in pages['pictures']:
				info_pic = requests.get(f'{url}/images/{page["id"]}', headers={'Authorization': f'Bearer {token}'})
				info_pic_json = info_pic.json()
				for key in info_pic_json:
					if str(info_pic_json[key]).__contains__(searchTerm):
						results.append(info_pic_json)
		if results:
			return jsonify(results)
		else:
			return 'Nothing found'
	except requests.exceptions.ConnectionError:
		return "Connection refused"
		
	
@app.route('/')
def home():
    return GetToken(url, apiKey)

token = GetToken(url, apiKey)

if __name__ == '__main__':
    app.run(debug=True)