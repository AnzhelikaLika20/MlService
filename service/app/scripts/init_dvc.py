import subprocess
import os


def run(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def init_dvc(base="/app"):
    data_path = os.path.join(base, "data")
    os.makedirs(data_path, exist_ok=True)

    run(f"cd {base} && dvc init --no-scm || true")

    run(f"cd {base} && dvc remote add -d s3remote s3://ml-models/dvc || true")
    run(f"cd {base} && dvc remote modify s3remote endpointurl http://minio:9000")
    run(f"cd {base} && dvc remote modify s3remote access_key_id minioaccess")
    run(f"cd {base} && dvc remote modify s3remote secret_access_key miniosecret")
    run(f"cd {base} && dvc remote modify s3remote region us-east-1")

if __name__ == "__main__":
    init_dvc()
