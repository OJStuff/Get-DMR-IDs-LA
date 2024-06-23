"""
Environment: Thonny IDE v4.1.4 and builtin Python v3.10.11.
Copyright: Released under CC BY-SA 4.0
Author: GitHub/OJStuff, June 23, 2024, v1.0
"""

import sys
import os
import argparse
import requests
import json
import csv
from unidecode import unidecode

from region_codes import DMR_RC
from country_codes import DMR_CC

DMR_URL: str = "https://radioid.net/static/users.json"
HAM_FILE: str = (
    "Liste over norske radioamatører (CSV).csv"  # Update getdmrids.py -> LA version
)


def strLeftJust(string: str, width: int, fill: str = " ") -> str:
    """
    Create a left justified string and fill unused space
    Args:
        string: A string
        width: Width of left justified string
        fill: Fill string
    Returns:
        A left justified string
    """
    if len(string) > width:
        string = string[:width]
    fill = fill * width
    return (string + fill)[:width]


def fileExist(file: str) -> bool:
    """
    Check the existence of file
    Args:
        file: Local filname
    Returns:
        True if file exists
    """
    status = os.path.exists(file)
    return status


def jsonLoad(file: str) -> dict:
    """
    Loads a json file
    Args:
        file: Json filename
    Returns:
        data: Json dictionary
    """
    with open(file, "rt", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)
    return data


def jsonDump(file: str, data: dict) -> None:
    """
    Dumps a local json file
    Args:
        file: Local json filename
        data: Data as a dictionary
    Returns:
        None
    """
    with open(file, "wt", encoding="utf-8") as jsonFile:
        json.dump(data, jsonFile)
    return None


def urlExist(url: str) -> bool:
    """
    Checks the existence of url
    Args:
        url: Url to check
    Returns:
        True if url exists
    """
    try:
        permanentRedirect: int = 308
        r = requests.head(url, timeout=5)
        status = r.status_code in (requests.codes.ok, permanentRedirect)
    except:
        status = False
    return status


def urlLoad(file: str, url: str, info: bool) -> bool:
    """
    Download file from url in chunks of 1024 bytes
    Args:
        file: Local filname
        url: Url to download
        info: True if info about downloaded size be shown
    Returns:
        None
    """
    try:
        status: bool = True
        r = requests.get(url, timeout=5)
        with open(file, "wb") as f:
            count: int = 0
            chunk_size: int = 1024
            for block in r.iter_content(chunk_size=chunk_size):
                f.write(block)
                count += 1
            f.close()
        if info:
            print(f" > {count/chunk_size:.2f} MB downloaded")
    except:
        status = False
    return status


def removeConjugate(inputList: list) -> list:
    """
    Removes conjugates (x and -x pairs) in a list
    Args:
        inputList: List to process
    Returns:
        A list with conjugates (x and -x pairs) removed
    """
    negList: list = []
    for nr in inputList:
        if nr < 0:
            negList.append(nr)
    for nr in negList:
        if (-nr) in inputList:
            inputList.remove(nr)
            inputList.remove(-nr)
    return inputList


def getLAHamsURL():  # Update getdmrids.py -> LA version
    """
    Find norwegian HAM db url from web page
    Args:
        none
    Returns:
        url
    """
    domain = "https://www.nkom.no"
    page = "/frekvenser-og-elektronisk-utstyr/radioamator/"
    file = "Liste%20over%20norske%20radioamat%C3%B8rer%20(CSV).csv"
    status = True
    fileLength = len(file)
    try:
        response = requests.get(domain + page)
        content = response.text
        end = content.find(file) + fileLength
        content = content[end - 500 : end]
        begin = content.find(page)
        end = content.find(file) + fileLength
        url = domain + content[begin:end]
    except:
        status = False
        url = ""
    return status, url


