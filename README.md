# Safe Python Script Execution Service

This service allows users to execute arbitrary Python code safely in a sandbox environment using NSJail. It returns the result of the script's `main()` function along with any stdout output.

## Architecture

- **Flask API**: Handles HTTP requests and responses
- **NSJail**: Provides a secure sandbox for executing Python code
- **Docker**: Containerizes the application for easy deployment

## Getting Started

### Running Locally

1. Build and run the Docker container:

```bash
docker build -t python-executor .
docker run -p 8080:8080 python-executor
```

2. Test the API with a sample request:

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Hello, World!\")\n    return {\"message\": \"Success\"}"}'
```

### Deployed API (Google Cloud Run)

You can test the deployed API using:

```bash
curl -X POST https://python-executor-755076272405.us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Hello, World!\")\n    return {\"message\": \"Success\"}"}'
```

### Example with NumPy and Pandas

```bash
curl -X POST https://python-executor-755076272405.us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import numpy as np\nimport pandas as pd\n\ndef main():\n    print(\"Using NumPy and Pandas\")\n    arr = np.array([1, 2, 3])\n    df = pd.DataFrame({\"A\": arr})\n    return {\"sum\": int(np.sum(arr)), \"shape\": df.shape[0]}"}'
```

## Features

- Executes arbitrary Python code in a secure sandbox
- Returns the result of the `main()` function and stdout output
- Performs input validation
- Provides error handling for malicious scripts
- Includes basic Python libraries (os, pandas, numpy)

## Security

This service uses NSJail to create a secure sandbox for Python script execution. The sandbox:

- Limits CPU usage and execution time (5 seconds)
- Restricts file system access to necessary directories only
- Provides memory limits (1024 MB)
- Uses read-only file system mounts for system directories
- Enforces resource limits to prevent DOS attacks

## Response Format

Successful execution:
```json
{
  "result": {},  // The return value of the main() function
  "stdout": ""   // Any output printed during script execution
}
```

Error during execution:
```json
{
  "error": "Error message"
}
```

## Technical Implementation

The service was built using:
- Flask web framework
- NSJail for secure script execution
- Docker for containerization
- Google Cloud Run for deployment

## GitHub Repository

https://github.com/VeldiBharath/takehome-challenge

## Google Cloud Run URL

https://python-executor-755076272405.us-central1.run.app

## Time to complete

Approximately 3 hours to implement and test the solution.
