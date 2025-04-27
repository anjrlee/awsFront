from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import json
from dotenv import load_dotenv
import uuid
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from datetime import datetime
import base64
import markdown
import re
# Get AWS credentials from environment variables
from datetime import datetime

from PIL import Image
from io import BytesIO

# Load .env

load_dotenv()


S3_BUCKET = os.getenv('S3_BUCKET_NAME')
BEDROCK_KB_ID = os.getenv('BEDROCK_KB_ID')
REGION = os.getenv('AWS_REGION')
BEDROCK_DATASOURCE_ID = os.getenv('BEDROCK_DATASOURCE_ID')
REGION = os.getenv('AWS_REGION')
# FILE="鋼種好吃"
FILE=""


code_string = """
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title("Sine Wave")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

"""

client = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)



# 初始化 Bedrock Agent Runtime client
bedrock_runtime_client = boto3.client(
    'bedrock-agent-runtime',
    region_name=REGION
)

# Flask App init
app = Flask(__name__)
CORS(app)



def img2txt(encoded_image):
    #response ="fake"
    # Create Claude prompt
    claude_input = {
        "anthropic_version": "bedrock-2023-05-31",  # Add this required parameter
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": encoded_image,
                        }
                    },
                    {
                        "type": "text",
                        "text": "請幫我萃取這張圖中的所有文字，回傳純文字即可。",
                    }
                ]
            }
        ],
        "max_tokens": 1024,
    }

    # Model ID depends on the version you enabled
    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(claude_input),
        contentType="application/json",
        accept="application/json"
    )

    # Parse response
    response_body = json.loads(response["body"].read())
    extracted_text = response_body["content"][0]["text"]
    print("圖片中的文字：",extracted_text)
    return extracted_text

def draw_and_save(code_string):
    try:
        # 使用隔離的命名空間執行代碼，避免全局變量衝突
        namespace = {}
        exec(f"import matplotlib.pyplot as plt\nimport numpy as np\n{code_string}", namespace)
        
        # 將 matplotlib 圖保存到內存中的字節數據
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # 將圖像轉換為 base64 編碼
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        
        return encoded_image
    except Exception as e:
        print(f"Error in draw_and_save: {e}")
        return None
    



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
    file_bytes = file.read()
    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
    #print("succeed")
    #print(img2txt(encoded_image))
    global FILE 
    FILE=img2txt(encoded_image)
    return FILE
    #post img2txt(file)


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

def handleChatResponse(response):
    output=""
    print("output1",response)
    for event in response['responseStream']:
        output=event['flowOutputEvent']['content']['document']
        break
        #output = json.loads(output)
    print("output=",output)
   
    return jsonify({
        'response': output,
        'status': 'Flow execution succeeded'
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})



def getChatResponse11(user_input):
    response = bedrock_runtime_client.invoke_flow(
            flowIdentifier="IQJ5LIPWZU",        
            flowAliasIdentifier="SSEL19PR33",   
            inputs = [
                {
                    "nodeName": "FlowInputNode",      
                    "nodeOutputName": "document",        
                    "content": {
                        "document": user_input

                    }
                }
            ]

    )
    print("response", response)
    return response
    




def getChatResponse12(user_input):
    print("user_input",user_input)
    obj = json.loads(user_input.strip('`').strip('json').strip())
    print(obj)
    if not obj['answerable']:
        return jsonify({
            'response': "請確認輸入格式/內容相關、正確",
            'status': 'Flow execution succeeded'
        }), 200
    user_input = "".join(obj['answerable'])
    print("user_input",user_input)
    response = bedrock_runtime_client.invoke_flow(
            flowIdentifier="NPUEQ646G3",        
            flowAliasIdentifier="1VKEITWEXH",   
            inputs = [
                {
                    "nodeName": "FlowInputNode",      
                    "nodeOutputName": "document",        
                    "content": {
                        "document": user_input

                    }
                }
            ]

    )
    print("response",response)
    event_stream = response['responseStream']
    output=""
    for event in event_stream:
        output=event['flowOutputEvent']['content']['document']
        break
    print("output", output)
    # 移除 Markdown 格式的 ```json 區塊
    # 使用正則表達式安全地移除開頭與結尾的區塊符號
    striped_output = re.sub(r'^```json\s*|\s*```$', '', output[0].strip(), flags=re.DOTALL)

    try:
        json_output = json.loads(striped_output)
        answer = json_output.get('Answer', '')
        answer = answer.replace("//", "/")
        html_output = markdown.markdown(answer)
        if "Code_Block" in json_output:
            code_block = json_output["Code_Block"]
            try:
                image_base64 = draw_and_save(code_block)
                if image_base64:
                    html_output += f'<br><img src="data:image/png;base64,{image_base64}" alt="Generated Image">'
                else:
                    html_output += "<br><p>Error generating image from code block.</p>"
            except Exception as e:
                print("Error generating image:", e)
                html_output += "<br><p>Error generating image from code block.</p>"
        return jsonify({
            'response': html_output,
            'status': 'succeeded'
        }), 200
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Failed content:", repr(striped_output))
        return jsonify({
            'error': 'Invalid JSON format in model response.',
            'status': 'failed'
        }), 500



