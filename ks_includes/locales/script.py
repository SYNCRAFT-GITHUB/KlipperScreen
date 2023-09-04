import os
import subprocess

# Define the specific location
base_directory = "/Users/rafael/Desktop/Wishbox/git/ks-x1-dev/ks_includes/locales"

# Define the bash command to be executed
bash_command = "msgfmt KlipperScreen.po -o KlipperScreen.mo"

# Function to traverse directories and execute the bash command
def execute_bash_in_folders(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            print(f"Entering directory: {dir_path}")

            # Change the working directory to the current folder
            os.chdir(dir_path)

            # Run the bash command in the current folder
            try:
                subprocess.run(bash_command, shell=True, check=True)
                print(f"Command executed successfully in {dir_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error executing command in {dir_path}: {e}")

# Start the traversal and execution
execute_bash_in_folders(base_directory)

