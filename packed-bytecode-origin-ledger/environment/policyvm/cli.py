import argparse
import json
from .compiler import write_artifact
from .runtime import run_artifact


def main():
    parser = argparse.ArgumentParser(prog="policyvm")
    commands = parser.add_subparsers(dest="command", required=True)
    compile_parser = commands.add_parser("compile")
    compile_parser.add_argument("program")
    compile_parser.add_argument("artifact")
    run_parser = commands.add_parser("run")
    run_parser.add_argument("artifact")
    args = parser.parse_args()
    if args.command == "compile":
        write_artifact(args.program, args.artifact)
    else:
        print(json.dumps(run_artifact(args.artifact), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
