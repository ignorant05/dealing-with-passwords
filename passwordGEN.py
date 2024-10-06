#created by ignorant05 aka ignorant05

#for more information about this tool, type : sudo python3 passwordGEN.py -h (or --help)

#! /usr/bin/env python3

import secrets 
import string 
import json 
import argparse
import sys
import os 

import platform 
import ctypes 

from datetime import datetime


def check():

    if platform.system() == 'Linux':
        
        if os.geteuid() != 0 : 

            print("[-] This tool must be run as root.")

            sys.exit(1)
    
    elif platform.system() == 'Windows':

        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True
            else:
                print("[-] This tool must be run as an administrator.")
                sys.exit(1)
        except Exception as e:
            print(f"[-] An error occurred: {e}")
            sys.exit(1)
    else :
        print("\n[¿] No supported OS\n")

def change_permission_and_ownership(path):

    root_uid=0
    root_gid=0
    
    try : 
        os.chown(path,root_uid,root_gid)
        os.chmod(path,0o600)
    except PermissionError :
        print("[-]You need to run the script with root permissions change the file's ownership and the persission.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[-] File {path} not found.")
        sys.exit(1)
    except Exception as e : 
        print(f"[-]Something went wrong {e}")
        sys.exit(1)
def load_file(path):


    if not os.path.exists(path):

        with open(path, 'w') as file:
            json.dump({"Generated passwords": []}, file, indent=4)

        return {"Generated passwords": []}

    try:
        with open(path, 'r') as file:
            content = file.read().strip()
            if not content:
                   
                return {"Generated passwords": []}

            return json.loads(content) 
    
    except json.JSONDecodeError :

        print(r"[-] Invalid json file ")
        sys.exit(1)

    except Exception as e : 

        print(r"[-] Something went wrong")
        print(e)
        sys.exit(1)

def save_output_in_file(path,password):

    try : 
        data = load_file(path)
        new_pass = {password : datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        data["Generated passwords"].append(new_pass)
        
        with open(path , 'w')as file : 
            json.dump(data,file,indent=4)
        print(f"[+]Password saved successfully to {path}")

    except OSError as e:
        print(f"[-] File write error: {e}")

    except Exception as e :
        print(f"\n[-] Something went wrong\n{e}")


def generate_password(uppercase=False, lowercase=False, nums=False, punctuations=False, length=12, invalid_chars = None):

    valid_chars =""
    password =""

    if uppercase :
        valid_chars+=string.ascii_uppercase

    if lowercase :
        valid_chars+=string.ascii_lowercase

    if nums:
        valid_chars+=''.join(str(x) for x in range(0,10))

    if punctuations:
        valid_chars+=string.punctuation

    if invalid_chars is not None :
        valid_chars =''.join(char for char in valid_chars if char not in invalid_chars)
    
    if not valid_chars:
        print("Error: No valid characters left for password generation!")
        sys.exit(1)

    for i in range (length):
        
        password+=secrets.choice(valid_chars)
    
    return password 



if __name__=="__main__" :

    check()
    tool_description = """This tool generates strong passwords based on user-selected options.
                          You can select character sets (uppercase, lowercase, numbers, punctuation) 
                          and specify a custom length and if you don't want some chars to be selected just use a flag and provide them."""
    
    parser = argparse.ArgumentParser(

        description=tool_description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-u", "--uppercase", 
        action="store_true", 
        help="Include uppercase letters in the password."
    )
    parser.add_argument(
        "-l", "--lowercase", 
        action="store_true", 
        help="Include lowercase letters in the password."
    )

    parser.add_argument(
        "-n", "--nums", 
        action="store_true", 
        help="Include numbers in the password."
    )

    parser.add_argument(
        "-p", "--punctuations", 
        action="store_true", 
        help="Include punctuation characters in the password."
    )
    parser.add_argument(
        "--length",
        type=int,
        default=12, 
        help="Specify the length of the password (default: 12)."
    )
    parser.add_argument(
        "-i", "--invalid-chars",
        type=str,
        default=None,
        help="Excludes the invalid characters depending on user input (default: None)"
    )
    parser.add_argument(
        "-o","--output",
        type=str,
        help="Path to the JSON file where you want to save the password."
    )

    args = parser.parse_args()

    password = generate_password(
        uppercase=args.uppercase,
        lowercase=args.lowercase,
        nums=args.nums,
        punctuations=args.punctuations,
        length=args.length,
        invalid_chars=args.invalid_chars
    )

    if args.output :
        change_permission_and_ownership(args.output)
        save_output_in_file(args.output,password)

    print(f"Generated password: {password}")



