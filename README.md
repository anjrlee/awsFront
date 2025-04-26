# Bedrock Chatbox Application

This is a simple chatbox application that uses Amazon Bedrock as the backend AI service. The application consists of a frontend web interface and a backend API server.

## Project Structure

```
.
├── frontend/
│   ├── index.html      # Main HTML file for the chat interface
│   ├── styles.css      # CSS styles for the chat interface
│   ├── script.js       # JavaScript for handling chat functionality
│   └── server.js       # Simple Node.js server to serve the frontend files
├── backend/
│   ├── app.py          # Flask application that integrates with Amazon Bedrock
│   └── requirements.txt # Python dependencies
├── .env.example        # Template for environment variables
└── start.sh           # Script to start both frontend and backend servers
```

## Prerequisites

- Python 3.7+
- Node.js
- AWS credentials configured with access to Amazon Bedrock

## Environment Variables Setup

Before running the application, you need to set up your AWS credentials for Amazon Bedrock. The application supports three methods:

### Method 1: Using a .env file (Recommended)

1. Copy the `.env.example` file to create a new `.env` file:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```

3. The `start.sh` script will automatically load these environment variables when you run the application.

### Method 2: System Environment Variables

You can also set environment variables directly in your system:

1. For Linux/macOS:
   ```
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```

2. For Windows Command Prompt:
   ```
   set AWS_ACCESS_KEY_ID=your_access_key
   set AWS_SECRET_ACCESS_KEY=your_secret_key
   set AWS_REGION=us-east-1
   ```

3. For Windows PowerShell:
   ```
   $env:AWS_ACCESS_KEY_ID="your_access_key"
   $env:AWS_SECRET_ACCESS_KEY="your_secret_key"
   $env:AWS_REGION="us-east-1"
   ```

### Method 3: AWS Credentials File

If you have the AWS CLI installed, you can configure your credentials using:

```
aws configure
```

This will create or update the credentials file at `~/.aws/credentials`.

### Testing Your Environment Variables

To verify that your environment variables are set up correctly, you can run:

```
./start.sh test-env
```

This will check if your AWS credentials are properly configured and can be accessed by the application.

## Running the Application

1. Make the start script executable:
   ```
   chmod +x start.sh
   ```

2. Run the start script:
   ```
   ./start.sh
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## Stopping the Application

Press `Ctrl+C` in the terminal where you started the application to stop both servers.

## Customization

- To change the Bedrock model, modify the `modelId` parameter in the `invoke_model` function in `backend/app.py`.
- To adjust the AI response parameters, modify the `temperature`, `max_tokens_to_sample`, and other parameters in the same function.



