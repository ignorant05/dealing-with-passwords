#Created by ignorant05 aka oussama baccara 


#Credentials_Manager v2.0

#Use the -h or --help flag for usage

#! /usr/bin/env python3

import sys 
import os 
import json 
import shutil

import ctypes
import platform

import argparse

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


def change_file_ownership(path):

    root_uid = 0
    root_gid = 0

    try :
        
        os.chown(path, root_uid, root_gid)
        os.chmod(path, 0o600)
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


def show_all_credentials(path) :

    file = load_file(path)
    
    terminal_width = shutil.get_terminal_size().columns

    for platform in file['platforms']: 

        p = platform.center(terminal_width)

        print(f"\n{'=' * terminal_width}")
        print(f"{p.upper()}")
        print(f"{'=' * terminal_width}\n")

        users = file['platforms'][platform]['users']
        i=1
        for arg in users:
            print(f"{'$' * terminal_width}\n")
            print(f"»»Account #{i} :\n")
            print(f"{'$' * terminal_width}\n")
            for a in arg :       
                    
                    for key , value in a.items():
                        
                        print(f"[&] {key.capitalize()}: {value} ")
                    print(f"\n{'+' * terminal_width}")
            i+=1
                
        print(f"{'=' * terminal_width}\n")

def show_one_cred(path, platform, username):

    file = load_file(path)

    terminal_width = shutil.get_terminal_size().columns

    p = platform.center(terminal_width)

    print(f"\n{'=' * terminal_width}")
    print(f"{p.upper()}")
    print(f"{'=' * terminal_width}\n")

    user_found = False
    
    users = file['platforms'][platform]['users']
    for user_list in users:
        for item in user_list:
            if "username" in item and item['username'].lower() == username.lower():
                user_found = True
                for item in user_list:
                    for key, value in item.items():
                        print(f"[&] {key.capitalize()}: {value}")
                    print(f"\n{'+' * terminal_width}")
                
        if user_found:
            break

    if not user_found:
        print(f"[-]User '{username}' doesn't exist in this platform.")
        print("\n[?]Try again with a valid username.")
        sys.exit(1)

def get_last_change_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_credentials(path, platform, username, email, password): 

    file = load_file(path) 

    new_credentials = [
            {
                "username" : username,
                "Last time changed": get_last_change_time()},
            {   "email" : email,
                "Last time changed": get_last_change_time()},
            {
                "password" : password,
                "Last time changed": get_last_change_time()}
            ]
    
    platform = platform.lower()

    if 'platforms' not in file:

        file['platforms'] = {}

    if not(platform in file['platforms']):
        
        file['platforms'][platform] = {'users' : []}
        
    file['platforms'][platform]['users'].append(new_credentials)
    save_file(path,file)
    print(f"\n[+] New credentials added for {platform.capitalize()}.")
    

    

def update_password(path, platform, username, old_password, new_password):
    file = load_file(path)  
    platform = platform.lower()

    if platform in file['platforms']:
        
        for user in file['platforms'][platform]['users']:
            
            found_username = False
            found_password = False

            
            for item in user:
                if "username" in item and item['username'].lower() == username.lower():
                    found_username = True 
                if "password" in item and item['password'] == old_password:
                    found_password = True  

           
            if found_username and found_password:
                for item in user:
                    if "password" in item:
                        item['password'] = new_password
                        item['Last time changed'] = get_last_change_time() 

                
                save_file(path, file)  
                
                print(f"\n[+] Password updated for {username} on {platform.capitalize()}.")
                return
        
        print(f"[-] User {username} not found or old password did not match on {platform.capitalize()}.")
    else:
        print(f"[-] Platform {platform.capitalize()} not found.")

    
def update_username(path, platform, old, new):

    file = load_file(path)  
    platform = platform.lower()

    if platform in file['platforms']:

        for user in file['platforms'][platform]['users']:
            
            found_username = False
            
            if avoid_duplication(path,platform, user[0]['username'],new):
                print(f"[-] Account is already in the {platform}.")
                print("[-] Try again with another username and email.")
                sys.exit(1)
            
            for item in user:
                if "username" in item and item['username'].lower() == old.lower():
                    found_username = True 
                

            if found_username :
                for item in user:
                    if "username" in item:
                        item['username'] = new
                        item['Last time changed'] = get_last_change_time() 

                
                save_file(path, file)  
                
                print(f"\n[+] Username {old} updated to {new} on {platform.capitalize()}.")
                return

        print(f"[-] User {username} not found on {platform.capitalize()}.")
    else:
        print(f"[-] Platform {platform.capitalize()} not found.")



