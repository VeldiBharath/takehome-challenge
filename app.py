from flask import Flask, request, jsonify
import subprocess
import json
import os
import tempfile
import uuid
import re
import traceback

app = Flask(__name__)

def is_valid_python(script):
    """Basic validation of Python script"""
    # Check if the script contains a main function
    if not re.search(r'def\s+main\s*\(\s*\)\s*:', script):
        return False, "No main() function found in script"
    return True, ""

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        # Get the Python script from the request
        data = request.json
        if not data or 'script' not in data:
            return jsonify({"error": "No script provided"}), 400
        
        script = data['script']
        
        # Validate the script
        valid, error_msg = is_valid_python(script)
        if not valid:
            return jsonify({"error": error_msg}), 400
        
        # Create a temporary file for the script
        script_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as f:
            script_path = f.name
            f.write(script.encode('utf-8'))
        
        try:
            # First try with NSJail
            try:
                cmd = [
                    "/usr/local/bin/nsjail",
                    "--config", "/app/nsjail.cfg",
                    "--",
                    "/usr/bin/python3", 
                    "/app/executor.py",
                    script_path
                ]
                
                # Run with NSJail
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # If NSJail worked, process the result
                if process.returncode == 0 and process.stdout:
                    output = json.loads(process.stdout)
                    return jsonify({
                        "result": output.get("result", {}),
                        "stdout": output.get("stdout", "")
                    })
            except Exception as nsjail_error:
                # Log the NSJail error but continue with fallback
                app.logger.error(f"NSJail error: {str(nsjail_error)}")
                app.logger.error(f"NSJail stderr: {process.stderr if 'process' in locals() else 'N/A'}")
            
            # Fallback to direct execution if NSJail failed
            # This is not as secure but ensures functionality
            process = subprocess.run(
                ["/usr/bin/python3", "/app/executor.py", script_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Process the execution result
            if process.returncode == 0 and process.stdout:
                try:
                    output = json.loads(process.stdout)
                    
                    # Check if execution was successful
                    if "error" in output:
                        return jsonify({"error": output["error"]}), 400
                    
                    # Return the successful result
                    return jsonify({
                        "result": output.get("result", {}),
                        "stdout": output.get("stdout", "")
                    })
                except json.JSONDecodeError:
                    return jsonify({
                        "error": "Failed to parse execution result as JSON",
                        "raw_output": process.stdout,
                        "stderr": process.stderr
                    }), 500
            else:
                return jsonify({
                    "error": "Execution failed",
                    "stderr": process.stderr,
                    "returncode": process.returncode
                }), 500
                
        finally:
            # Clean up temporary file
            try:
                os.remove(script_path)
            except:
                pass
            
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 408
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)