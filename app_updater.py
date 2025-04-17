import json 
from movrs_apis import get_user_data,read_json_file


def check_version_to_update():
    data = read_json_file("user_cred.json")
    user_data = get_user_data(data.get("logged_user_id"))[0]
    return user_data["version_id"]




def confirm_version_check():
    data = read_json_file("current_state.json")
    current_version = data.get("current_version")
    new_version = check_version_to_update()
    if(new_version == current_version):
        return "Version is uptodate"
    else:
        print(new_version ,"current_version", current_version)
        return "Version needs to be updated"

print(confirm_version_check())