def update_email(path, platform, old, new):

    file = load_file(path)
 
    platform = platform.lower()
    
    if platform in file['platforms']:

        for user in file['platforms'][platform]['users']:
            
            found_email = False
            
            if avoid_duplication(path,platform, user[0]['username'],new):
                print(f"[-] Account is already in the {platform}.")
                print("[-] Try again with another username and email.")
                sys.exit(1)
                
            for item in user:
                if "email" in item and item['email'] == old:
                    found_email = True 
                

            if found_email :
                for item in user:
                    if "email" in item:
                        item['email'] = new
                        item['Last time changed'] = get_last_change_time() 

                
                save_file(path, file)  
                
                print(f"\n[+] Email {old} updated to {new} on {platform.capitalize()}.")
                return

        print(f"[-] email {old} not found on {platform.capitalize()}.")
    else:
        print(f"[-] Platform {platform.capitalize()} not found.")

def remove_account (path, platform, username):

    file = load_file(path)

    platform = platform.lower()

    if platform in file['platforms']:

        users = file['platforms'][platform]['users']

        updated_users = [user for user in users if not (
               user[0]['username'].lower() == username.lower()
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
    
def avoid_duplication (path, platform, username, email):

    file = load_file(path)

    platform = platform.lower()

    if platform in file['platforms']:
        for user in file['platforms'][platform]['users']:
            # Check for duplicates in username and email
            user_username = next((item['username'] for item in user if 'username' in item), None)
            user_email = next((item['email'] for item in user if 'email' in item), None)
            
            if user_username == username and user_email == email:
                return True  
    return False  
    



if __name__ == "__main__":

    
    check()
    tool_desc = """\
            A simple tool that manages your social media accounts in a secured way.\n
            Usage: sudo python3 password_manager.py <path_to_password_file> <argument>.\n\n
            Ex : sudo python3 password_manager.py credentials.json -a facebook john john_is_cool@gmail.com i_am_invincible\n\n
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
        help="Changes the username of an account : provide the platform, the old username and the new username."
    )

    parser.add_argument(
        "-e", "--email",
        nargs=3, 
        metavar=("platform", "old_email", "new_email"), 
        type=str,
        help="Changes the email of an account : provide the platform, the old email and the new email."
    )

    parser.add_argument(
        "-p", "--password",
        nargs=4, 
        metavar=("platform", "username", "old_password", "new_password"), 
        type=str,
        help="Changes the password of an account : provide the platform , username , old password and the new password."
    )

    parser.add_argument(
        "-d", "--delete",
        nargs=2, 
        metavar=("platform", "username"), 
        type=str,
        help="Deletes an account from a file: provide platform and username."
    )

    parser.add_argument(
        "-a", "--add",
        nargs=4, 
        metavar=("platform", "username", "email", "password"), 
        type=str,
        help="Add new credentials by providing respectively : platform, username, email and password."
    )

    parser.add_argument(
        "-sa", "--show-all",
        action="store_true",
        help="Show all existing credentials"
    )

    parser.add_argument(
        "-s", "--show",
        nargs=2, 
        metavar=("platform", "username"), 
        type=str,
        help="show credentials of one specified account : provide the platform and the username."
    )

    parser.add_argument(
        "path",
        type=str,
        help="Path to the JSON file where credentials are stored."
    )

    args = parser.parse_args()

    if len(sys.argv)<3 :

        print("Usage: sudo python3 credentials_manager.py <path_to_password_file> <argument>.")
        sys.exit(1)

    path = args.path

    
    change_file_ownership(path)

    if args.show_all:
        show_all_credentials(path)

    elif args.show:
        platform, username = args.show
        show_one_cred(path, platform, username)

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
        
