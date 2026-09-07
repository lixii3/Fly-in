from fly_in.src.parser import Parser,\
    MultipleParsingExceptions, ParsingException
import os
import sys


def test_cases(dir_path: str, verbose: bool = False):
    err_list: list[str] = []
    output: str = ""
    try:
        file_list = [f for f in os.listdir(dir_path) if f.endswith('.txt')]
    except OSError as e:
        raise e
    for filename in file_list:
        try:
            output += ('\n' + "=" * 40 + filename + "=" * 40 + '\n')
            Parser.parse_map(os.path.join(dir_path, filename))
        except (ParsingException, MultipleParsingExceptions, OSError) as e:
            err_list.append(filename)
            output += str(e) + '\n'
        else:
            output += "NO ERRORS ON THIS FILE\n"

    if verbose:
        print(output)
    else:
        print("Pass the argument 'verbose', 'true' or '1' to view error details "
              "for each tested file")
    print("=+" * 20 + "SUMMARY" + "+=" * 20)
    ok = "[OK]"
    notok = "[ERROR]"
    for filename in file_list:
        print(f"{ok if filename not in err_list else notok} {filename}")


if __name__ == "__main__":
    verbose = False
    if len(sys.argv) == 2:
        if sys.argv[1].lower() in ["verbose", "true", "1"]:
            verbose = True
    dir_path = "fly_in/maps/.test/files"
    try:
        test_cases(dir_path, verbose=verbose)
    except (OSError, MultipleParsingExceptions) as e:
        print(e)
