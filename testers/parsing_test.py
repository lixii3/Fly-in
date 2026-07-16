from fly_in.src.parser import Parser, MultipleParsingExceptions, ParsingException
import os

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
            Parser.parse_map(dir_path + '/' + filename)
        except (ParsingException, MultipleParsingExceptions, OSError) as e:
            err_list.append(filename)
            output += str(e) + '\n'
        else:
            output += "NO ERRORS ON THIS FILE\n"

    if verbose:
        print(output)
    print("=+" * 20 + "SUMMARY" + "+=" * 20)
    ok = "[OK]"
    notok = "[ERROR]"
    for filename in file_list:
        print(f"{ok if filename not in err_list else notok} {filename}")


if __name__ == "__main__":
    try:
        test_cases("fly_in/maps/test/files", verbose=True)
    except (OSError, MultipleParsingExceptions) as e:
        print(e)
