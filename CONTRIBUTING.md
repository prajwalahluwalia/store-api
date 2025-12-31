# HOW TO CONTRIBUTE

## Run Dockerfile locally
'''
    docker run -dp 5005:5000 -w /app -v "$(pwd):/app" IMAGE_NAME -c "flask run --host 0.0.0.0"
'''