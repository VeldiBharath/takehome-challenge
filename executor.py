import sys
import json
import importlib.util
import traceback
import io
import contextlib

def execute_script(script_path):
    # Capture stdout
    stdout_buffer = io.StringIO()
    
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location("user_script", script_path)
        user_module = importlib.util.module_from_spec(spec)
        
        # Capture stdout during execution
        with contextlib.redirect_stdout(stdout_buffer):
            spec.loader.exec_module(user_module)
            
            # Execute the main function
            if hasattr(user_module, 'main'):
                result = user_module.main()
                
                # Verify result is JSON serializable
                try:
                    json.dumps(result)
                except (TypeError, OverflowError):
                    return json.dumps({
                        "error": "main() function must return JSON serializable data"
                    })
                
                return json.dumps({
                    "result": result,
                    "stdout": stdout_buffer.getvalue()
                })
            else:
                return json.dumps({
                    "error": "No main() function found in script"
                })
    except Exception as e:
        # Return the error message and traceback
        error_msg = str(e)
        tb = traceback.format_exc()
        return json.dumps({
            "error": error_msg,
            "traceback": tb,
            "stdout": stdout_buffer.getvalue()
        })

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: executor.py <script_path>"}))
        sys.exit(1)
    
    script_path = sys.argv[1]
    result = execute_script(script_path)
    print(result)