def argsHandle() -> tuple[bool, bool, str, list, list]:
    """
    Collects and checks arguments before processing
    Args:
        None
    Returns:
        status: Returns True if args are OK
        fFormat: Returns a string with selected file format
        cList: Returns a list of selected country codes
        rList: Returns a list of selected region codes
    """
    status: bool = True
    fFormat: str = ""
    cList: list = []
    rList: list = []

    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="""Program exports a formatted file with DMR IDs
        based on users criteria. This file can  be imported into a radio,
        like AnyTone D878/D578, as digital contact list""",
        epilog="""Updated version and resources may be found at
        https://GitHub.com/OJStuff""",
    )

    parser.add_argument(
        "-s",
        "--statistics",
        help="show statistics for formatted file with dmr-id's",
        action="store_true",
    )

    parser.add_argument(
        "-d",
        "--download",
        help="download DMR database from https://radioid.net",
        action="store_true",
    )

    parser.add_argument(  # Update getdmrids.py -> LA version
        "-dla",
        "--downloadLA",
        help="download LA database from https://nkom.no",
        action="store_true",
    )

    parser.add_argument(
        "-f",
        "--format",
        help="file format for the formatted file",
        default=["anytone"],
        choices=["anytone", "text"],
        nargs=1,
    )

    parser.add_argument(
        "-r",
        "--region",
        help="region codes added for the formatted file",
        type=int,
        nargs="*",
    )

    parser.add_argument(
        "-c",
        "--country",
        help="country codes added/subtracted for the formatted file",
        type=int,
        nargs="*",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print(f"Please try {sys.argv[0]} -h if you need help")

    statActive = args.statistics
    downActive = args.download
    dlaActive = args.downloadLA  # Update getdmrids.py -> LA version

    if downActive:
        if urlExist(DMR_URL):
            print(f'Downloading DMR database "{os.path.basename(DMR_URL)}"', end="")
            if not urlLoad(os.path.basename(DMR_URL), DMR_URL, True):
                print(f"\nProblem downloading {DMR_URL} -> network problems !")
                sys.exit(1)
        else:
            print(f"{DMR_URL} unreachable -> network problems !")
            sys.exit(1)

    dlaStatus, urlLA = getLAHamsURL()  # Update getdmrids.py -> LA version
    if dlaActive and dlaStatus:  # Update getdmrids.py -> LA version
        if urlExist(urlLA):
            print(f'Downloading LA database "{HAM_FILE}"', end="")
            if not urlLoad(HAM_FILE, urlLA, True):
                print(f"\nProblem downloading {HAM_FILE} -> network problems !")
                sys.exit(1)
        else:
            print(f"{DMR_URL} unreachable -> network problems !")
            sys.exit(1)

    fFormat = args.format

    regionActive = not ((args.region == []) or (args.region == None))
    if regionActive:
        rList = list(set(args.region))

    countryActive = not ((args.country == []) or (args.country == None))
    if countryActive:
        cList = removeConjugate(list(set(args.country)))

    if (not regionActive) and (not countryActive):
        print("No options specified to do anything...")
        status = False

    if regionActive or countryActive:
        print("Options specified for export of formatted file:")

    if regionActive:
        for n in rList:
            if n in DMR_RC.keys():
                print("-r", n, "include region:", DMR_RC[n])
            else:
                print("-r", n, "ignore region: (non existant)")

    if countryActive:
        countryRemove: list = []
        for n in cList:
            if abs(n) in DMR_CC.keys():
                if n < 0:
                    firstDigitCountry = int(str(n)[1])
                    if firstDigitCountry not in rList:
                        print("-c", n, "exclude country:", DMR_CC[-n], "(redundant)")
                        countryRemove.append(n)
                    else:
                        print("-c", n, "exclude country:", DMR_CC[-n])
                else:
                    firstDigitCountry = int(str(n)[0])
                    if firstDigitCountry in rList:
                        print("-c", n, "include country:", DMR_CC[n], "(redundant)")
                        countryRemove.append(n)
                    else:
                        print("-c", n, "include country:", DMR_CC[n])
            else:
                print("-c", n, "ignores country: (non existant)")
        for r in countryRemove:
            cList.remove(r)

    if not fileExist(os.path.basename(DMR_URL)):
        print(f'\nCan\'t find local DMR database "{os.path.basename(DMR_URL)}"')
        print(f'Use -d option to download "{os.path.basename(DMR_URL)}"')
        status = False

    if not fileExist(HAM_FILE):  # Update getdmrids.py -> LA version
        print(f'\nCan\'t find local LA database "{HAM_FILE}"')
        print(f'Use -dla option to download "{HAM_FILE}"')
        status = False

    return statActive, status, fFormat, cList, rList


def regionInclude(id: int, rList: list) -> bool:
    """
    Check if id is a wanted dmr user according to region list
    Args:
        id: DMR ID to check
        rList: List of region codes
    Returns:
        status: True if region match for id
    """
    status = int(str(id)[0]) in rList
    return status


def countryInclude(id: int, cList: list) -> bool:
    """
    Check if id is a wanted dmr user according to country list
    Args:
        id: DMR ID to check
        cList: List of country codes
    Returns:
        status: True if country match for id
    """
    status = int(str(id)[:3]) in cList
    return status


def countryExclude(id: int, cList: list) -> bool:
    """
    Check if id is an unwanted dmr user according to list of excluded countries
    Args:
        id: DMR ID to check
        cList: List of country codes
    Returns:
        status: True if country exclude match for id
    """
    status = -int(str(id)[:3]) in cList
    return status


def dmrSelection(cList: list, rList: list) -> list[dict]:
    """
    Returns a list of dmr data from selection criteria
    Args:
        None
    Returns:
        selection: A list of dictionaries with dmr data
    """
    selection: list = []
    dmrDB = jsonLoad(os.path.basename(DMR_URL))
    print(f'Getting DMR IDs from "{os.path.basename(DMR_URL)}"')
    for i in dmrDB["users"]:
        if regionInclude(i["radio_id"], rList) and not countryExclude(
            i["radio_id"], cList
        ):
            selection.append(i)
        if not regionInclude(i["radio_id"], rList) and countryInclude(
            i["radio_id"], cList
        ):
            selection.append(i)
    return selection


def dmrTouchup(data: list) -> list[dict]:
    """
    Returns a list of dmr data from selection criteria that is converted from
    utf-8 to ascii, since radioes do not like to display utf-8 on screen.
    So: æ -> ae, ø -> o, å -> a, ü -> u and so on.
    Args:
        data: A list of data to touch up
    Returns:
        dataToucup: A list of dictionaries with dmr data
    """
    dataToucup: list = []
    for x in data:
        x["fname"] = x["fname"].title()
        x["name"] = x["name"].title()
        x["country"] = x["country"].title()
        x["callsign"] = x["callsign"].upper()
        x["city"] = x["city"].title()
        x["surname"] = x["surname"].title()
        x["state"] = x["state"].title()
        dataToucup.append(x)
    return dataToucup


def dmrStat(data: list):
    stat: list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for x in data:
        rcode = int(str(x["radio_id"])[:1])
        stat[rcode] += 1
    print("\nStatistics for exported formatted file:")
    for r in range(len(stat)):
        print(f"{stat[r]:9,} IDs from region {r}: {DMR_RC[r]}")
    return None


def csvLoad(file: str, mode: str, newl: str, enc: str, delim: str) -> list:
    """
    Import csv file rows
    Args:
        file: CSV filename
        mode: CSV file mode
        newl: CSV newline char
        enc: CSV file encoding
        delim: CSV delimiter
    Returns:
        List of rows
    """
    fileRows = []
    with open(file, mode, newline=newl, encoding=enc) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delim)
        next(csvreader)  # Skip the header
        for row in csvreader:
            fileRows.append(row)  # Get all the rows
        csvfile.close()
    return fileRows


