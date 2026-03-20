import os; from os import path
import sys
import json
import datetime



def format_iso_time(iso_ts:str) -> str:
    iso_ts_obj = datetime.datetime.fromisoformat(iso_ts)
    return datetime.datetime.strftime(iso_ts_obj, "%Y-%m-%d %H:%M:%S")

def format_header(header: dict) -> str:
    return f"#{header['name']} - {header['category']} - \"{header['topic']}\""

def format_message(msg: dict) -> str:
    return f"{format_iso_time(msg['timestamp'])} - @{msg['author']['name']}:\n{msg['content']}"
    
def format_buffer(buffer: list[str]) -> str:
    out = ''
    for item in buffer:
        out += item + "\n"

def convert_file(file_path:str) -> list[str]:
    buffer = []
    
    with open(file_path, 'r') as f:
        header = f.readline()
        header = json.loads(header)

        buffer.append(format_header(header))

        for line in f:
            msg = json.loads(line)

            buffer.append(format_message(msg))
    
    return buffer

if __name__ == '__main__':    
    if len(sys.argv) < 2:
        print('ERROR: Not enough file arguments given!')
    
    WORKING_DIR = os.getcwd()
    SCRIPT_DIR = f"{path.dirname(path.abspath(__file__))}"
    OUTPUT_DIR = path.join(SCRIPT_PATH, 'output')


    for arg in sys.argv[1:]:
        file_path = path.join(WORKING_DIR, arg)
    
        print(f"Converting File: {file_path}")

        convert_file(file_path)