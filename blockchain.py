import subprocess

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
        # Non-blocking async spawn
        subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        return {
            "status": "pending",
            "project_id": project_id,
            "tx_hash": "processing_async",
            "explorer_link": "https://stellar.expert/explorer/testnet",
            "error": None
        }
    except Exception as e:
        # Step 1: Sanitize outputs and ensure emojis / special chars don't fail encoding
        error_output = str(e).encode("ascii", "ignore").decode()
        
        return {
            "status": "failed",
            "project_id": project_id,
            "tx_hash": "",
            "explorer_link": "https://stellar.expert/explorer/testnet",
            "error": error_output
        }
