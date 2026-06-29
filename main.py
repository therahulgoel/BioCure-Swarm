import os
import time
from dotenv import load_dotenv

# Load local environment variables from .env file securely
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agent.multi_agent_pipeline import run_pipeline

app = Flask(__name__)
CORS(app)

# Serve the dashboard static files
@app.route('/')
def index():
    return send_from_directory('dashboard', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('dashboard', path)

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        image_base64 = data.get('image')

        start_time = time.time()
        
        # Execute the multi-agent pipeline
        analysis_result, logs = run_pipeline(prompt, image_url=image_base64)
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        # Calculate simulated metrics based on output size
        tokens_approx = len(analysis_result) / 4
        tokens_per_sec = round(tokens_approx / duration) if duration > 0 else 1500

        return jsonify({
            "analysis": analysis_result,
            "logs": logs,
            "time": duration,
            "tokens_per_sec": tokens_per_sec
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Changed port to 8080 because 5000 is often blocked by macOS AirPlay Receiver ( causing 403/Address in use)
    print("⚡ BioCure Swarm Server starting on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)