"""
AI Research Agent - Web Application
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from agent import Agent
from config import WEB_HOST, WEB_PORT


template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
agent = None


def init():
    global agent
    print("Initializing Agent...")
    agent = Agent()
    print("Agent ready!")


@app.route('/')
def home():
    # debug: print where Flask is looking for templates
    print("Template folder:", app.template_folder)
    print("Does it exist?", os.path.exists(app.template_folder))
    print("Files inside:", os.listdir(app.template_folder) if os.path.exists(app.template_folder) else "FOLDER NOT FOUND")
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'error': 'empty question'})

    # Run agent
    result = agent.run(question)

    return jsonify({
        'question': question,
        'answer': result['answer'],
        'steps': result['steps']
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  AI Research Agent")
    print("=" * 50)

    init()

    print("\n" + "=" * 50)
    print("  http://%s:%d" % (WEB_HOST, WEB_PORT))
    print("  Ctrl+C to stop")
    print("=" * 50 + "\n")

    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)