def dmrUpdateLA(data: list) -> list[dict]:  # Update getdmrids.py -> LA version
    """
    Updates dmr data with data for norwegian ham operator list from NKOM (fileLA)
    Args:
        data: A list of data to touch up
    Returns:
        data: An updated list of dictionaries with dmr data
    """
    fileLA: str = HAM_FILE
    dataLA: list = []

    if fileExist(fileLA):
        dataLA = csvLoad(fileLA, "rt", "", "ansi", ";")
        print(f'Updating IDs from "{fileLA}"')
        for x in data:
            ccode = int(str(x["radio_id"])[:3])
            if ccode == 242:
                for ham in dataLA:
                    if x["callsign"] == ham[0]:
                        if ham[9] != "Personlig":
                            x["fname"] = "( " + ham[9] + " )"
                            x["name"] = "( " + ham[9] + " )"
                            x["country"] = ham[8]
                            x["city"] = ham[7]
                            x["surname"] = ham[3]
                            x["state"] = ""

                        if ham[9] == "Personlig" and ham[2] == "":
                            # Keep radioid.net data, no updated data in dataLA
                            None

                        if ham[9] == "Personlig" and ham[2] != "":
                            # Update radioid.net data with updated data from dataLA
                            x["fname"] = ham[2]
                            x["name"] = ham[2]
                            x["country"] = ham[8]
                            x["city"] = ham[7]
                            x["surname"] = ham[3]
                            x["state"] = ""

                        if ham[9] == "" and ham[2] == "":
                            x["fname"] = ""
                            x["name"] = ""
    return data