def getChatResponse21(user_input):
    print("user_input1", user_input)
    response = bedrock_runtime_client.invoke_flow(
            flowIdentifier="2KRL9LSKYI",        
            flowAliasIdentifier="V73PBHK8YF",   
            inputs = [
                {
                    "nodeName": "FlowInputNode",      
                    "nodeOutputName": "document",        
                    "content": {
                        "document": user_input

                    }
                }
            ]

    )
    return response



def getChatResponse22(user_input):
    print("user_input2",user_input)
    obj = json.loads(user_input.strip('`').strip('json').strip())
    print(obj)
    if not obj['answerable']:
        return jsonify({
            'response': "請確認輸入格式/內容相關、正確",
            'status': 'Flow execution succeeded'
        }), 200
    user_input = "".join(obj['answerable'])
   
    my_dict = {
            "query":user_input,
            "file_content":FILE
    }
    user_input=str(my_dict)
    print("user_input",user_input)
    response = bedrock_runtime_client.invoke_flow(
            flowIdentifier="NPUEQ646G3",        
            flowAliasIdentifier="1VKEITWEXH",   
            inputs = [
                {
                    "nodeName": "FlowInputNode",      
                    "nodeOutputName": "document",        
                    "content": {
                        "document": user_input

                    }
                }
            ]

    )
    print("response",response)
    event_stream = response['responseStream']
    output=""
    for event in event_stream:
        output=event['flowOutputEvent']['content']['document']
        break
    print(output)

    # 移除 Markdown 格式的 ```json 區塊
    # 使用正則表達式安全地移除開頭與結尾的區塊符號
    striped_output = re.sub(r'^```json\s*|\s*```$', '', output[0].strip(), flags=re.DOTALL)

    try:
        json_output = json.loads(striped_output)
        answer = json_output.get('Answer', '')
        answer = answer.replace("//", "/")
        html_output = markdown.markdown(answer)
        if "Code_Block" in json_output:
            code_block = json_output["Code_Block"]
            try:
                image = draw_and_save(code_block)
                image_path = os.path.abspath(image.filename)
                html_output += f'<br><img src="file://{image_path}" alt="Generated Image">'
            except Exception as e:
                print("Error generating image:", e)
            html_output += "<br><p>Error generating image from code block.</p>"
        return jsonify({
            'response': html_output,
            'status': 'succeeded'
        }), 200
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Failed content:", repr(striped_output))
        return jsonify({
            'error': 'Invalid JSON format in model response.',
            'status': 'failed'
        }), 500
    


@app.route('/api/chat', methods=['POST'])
def chat():
        global FILE 
        data = request.json
        user_input = data.get('message', '')
        if not user_input:
            print("Missing 'inputs' in request")
            return jsonify({"error": "Missing 'message' in request"}), 400
        #print("data=",user_message)
        #user_input = request.json.get('inputs')
        my_dict = {
            "query":user_input,
            "file_content":FILE
        }
        processedInput=str(my_dict)

        if FILE=="":
            response=getChatResponse11(processedInput)
        else:
            response=getChatResponse21(processedInput)

        #print("response",response)
        event_stream = response['responseStream']
        output=""
        #print(type(event_stream))
        for event in event_stream:
            output=event['flowOutputEvent']['content']['document']
            break

        print("output",output)

        if FILE=="":
            return getChatResponse12(output)

        else:
            #print("22")
            return getChatResponse22(output)
            FILE=""



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


