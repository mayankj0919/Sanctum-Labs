from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pipeline import run_pipeline, generate_phases_stream
from vision_parser import parse_floor_plan
import data

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)


import json
import uuid
import time
import threading
import subprocess
import re
from blockchain import store_hash_on_stellar

def stream_with_blockchain(generator):
    for chunk in generator:
        if not chunk.strip():
            continue
            
        try:
            data = json.loads(chunk)
            if data.get("phase") == "final" and "report_hash" in data:
                project_id = f"PRJ_{int(time.time())}"
                
                data["blockchain"] = {
                    "status": "pending",
                    "project_id": project_id,
                    "tx_hash": "processing_async",
                    "explorer_link": "https://stellar.expert/explorer/testnet",
                    "error": None
                }
                
                # Pipeline priority: yield immediately
                yield json.dumps(data) + "\n"
                
                # Background upload: fire-and-forget
                def run_blockchain_task(pid, hash_val):
                    res = store_hash_on_stellar(pid, hash_val)
                    try:
                        print(f"Blockchain result for {pid}:", res)
                    except:
                        pass
                        
                try:
                    print(f"Storing hash to Stellar for {project_id}...")
                except:
                    pass
                threading.Thread(target=run_blockchain_task, args=(project_id, data["report_hash"])).start()

            else:
                yield chunk
        except json.JSONDecodeError:
            yield chunk

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if request.is_json:
            req_data = request.get_json()
            if "rooms" not in req_data or "walls" not in req_data:
                return jsonify({"error": "Missing 'rooms' or 'walls' in JSON payload"}), 400
            
            return Response(stream_with_blockchain(generate_phases_stream(req_data)), mimetype="application/x-ndjson")
            
        elif 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
            
            try:
                parsed_data = parse_floor_plan(image_data)
            except Exception as parse_error:
                print(f"Vision parsing error: {parse_error}")
                parsed_data = {
                    "rooms": data.rooms,
                    "walls": data.walls
                }
            
            return Response(stream_with_blockchain(generate_phases_stream(parsed_data)), mimetype="application/x-ndjson")
            
        else:
            return jsonify({"error": "Unsupported Content-Type"}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/verify/<project_id>', methods=['GET'])
def verify_hash(project_id):
    try:
        contract_id = "CDLIC3HMOLOBD5E3BZSKLENWZZ52LGUDW5YGFNWJHVAHZKK7XFIDHDDJ"
        cmd = (
            r'"C:\Program Files (x86)\Stellar CLI\stellar.exe" contract invoke '
            f"--id {contract_id} "
            f"--network testnet "
            f"--source deployer "
            f"-- get_hash "
            f"--project_id {project_id}"
        )
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        clean_output = result.stdout.encode("ascii", "ignore").decode().strip()
        
        if result.returncode == 0:
            match = re.search(r'"([a-fA-F0-9]{64})"', clean_output)
            if match:
                stored_hash = match.group(1)
            else:
                lines = [l for l in clean_output.split('\n') if l.strip()]
                stored_hash = lines[-1].strip('"') if lines else clean_output.strip('"')
            
            return jsonify({
                "status": "verified",
                "project_id": project_id,
                "stored_hash": stored_hash
            })
        else:
            clean_error = result.stderr.encode("ascii", "ignore").decode().strip()
            return jsonify({
                "status": "not_found",
                "project_id": project_id,
                "error": clean_error or clean_output
            })
            
    except Exception as e:
        return jsonify({
            "status": "not_found",
            "project_id": project_id,
            "error": str(e).encode("ascii", "ignore").decode()
        })


if __name__ == '__main__':
    print("Starting PLANWISE Backend Server on port 5000...")
    app.run(port=5000, debug=True)
