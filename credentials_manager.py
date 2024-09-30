#Created by ignorant05 aka oussama baccara 
#Credentials_Manager v1.0
#Use the -h or --help flag for usage

#! /usr/bin/env python3

import sys 
import os 
import json 
import shutil

import ctypes
import platform

import argparse


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


def change_file_ownership(path):

    root_uid = 0
    root_gid = 0

    try :
        
        os.chown(path, root_uid, root_gid)
        print(f"[+] Changed ownership of {path} to root (UID: {root_uid}, GID: {root_gid}).")

    except PermissionError:
        print(f"[-] Permission denied. You need to run this script as root to change file ownership.")
        sys.exit(1)

    except FileNotFoundError:

        print(f"[-] File {path} not found.")
        sys.exit(1)
    except Exception as e:

        print(f"[-] An error occurred: {e}")
        sys.exit(1)



def load_file(path):

    if not os.path.exists(path):

        with open(path, 'r+') as file:
            json.dump({"platforms": {}}, file, indent=4)
        return {"platforms": {}}

    try:
        with open(path, 'r') as file:
            content = file.read().strip()
            if not content:
                   
                return {"platforms": {}}

            return json.loads(content) 
    
    except json.JSONDecodeError :

        print(r"[-] Invalid json file ")
        sys.exit(1)

    except Exception as e : 

        print(r"[-] Something went wrong")
        print(e)
        sys.exit(1)

def save_file (path,data):

    try : 

        with open(path , 'w')as file : 
            json.dump(data,file,indent=4)

    except OSError as e:
        print(f"[-] File write error: {e}")

    except Exception as e :
        print(f"\n[-] Something went wrong\n{e}")


def show_credentials(path) :

    file = load_file(path)
    
    terminal_width = shutil.get_terminal_size().columns

    for platform in file['platforms']: 

        p = platform.center(terminal_width)

        print(f"{p}")

        for user in file['platforms'][platform]['users']:
            
            for key, value in user.items():

                print(f"[×]  {key}: {value}")
            print("\n")

def new_credentials(path, platform, username, email, password): 

    file = load_file(path) 

    new_credentials = {
            "username" : username ,
            "email" : email ,
            "password" : password
            }  
    
    platform = platform.lower()

    if 'platforms' not in file:

        file['platforms'] = {}

    if not(platform in file['platforms']):
        
        file['platforms'][platform] = {'users' : []}
        
    file['platforms'][platform]['users'].append(new_credentials)
    save_file(path,file)
    print(f"\n[+] New credentials added for {platform.capitalize()}.")
    

    

def update_password(path, platform, username, old ,new):

    file = load_file(path)
 
    platform = platform.lower()
    
    if platform in file['platforms']:

        for user in file['platforms'][platform]['users']:

            if user['username'].lower() == username.lower() and user['password'] == old :
                
                user['password'] = new
                
                save_file(path, file)

                print(f"\n[+] Password updated for {username} on {platform.capitalize()}.")

                return
            
        print(f"[-] User {username} not found on {platform.capitalize()}.")
    else:
        print(f"[-] platform {platform.capitalize()} not found.")


    
def update_username(path, platform, old, new):

    file = load_file(path)
 
    platform = platform.lower()
    
    if platform in file['platforms']:

        for user in file['platforms'][platform]['users']:

            if user['username'].lower() == old.lower():
                
                user['username'] = new
                
                
                save_file(path, file)

                print(f"\n[+] Username updated on {platform.capitalize()}.")

                return
            
        print(f"[-] Username {old} not found on {platform.capitalize()}.")
    else:
        print(f"[-] platform {platform.capitalize()} not found.")



def update_email(path, platform, old, new):

    file = load_file(path)
 
    platform = platform.lower()
    
    if platform in file['platforms']:

        for user in file['platforms'][platform]['users']:

            if user['email'].lower() == old.lower():
                
                user['email'] = new
                
                
                save_file(path, file)

                print(f"\n[+] Email updated on {platform.capitalize()}.")

                return
            
        print(f"[-] Email {old} not found on {platform.capitalize()}.")
    else:
        print(f"[-] platform {platform.capitalize()} not found.")


def remove_account (path, platform, username):

    file = load_file(path)

    platform = platform.lower()

    if platform in file['platforms']:

        

        users = file['platforms'][platform]['users']

        updated_users = [user for user in users if not (
               user['username'].lower() == username.lower()
                    )]
        if len(updated_users) == len(users):

            print(f"[-] User {username} not found on {platform.capitalize()}.")

        else:
            if len(updated_users) == 0 :
                del file['platforms'][platform]
            else :
                file['platforms'][platform]['users'] = updated_users
            save_file(path, file)
            print(f"[+] Account successfully removed from {platform.capitalize()}.")
            
                
    else:

        print(f"[-] platform {platform.capitalize()} not found.")
    



if __name__ == "__main__":

    
    check()
    tool_desc = """\
            A simple tool that manages your social media accounts in a secured way.\n
            Usage: sudo python3 password_manager.py <path_to_password_file> <argument>.\n
            Ex : sudo python3 password_manager.py credentials.json -a facebook john john_is_cool@gmail.com i_am_invincible\n
            >>> This command adds a new username, email, and password to the Facebook platform area.
            """

    parser = argparse.ArgumentParser(

        description=tool_desc,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-u", "--username",
        nargs=3, 
        metavar=("platform", "old_username", "new_username"), 
        type=str,
        help="Changes the username of an account"
    )

    parser.add_argument(
        "-e", "--email",
        nargs=3, 
        metavar=("platform", "old_email", "new_email"), 
        type=str,
        help="Changes the email of an account"
    )

    parser.add_argument(
        "-p", "--password",
        nargs=4, 
        metavar=("platform", "username", "old_password", "new_password"), 
        type=str,
        help="Changes the password of an account"
    )

    parser.add_argument(
        "-d", "--delete",
        nargs=2, 
        metavar=("platform", "username"), 
        type=str,
        help="Deletes an accound credentials"
    )

    parser.add_argument(
        "-a", "--add",
        nargs=4, 
        metavar=("platform", "username", "email", "password"), 
        type=str,
        help="Adds new credentials"
    )

    parser.add_argument(
        "-s", "--show",
        action="store_true",
        help="Show content of the passwords file"
    )

    parser.add_argument(
        "path",
        type=str,
        help="Path to the JSON file where credentials are stored"
    )

    args = parser.parse_args()

    if len(sys.argv)<3 :

        print("Usage: sudo python3 credentials_manager.py <path_to_password_file> <argument>.")
        sys.exit(1)

    path = args.path

    change_file_ownership(path)

    if args.show:
        show_credentials(path)

    elif args.add:
        platform, username, email, password = args.add
        new_credentials(path, platform, username, email, password)

    elif args.delete:
        platform, username = args.delete
        remove_account(path, platform, username)

    elif args.email:
        platform, old_email, new_email = args.email
        update_email(path, platform, old_email, new_email)

    elif args.username:
        platform, old_username, new_username = args.username 
        update_username(path, platform, old_username, new_username)

    elif args.password:
        platform, username, old_password, new_password = args.password
        update_password(path, platform, username, old_password, new_password)
