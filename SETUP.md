# Setup Instructions for Pony Realism on RunPod

## Getting a CivitAI API Key

1. Create an account on [CivitAI](https://civitai.com/) if you don't have one
2. Go to your [Account Settings](https://civitai.com/user/account)
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy the API key for use in the next steps

## Building the Docker Image

### Option 1: Build with API Key (Recommended)

```bash
docker build --build-arg CIVITAI_API_KEY="your_api_key_here" -t your-dockerhub-username/pony-realism-sdxl:latest .
```

### Option 2: Build without API Key

If the model doesn't require authentication, you can build without the API key:

```bash
docker build -t your-dockerhub-username/pony-realism-sdxl:latest .
```

**Note:** Some models on CivitAI require authentication. If the build fails during model download, you'll need to use Option 1 with a valid API key.

## Deploying to RunPod

1. Push your Docker image:
   ```bash
   docker push your-dockerhub-username/pony-realism-sdxl:latest
   ```

2. In RunPod:
   - Go to Serverless > Deploy Worker
   - Select your container image
   - Configure GPU and other settings as needed
   - Deploy

## Runtime Environment Variables (Optional)

If you prefer to set the API key at runtime instead of build time, you can:

1. Remove the model download from the Dockerfile
2. Set `CIVITAI_API_KEY` as an environment variable in RunPod
3. Download the model on first run (this will increase cold start time)

## Troubleshooting

- **403 Forbidden Error**: The model requires authentication. Make sure you're using a valid CivitAI API key.
- **404 Not Found**: Check that the model URL is correct and the model is still available on CivitAI.
- **Connection Timeout**: CivitAI might be experiencing high load. Try building again later.