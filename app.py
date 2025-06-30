from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['todo_db']
collection = db['tasks']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('content')
        due_date = request.form.get('due')
        priority = request.form.get('priority')
        if content:
            collection.insert_one({
                'content': content,
                'done': False,
                'priority': priority,
                'due': due_date,
                'created_at': datetime.now()
            })
        return redirect('/')
    
    query = request.args.get('q')
    if query:
        tasks = collection.find({'content': {'$regex': query, '$options': 'i'}})
    else:
        tasks = collection.find()
    
    total = collection.count_documents({})
    completed = collection.count_documents({'done': True})
    pending = total - completed
    
    return render_template('index.html', tasks=tasks, total=total, completed=completed, pending=pending)

@app.route('/complete/<task_id>')
def complete(task_id):
    collection.update_one({'_id': ObjectId(task_id)}, {'$set': {'done': True}})
    return redirect('/')

@app.route('/delete/<task_id>')
def delete(task_id):
    collection.delete_one({'_id': ObjectId(task_id)})
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
