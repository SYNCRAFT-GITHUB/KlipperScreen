import os
import subprocess

base_directory = os.path.dirname(os.path.abspath(__file__))
bash_command = "msgfmt KlipperScreen.po -o KlipperScreen.mo"

def execute_bash_in_folders(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            print(f"[*] Entering directory: {dir_path}")

            os.chdir(dir_path)

            try:
                subprocess.run(bash_command, shell=True, check=True)
                print(f"[*] Command OK in {dir_path}")
            except subprocess.CalledProcessError as e:
                print(f"[X] Error in {dir_path}: {e}")

execute_bash_in_folders(base_directory)

