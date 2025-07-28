from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    print(f"Scanning URL: {url}")
    # Run wcag_checker.py and capture output
    result = subprocess.run(['python', 'wcag_checker.py', url], capture_output=True, text=True, cwd=os.getcwd())
    print(f"Subprocess return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    if result.returncode != 0:
        return jsonify({"error": "Scan failed", "details": result.stderr}), 500
    
    # Parse the stdout to find the JSON report path
    stdout_lines = result.stdout.strip().split('\n')
    report_path = None
    for line in stdout_lines:
        if line.startswith("Full JSON report saved:"):
            report_path = line.replace("Full JSON report saved:", "").strip()
            break
    
    if report_path and os.path.exists(report_path):
        with open(report_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Report not found", "path": report_path or "Not detected"}), 500

if __name__ == '__main__':
    app.run(debug=True)