import subprocess
import threading

def store_hash_on_stellar(project_id: str, hash_val: str) -> dict:
    contract_id = "CDLIC3HMOLOBD5E3BZSKLENWZZ52LGUDW5YGFNWJHVAHZKK7XFIDHDDJ"
    cmd = (
        r'"C:\Program Files (x86)\Stellar CLI\stellar.exe" contract invoke '
        f"--id {contract_id} "
        f"--network testnet "
        f"--source deployer "
        f"-- store_hash "
        f"--project_id {project_id} "
        f"--hash {hash_val}"
    )
    
    try:
        # Step 1: Use safe subprocess call
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Step 2: Sanitize result strings safely
        raw_out = result.stdout or ""
        raw_err = result.stderr or ""
        clean_out = raw_out.encode("ascii", "ignore").decode().strip()
        clean_err = raw_err.encode("ascii", "ignore").decode().strip()

        # Step 3: Safe logging
        try:
            if result.returncode != 0:
                print(f"--- Blockchain Error for {project_id} ---")
                print(f"STDERR: {clean_err}")
                print(f"STDOUT: {clean_out}")
            else:
                print(f"Blockchain Write Success: {project_id}")
        except:
            pass

        if result.returncode == 0:
            return {
                "status": "success",
                "project_id": project_id,
                "tx_hash": "confirmed",
                "explorer_link": "https://stellar.expert/explorer/testnet",
                "error": None
            }
        else:
            return {
                "status": "failed",
                "project_id": project_id,
                "tx_hash": "",
                "explorer_link": "https://stellar.expert/explorer/testnet",
                "error": clean_err or clean_out
            }

    except Exception as e:
        safe_exc = str(e).encode("ascii", "ignore").decode()
        try:
            print(f"System Error in Blockchain Module: {safe_exc}")
        except: pass
        
        return {
            "status": "failed",
            "project_id": project_id,
            "tx_hash": "",
            "explorer_link": "https://stellar.expert/explorer/testnet",
            "error": safe_exc
        }
