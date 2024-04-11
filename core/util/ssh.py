import os
import subprocess
import tempfile


def get_pubkey_fingerprint(pubkey: str) -> str | None:
    """
    Turns this "ssh-rsa AAAAB3N... user@computer"
    Into "SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0M"
    :param pubkey: Public SSH key
    :return: Fingerprint of given public key
    """
    (_fd, path) = tempfile.mkstemp()
    with open(path, mode="w") as f:
        f.write(pubkey)
        f.flush()
    # 3072 SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0M robko@robko-ntb (RSA)
    # ssh-keygen -lf test_key.pub
    process = subprocess.Popen(
        ['ssh-keygen', '-lf', path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    try:
        # Check if there's an error
        if stderr:
            print("Error:", stderr.decode())
            return None
        # Parse the output to extract the SHA256 fingerprint
        output_lines = stdout.decode().splitlines()
        for line in output_lines:
            if "SHA256:" in line:
                fingerprint = line.split()[1]
                return fingerprint
    finally:
        os.remove(path)
