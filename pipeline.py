import argparse
import logging
import os
import subprocess
import sys
import tempfile

COMPOSE_FILE = "dockercompose.yml"
COMPOSE_ENV_TARGET = "test"


class Pipeline:
    def __init__(self):
        self._charcode = "utf-8"
        args = self._make_parser().parse_args()
        self._config_logger(args)
        self._check_localenv_commands = self._get_check_localenv_commands()
        self._build_commands = self._get_build_commands(args)
        self._deploy_commands = self._get_deploy_commands(args)
        self._analyze_commands = self._get_analyze_commands(args)
        self._test_commands = self._get_test_commands(args)
        self._check_vulnerability_commands = self._get_check_vulnerability_commands(
            args
        )

    def run(self):
        self._cd_to_script_directory()
        for command in self._check_localenv_commands:
            self._check_command(command, "Local enviroment has problem.")

        os.environ["TARGET"] = COMPOSE_ENV_TARGET
        for command in self._build_commands:
            self._check_command(command, "Build command failed.")
        for command in self._deploy_commands:
            self._check_command(command, "Deploy command failed.")

        for command in self._analyze_commands:
            self._check_command(command, "Analyze command failed.")
        for command in self._test_commands:
            self._check_command(command, "Test command failed.")
        for command in self._check_vulnerability_commands:
            self._check_command(command, "Check vulnerability command failed.")

    def _make_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="tool for checking software quality: build -> deploy -> code-analysis -> unittest -> vulnerability check"
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="quiet output. showing only what fails",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="verbose output. showing commands output",
        )
        parser.add_argument(
            "--build_ignore_cache",
            action="store_true",
            help="build container without using cache",
        )
        parser.add_argument(
            "--codeanalysis_skip",
            action="store_true",
            help="skip running all code analysis tools",
        )
        parser.add_argument(
            "--codeanalysis_skip_lint",
            action="store_true",
            help="skip running lint-checker(flake8)",
        )
        parser.add_argument(
            "--codeanalysis_skip_typecheck",
            action="store_true",
            help="skip running type-checker(mypy)",
        )
        parser.add_argument(
            "--test_skip", action="store_true", help="skip all unittests"
        )
        parser.add_argument(
            "--test_options",
            type=str,
            default="",
            help="specify which containers run what unittests. syntax '<container1>:<option1>,<container2>:<option2>,...'",
        )
        parser.add_argument(
            "--vulnerabilitycheck_skip",
            action="store_true",
            help="skip vulnerability check",
        )
        parser.add_argument(
            "--vulnerabilitycheck_level",
            type=str,
            default="",
            help="specify checking severity level. supports high|midle|low. default is high",
        )
        parser.add_argument(
            "--vulnerabilitycheck_ignore_unfixed",
            action="store_true",
            help="ignore unfixed vulnerability",
        )
        return parser

    def _config_logger(self, args):
        if args.quiet + args.verbose > 1:
            print("option --quiet and --verbose can't be used at same time.")
            sys.exit(1)

        elif args.quiet:
            level = logging.CRITICAL
        elif args.verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(level=level, format="%(message)s")

    def _get_check_localenv_commands(self):
        return [
            "command -v docker",
            "command -v docker-compose",
        ]

    def _get_build_commands(self, args):
        if args.build_ignore_cache:
            command = f"docker-compose -f {COMPOSE_FILE} build --no-cache --pull"
        else:
            command = f"docker-compose -f {COMPOSE_FILE} build"
        return [command]

    def _get_deploy_commands(self, args):
        return [f"docker-compose -f {COMPOSE_FILE} up -d"]

    def _get_analyze_commands(self, args):
        lint_command = "docker container exec myapp.app flake8 -v"
        type_check_command = "docker container exec myapp.app mypy myapp"

        if (
            args.codeanalysis_skip
            + args.codeanalysis_skip_lint
            + args.codeanalysis_skip_typecheck
            > 1
        ):
            logging.critical(
                "option --codeanalysis_skip and --codeanalysis_skip_lint and --codeanalysis_skip_typecheck can't be used at same time."
            )
            sys.exit(1)

        if args.codeanalysis_skip:
            return []
        if args.codeanalysis_skip_lint:
            return [type_check_command]
        if args.codeanalysis_skip_typecheck:
            return [lint_command]
        return [lint_command, type_check_command]

    def _get_test_commands(self, args):
        if args.test_skip + bool(args.test_options) > 1:
            logging.critical(
                "option --test_skip and --test_options can't be used at same time."
            )
            sys.exit(1)

        if args.test_skip:
            return []
        if not args.test_options:
            return ["docker container exec myapp.app pytest"]

        try:
            commands = []
            for container_option in args.test_options.split(","):
                words = container_option.split(":")
                container = words[0].strip()
                option = words[1].strip()
                commands.append(f"docker container exec {container} pytest {option}")
            return commands
        except Exception:
            logging.critical(
                "--test_options has wrong format. sample '<container1>:<option1>,<container2>:<option2>'"
            )
            sys.exit(1)

    def _get_check_vulnerability_commands(self, args):
        if args.vulnerabilitycheck_skip + bool(args.vulnerabilitycheck_level) > 1:
            logging.critical(
                "option --vulnerabilitycheck_skip and --vulnerabilitycheck_level can't be used at same time."
            )
            sys.exit(1)

        if args.vulnerabilitycheck_skip + args.vulnerabilitycheck_ignore_unfixed > 1:
            logging.critical(
                "option --vulnerabilitycheck_skip and --vulnerabilitycheck_ignore_unfixed can't be used at same time."
            )
            sys.exit(1)

        if args.vulnerabilitycheck_skip:
            return []

        level = args.vulnerabilitycheck_level.lower().strip()
        if level == "":
            level = "high"
        if level not in {"critical", "high", "medium", "low"}:
            logging.critical(
                "option --vulnerabilitycheck_level supports high|medium|low"
            )
            sys.exit(1)

        commands = []
        fname = tempfile.NamedTemporaryFile().name
        make_tar_command = f"docker save -o {fname}.tar myapp.app:local"
        commands.append(make_tar_command)

        vmap = {
            "critical": ("low,medium,high", "critical"),
            "high": ("low,medium", "high,critical"),
            "medium": ("low", "medium,high,critical"),
            "low": ("", "low,medium,high,critical"),
        }
        no_exit_sev = vmap[level][0]
        exit_sev = vmap[level][1]
        ignore_unfixed_option = (
            "--ignore-unfixed" if args.vulnerabilitycheck_ignore_unfixed else ""
        )

        if no_exit_sev != "":
            noexit_command = f"docker run --mount type=bind,source='{fname}.tar',target=/image.tar,readonly aquasec/trivy image --severity {no_exit_sev} {ignore_unfixed_option} -f table --input /image.tar"
            commands.append(noexit_command)
        exit_command = f"docker run --mount type=bind,source='{fname}.tar',target=/image.tar,readonly aquasec/trivy image --severity {exit_sev} {ignore_unfixed_option} --exit-code 1 -f table --input /image.tar"
        commands.append(exit_command)

        return commands

    def _cd_to_script_directory(self):
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def _run_command(self, command):
        logging.info("$ " + command)

        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        buffer = []
        while True:
            line = proc.stdout.readline()
            if line:
                line = line.decode(self._charcode)
                line = line.rstrip()
                buffer.append(line)
                logging.debug(line)
            if not line and proc.poll() is not None:
                break
        logging.debug("")

        output = "\n".join(buffer)
        return (proc.returncode, output)

    def _check_command(self, command, error_message):
        (returncode, output) = self._run_command(command)
        if returncode == 0:
            return

        logging.critical(f"failed at command '$ {command}'")
        logging.critical(f"===output===\n{output}\n======")
        logging.critical(error_message)
        logging.critical("abort")
        sys.exit(1)


if __name__ == "__main__":
    Pipeline().run()