def dmrExportAnytone(data: list, file: str) -> None:
    """
    Creates csv file formatted for AnyTone D878/D578 for export
    Args:
        Data: List of selected DMR IDs
        File: Filename for exported file
    Returns:
        None
    """
    # dataWidth AnyTone D878/D578: list = [8, 8, 16, 16, 16, 16, 16, 12, 4]
    csvHead: list = [
        "Radio ID",
        "Callsign",
        "Name",
        "City",
        "State",
        "Country",
        "Remarks",
        "Call Type",
        "Call Alert",
    ]
    csvRows: list = []
    csvRows.append(csvHead)

    for x in data:
        csvRow: list = [
            unidecode(str(x["radio_id"])),
            unidecode(x["callsign"]),
            unidecode(x["fname"]),
            unidecode(x["city"]),
            unidecode(x["state"]),
            unidecode(x["country"]),
            unidecode(""),
            unidecode("Private Call"),
            unidecode("None"),
        ]
        csvRows.append(csvRow)

    with open(file, "wt", newline="", encoding="utf-8") as csvfile:
        cswriter = csv.writer(csvfile)
        cswriter.writerows(csvRows)
        print(f'DMR ID file "{file}" was exported with {len(data):,} IDs')
    return None


def dmrExportText(data: list, file: str) -> None:
    """
    Creates txt file formatted as text for export
    Args:
        Data: List of selected DMR IDs
        File: Filename for exported file
    Returns:
        None
    """
    dataWidth: list = [30, 30, 30, 10, 30, 30, 10, 10, 30]
    txtRow: str = ""
    txtRows: list = []

    txtHead = [
        "fname",
        "name",
        "country",
        "callsign",
        "city",
        "surname",
        "radio_id",
        "id",
        "state",
    ]

    for x in range(len(txtHead)):
        txtRow += strLeftJust(txtHead[x], dataWidth[x])
    txtRows.append(txtRow + "\n\n")

    for x in data:
        txtRow = (
            strLeftJust(x["fname"], dataWidth[0])
            + strLeftJust(x["name"], dataWidth[1])
            + strLeftJust(x["country"], dataWidth[2])
            + strLeftJust(x["callsign"], dataWidth[3])
            + strLeftJust(x["city"], dataWidth[4])
            + strLeftJust(x["surname"], dataWidth[5])
            + strLeftJust(str(x["radio_id"]), dataWidth[6])
            + strLeftJust(str(x["id"]), dataWidth[7])
            + strLeftJust(x["state"], dataWidth[8])
        )
        txtRows.append(txtRow + "\n")

    with open(file, "wt", encoding="utf-8") as txtFile:
        txtFile.writelines(txtRows)
        txtFile.close()

    print(f'DMR ID file "{file}" was exported with {len(data):,} IDs')
    return None


def main() -> None:
    dmrData: list = []
    argsOK: bool = False
    countryList: list = []
    regionList: list = []

    statOn, argsOK, fileFormat, countryList, regionList = argsHandle()

    if argsOK and fileExist(os.path.basename(DMR_URL)):
        dmrData = dmrSelection(countryList, regionList)

        dmrData = dmrUpdateLA(dmrData)  # Update getdmrids.py -> LA version

        dmrData = dmrTouchup(dmrData)

        if fileFormat[0] == "anytone":
            dmrExportAnytone(
                dmrData, os.path.basename(DMR_URL).replace(".json", "-anytone.csv")
            )

        if fileFormat[0] == "text":
            dmrExportText(
                dmrData, os.path.basename(DMR_URL).replace(".json", "-text.txt")
            )

        if statOn:
            dmrStat(dmrData)


if __name__ == "__main__":
    main()
