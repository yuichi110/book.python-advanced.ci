import requests
import subprocess
import sys
import time


class DockerCD:
    def __init__(self, yaml_url):
        self._charcode = "utf8"
        self._yaml_url = yaml_url
        self._last_yaml = ""

    def run(self, interval=60):
        self._run_command("command -v docker")
        self._run_command("command -v docker-compose")
        self._run_command("docker info")

        while True:
            try:
                yaml = self._get_dockercompose_yaml()
                if self._last_yaml == yaml:
                    print("no change.")
                else:
                    self._last_yaml = yaml
                    self._apply_yaml(yaml)
            except Exception as e:
                print(e)
            time.sleep(interval)

    def _get_dockercompose_yaml(self):
        res = requests.get(self._yaml_url)
        yaml = res.text.strip()
        return yaml

    def _apply_yaml(self, yaml):
        command = f"docker compose -f - up -d << EOF\n{yaml}\nEOF"
        self._run_command(command)

    def _run_command(self, command):
        print("$ " + command)
        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        print()
        while True:
            line = proc.stdout.readline()
            if line:
                line = line.decode(self._charcode)
                line = line.rstrip()
                print(line)
            if not line and proc.poll() is not None:
                break
        print()

        if proc.returncode != 0:
            raise Exception("Error: command failed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("syntax: python deploy.py <yaml_url>")
        sys.exit(1)
    yaml_url = sys.argv[1]
    dcd = DockerCD(yaml_url)
    dcd.run()
