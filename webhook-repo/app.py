from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

app = Flask(__name__)
client = MongoClient(config.MONGO_URI)
db = client.webhook_db
collection = db.events

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event = request.headers.get('X-GitHub-Event')

    # Basic extraction — customize more
    if event == 'push':
        doc = {
            "action_type": "PUSH",
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
            "timestamp": datetime.utcnow()
        }
    elif event == 'pull_request':
        action = data['action']
        pr = data['pull_request']
        if action == 'opened':
            doc = {
                "action_type": "PULL_REQUEST",
                "author": pr['user']['login'],
                "from_branch": pr['head']['ref'],
                "to_branch": pr['base']['ref'],
                "timestamp": datetime.utcnow()
            }
        elif action == 'closed' and pr['merged']:
            doc = {
                "action_type": "MERGE",
                "author": pr['user']['login'],
                "from_branch": pr['head']['ref'],
                "to_branch": pr['base']['ref'],
                "timestamp": datetime.utcnow()
            }
        else:
            return '', 204
    else:
        return '', 204

    collection.insert_one(doc)
    return '', 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1).limit(10))
    for e in events:
        e['_id'] = str(e['_id'])  # remove ObjectId
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
