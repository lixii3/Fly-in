from fly_in.src.parser import Parser, ParsingException, MultipleParsingExceptions
from fly_in.src.scheduler import Scheduler, SchedulerException
import os
import sys


outputfile = "test_output.txt"
dir_path = "fly_in/maps/hard"


def test(verbose):
    err_list: list[str] = []
    output: str = ""
    try:
        file_list = [f for f in os.listdir(dir_path) if f.endswith(".txt")]
        # svuota file
        with open(outputfile, "w") as _:
            pass
    except OSError as e:
        raise e
    for filename in file_list:
        try:
            output += "\n" + "=" * 10 + filename + "=" * 10 + "\n"
            g = Parser.parse_map(os.path.join(dir_path, filename))
            s = Scheduler(g)
            s.schedule()

            with open("output.txt", "r") as sorgente:
                testo = sorgente.read()

            with open(outputfile, "a") as destinazione:
                destinazione.write("\n" + "=" * 35 + f"{filename}" + "=" * 35)
                destinazione.write(f"\n{testo}")
        except (
            ParsingException,
            MultipleParsingExceptions,
            OSError,
            SchedulerException,
        ) as e:
            err_list.append(filename)
            output += str(e) + "\n"
        else:
            output += "NO ERRORS ON THIS FILE\n"

    if verbose:
        print(output)
    else:
        print(
            "Pass the argument 'verbose', 'true' or '1' to view error details for each tested file"
        )
    print("=+" * 20 + "SUMMARY" + "+=" * 20)
    ok = "[OK]"
    notok = "[ERROR]"
    for filename in file_list:
        print(f"{ok if filename not in err_list else notok} {filename}")


if __name__ == "__main__":
    verbose = False
    if len(sys.argv) >= 2:
        if sys.argv[1].lower() in ["true", "1"]:
            verbose = True
    test(verbose)
