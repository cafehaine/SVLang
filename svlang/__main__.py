from .compiler import compile

if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    from io import StringIO
    import sys

    parser = ArgumentParser(
        description="Compile SVLang programs into SVC16 binaries.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source", default="-", nargs="?", help="The source file ('-' for stdin)"
    )
    parser.add_argument("output", help="The output file ('-' for stdout)")
    args = parser.parse_args()

    # Read input data from stdin or a file.
    input_data: str
    if args.source == "-":
        buffer = StringIO()
        try:
            while True:
                buffer.write(input("> "))
        except EOFError:
            pass
        input_data = buffer.getvalue()
    else:
        with open(args.source, "r") as input_file:
            input_data = input_file.read()

    binary = compile(input_data)

    if args.output == "-":
        sys.stdout.buffer.write(binary)
    else:
        with open(args.output, "wb") as binary_output_file:
            binary_output_file.write(binary)
