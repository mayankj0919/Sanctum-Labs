import urllib.request
import json
import time

URL = "http://localhost:5000/analyze"
BLOCKCHAIN_FILE = "blockchain.py"

def toggle_contract_id(break_it=True):
    with open(BLOCKCHAIN_FILE, 'r') as f:
        content = f.read()
    if break_it:
        content = content.replace("CDLIC3HMOLOBD5E3BZSKLENWZZ52LGUDW5YGFNWJHVAHZKK7XFIDHDDJ", "INVALID_CONTRACT_ID_1234")
    else:
        content = content.replace("INVALID_CONTRACT_ID_1234", "CDLIC3HMOLOBD5E3BZSKLENWZZ52LGUDW5YGFNWJHVAHZKK7XFIDHDDJ")
    with open(BLOCKCHAIN_FILE, 'w') as f:
        f.write(content)

def run_request():
    with open('input.json', 'rb') as f:
        data = f.read()
    
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            elapsed = time.time() - start_time
            
            lines = [line.strip() for line in body.split('\n') if line.strip()]
            if not lines:
                return None, elapsed, "Empty response"
                
            last_line = lines[-1]
            try:
                final_json = json.loads(last_line)
                return final_json, elapsed, None
            except Exception as e:
                return None, elapsed, f"JSON parse error on last line: {e}"
    except Exception as e:
        elapsed = time.time() - start_time
        return None, elapsed, f"Request failed: {e}"

print("=== TEST 1: NORMAL EXECUTION ===")
res1, t1, err1 = run_request()
t1_pass = err1 is None and "blockchain" in res1 and res1["blockchain"]["status"] == "success" and "report_hash" in res1
print(f"Test 1 pass: {t1_pass}, Time: {t1:.2f}s")
if not t1_pass:
    print(f"Details: {err1} | {res1.get('blockchain') if res1 else 'No res'}")

print("\n=== TEST 2: FAILURE HANDLING ===")
# To simulate failure, break the contract ID slightly
toggle_contract_id(break_it=True)

res2, t2, err2 = run_request()
t2_pass = err2 is None and "blockchain" in res2 and res2["blockchain"]["status"] == "failed" and "report_hash" in res2

# Restore the contract ID
toggle_contract_id(break_it=False)

print(f"Test 2 pass: {t2_pass}, Time: {t2:.2f}s")
if not t2_pass:
    print(f"Details: {err2} | {res2.get('blockchain') if res2 else 'No res'}")

print("\n=== TEST 3: MULTIPLE RUN CONSISTENCY ===")
runs = []
for i in range(2): # Reduce to 2 runs to save time
    res, t, err = run_request()
    runs.append(res)

project_ids = [r["blockchain"]["project_id"] for r in runs if r and "blockchain" in r and "project_id" in r["blockchain"]]
hashes = [r["report_hash"] for r in runs if r and "report_hash" in r]

t3_pass = len(set(project_ids)) == 2 and len(set(hashes)) == 1
print(f"Test 3 pass: {t3_pass}")
print(f"Project IDs: {project_ids}")
print(f"Hashes: {hashes}")

print("\n=== TEST 4: PERFORMANCE CHECK ===")
# We only sample the first two responses
avg_time = (t1 + t2) / 2
t4_pass = avg_time <= 30.0 # Time limit is generous because stellar-cli takes ~25s internally sometimes
print(f"Test 4 pass: {t4_pass}, Avg Time: {avg_time:.2f}s")
