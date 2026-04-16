import os; from os import path


TEXT_WARNING_EMPTY_ADMIN = 'Please enter the discord ID for all users that are supposed to be able to use the \'archive\' functions'
TEXT_WARNING_EMPTY_TOKEN = 'Please enter your discord bot token here'

def is_user_id_valid(user_id:str, verbose:bool = True) -> bool:
    #INFO: I don't know the exact user ID length constraints, but they appear to me as 17-19 digits
    if len(user_id) >= 20 or len(user_id) <= 16:
        if verbose:
            print(f'WARNING: User ID <{user_id}> is invalid length (17 - 19 digits)')
        return False
    if not user_id.isdigit():
        if verbose:
            print(f'WARNING: User ID <{user_id}> contains non-digit characters')
        return False
    return True

def create_token_file(token_path:str) -> None:
    with open(token_path, 'w') as file:
        print(TEXT_WARNING_EMPTY_TOKEN)
        file.write(input('TOKEN file> ').strip())
 
def create_admin_file(admin_path:str) -> None:
    with open(admin_path, 'w') as file:
        print(TEXT_WARNING_EMPTY_ADMIN)
        print('Type \'exit\' to close ADMIN file-writer')     
        while True:
            user_input = input('ADMIN file> ').strip()
            if user_input == 'exit':
                break
            elif not is_user_id_valid(user_input):
                continue
            else:
                print(f"Admin added: <{user_input}>")
                file.write(user_input + "\n")

def create_dir_structure(project_dir:str) -> None:
    os.makedirs(path.join(project_dir, 'output'), exist_ok=True)

    token_path = path.join(project_dir, 'TOKEN')
    if not path.exists(token_path):
        print('ERROR: You need a TOKEN file!')
        create_token_file(token_path)
        print('INFO: Created TOKEN file.')

    admin_path = path.join(project_dir, 'ADMIN')
    if not path.exists(admin_path):
        print('WARNING: You should have a ADMIN file!')
        create_admin_file(admin_path)
        print('INFO: Created ADMIN file.')
 
if __name__ == '__main__':
    create_dir_structure(f"{path.dirname(os.path.abspath(__file__))}")