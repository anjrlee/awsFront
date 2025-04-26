from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
FLOW_ID = os.getenv('FLOW_ID')

# 初始化 Bedrock Agent Runtime client
bedrock_runtime_client = boto3.client(
    'bedrock-agent-runtime',
    region_name=AWS_REGION
)

# Flask App init
app = Flask(__name__)
CORS(app)
# Get AWS credentials from environment variables


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Welcome to the API",
        "endpoints": {
            "/api/health": "GET - Health check endpoint",
            "/api/chat": "POST - Chat endpoint"
        }
    })


@app.route('/api/deleteVectorDB', methods=['POST'])
def deleteVectorDB():
    try:
        data = request.json
        vectorDBName = data.get('vectorDBName', '')

        if not vectorDBName:
            return jsonify({"error": "No vectorDBName provided"}), 400

        # 測試硬編碼的回應
        ai_response = "這是測試回應"
        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500<end_of_inser


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


