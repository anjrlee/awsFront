from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import json
from dotenv import load_dotenv
import uuid

# Load .env
load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET_NAME')
BEDROCK_KB_ID = os.getenv('BEDROCK_KB_ID')
REGION = os.getenv('AWS_REGION')
BEDROCK_DATASOURCE_ID = os.getenv('BEDROCK_DATASOURCE_ID')


# 初始化 Bedrock Agent Runtime client
bedrock_runtime_client = boto3.client(
    'bedrock-agent-runtime',
    region_name=REGION
)

# Flask App init
app = Flask(__name__)
CORS(app)
# Get AWS credentials from environment variables



def upload_to_s3(file, filename):
    s3 = boto3.client('s3', region_name=REGION)
    s3.upload_fileobj(file, S3_BUCKET, filename)
    return f's3://{S3_BUCKET}/{filename}'

# 啟動知識庫 ingestion 任務
def ingest_to_knowledge_base(s3_uri):
    bedrock = boto3.client('bedrock-agent', region_name=REGION)
    response = bedrock.start_ingestion_job(
        knowledgeBaseId=BEDROCK_KB_ID,
        dataSourceId=BEDROCK_DATASOURCE_ID
    )
    return response

@app.route('/api/upload', methods=['POST'])
def upload_txt_to_bedrock():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = f"{uuid.uuid4()}.txt"

    try:
        s3_uri = upload_to_s3(file, filename)
        print("DEBUG: S3 URI =", s3_uri)
        
        job_id = ingest_to_knowledge_base(s3_uri)
        print("DEBUG: Ingestion Job ID =", job_id)

        return jsonify({
            'message': 'Upload successful',
            's3_uri': s3_uri,
            'ingestion_job_id': job_id
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({'error': 'Upload failed', 'detail': str(e)}), 500


def clear_s3_bucket():
    s3 = boto3.client('s3', region_name=REGION)
    objects = s3.list_objects_v2(Bucket=S3_BUCKET)

    if 'Contents' in objects:
        delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
        s3.delete_objects(Bucket=S3_BUCKET, Delete={'Objects': delete_keys})
        print("DEBUG: Deleted all objects from S3 bucket")
        return len(delete_keys)
    else:
        print("DEBUG: S3 bucket already empty")
        return 0


@app.route('/api/deleteVectorDB', methods=['POST'])
def clear_s3():
    try:
        deleted_count = clear_s3_bucket()
        # update kb
        response = ingest_to_knowledge_base(None)
        return jsonify({
            'message': 'S3 bucket cleared',
            'deleted_objects': deleted_count
        })
    except Exception as e:
        print("ERROR in /clear-s3:", e)
        return jsonify({'error': 'Failed to clear S3 bucket', 'detail': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Welcome to the API",
        "endpoints": {
            "/api/health": "GET - Health check endpoint",
            "/api/chat": "POST - Chat endpoint"
        }
    })






# @app.route('/api/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.json
#         user_message = data.get('message', '')
        
#         if not user_message:
#             return jsonify({"error": "No message provided"}), 400
        
#         # 測試硬編碼的回應
#         ai_response = "這是測試回應"
#         return jsonify({"response": ai_response})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500

    
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"server error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        #print("data=",user_message)
        #user_input = request.json.get('inputs')
        if not user_input:
            print("Missing 'inputs' in request")
            return jsonify({"error": "Missing 'message' in request"}), 400
        response = bedrock_runtime_client.invoke_flow(
            flowIdentifier="Z15IBK17JY",        # Flow ID
            flowAliasIdentifier="6NNORYDLV9",   # ✅ 使用 alias ID，而非 alias 名稱
            inputs = [
                {
                    "nodeName": "FlowInputNode",       # FlowInput 節點固定是這個名稱
                    "nodeOutputName": "document",         # ✅ 這才是你 FlowInput 的輸出名稱
                    "content": {
                        "document": user_input
                    }
                }
            ]

        )

        #print("response",response)
        event_stream = response['responseStream']
        output=""
        #print(type(event_stream))
        
        for event in event_stream:
            output=event['flowOutputEvent']['content']['document']
            break
        return jsonify({
            'response': output,
            'status': 'Flow execution succeeded'
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'Failed to invoke Bedrock Flow'
        }), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


