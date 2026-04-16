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
    return '\n'.join(buffer)

def convert_file(file_path:str) -> list[str]:
    buffer = []
    try:
        with open(file_path, 'r') as f:
            header = f.readline()
            header = json.loads(header)

            buffer.append(format_header(header))

            for line in f:
                msg = json.loads(line)

                buffer.append(format_message(msg))
        
        return buffer
    except Exception as e:
        print(f"ERROR: {e}")
        return []

if __name__ == '__main__':    
    if len(sys.argv) < 2:
        print('ERROR: Not enough file arguments given!')
    
    WORKING_DIR = os.getcwd()
    SCRIPT_DIR = path.dirname(path.abspath(__file__))
    OUTPUT_DIR = path.join(SCRIPT_DIR, 'output')


    for arg in sys.argv[1:]:
        file_path = path.join(WORKING_DIR, arg)
        print(f"Converting File: {file_path}")
        for msg in convert_file(file_path):
            print(msg)