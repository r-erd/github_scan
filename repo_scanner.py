import csv
import os
import shutil
import subprocess
import time
import argparse
import os

# brief functionality explanation:
# go through a .csv file with links to github repositories
# for each link :
# clone the repo (first append .git to the link)
# check if the code uses Flask
# check if the code contains the function/string "render_template_string"
# if both is true, print the repository name and the file path
# delete the cloned repository (could also keep if match)
# continue this until 100 repos that match the condition were found


def clone_repository(repo_url, destination, blacklist):
    """
    Clones a repository from the given `repo_url` to the specified `destination` directory.
    (Only if not on blacklist)

    Args:
        github_token (str): The GitHub token used for authentication.
        repo_url (str): The URL of the repository to clone.
        destination (str): The directory where the repository will be cloned.

    Returns:
        bool: True if the repository was cloned successfully, False otherwise.
    """
    repo_url = repo_url.strip()

    if repo_url in blacklist:
        print("already processed this one.")
        return False
    else:
        blacklist.append(repo_url)
        with open("blacklist.txt", 'a') as file:
            file.write(repo_url + '\n')

    try:
        subprocess.run(['git', 'clone', f'{repo_url}.git', destination], check=True)
        print(f"Repository cloned successfully to: {destination}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_url}: {e}")
        return False


def grep(repo_path, string):
    """
    Find files in the given repository path that contain the provided string.

    Args:
        repo_path (str): The path to the repository to scan.

    Returns:
        list: A list of file paths that contain the provided string.
    """
    files_that_match = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if string in content:
                files_that_match.append(file_path)

    return files_that_match


def get_folder_size(folder_path):
    """
    Calculate the total size of a folder and its subfolders.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        int: The total size of the folder in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size


def handle_report(path, report_number, blacklist):
    csv_file_path = os.path.join(path, f'repositories_{report_number}.csv')

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #next(csv_reader)  # there is no header to skip

        repos_found = 0
        for row in csv_reader:
            time.sleep(3)
            if repos_found >= 100:
                break  # Stop if 100 repos are found (have to manually check them)

            repo_name, stars, repo_url = row[0], row[1], row[2]
            repo_destination = './tmp/' + repo_name

            if not os.path.exists(repo_destination):
                os.makedirs(repo_destination)


            print(f"Examining repository: {repo_url}")

            if clone_repository(repo_url, repo_destination, blacklist):
                print(f"Checking repository {repo_name} for Flask and render_template_string")

                # check if the repo is "small" enough so the search doesnt crash us
                # this size estimate is not very precise
                # and it would be better to check before cloning (obv)
                try:
                    size = get_folder_size(repo_destination)
                    mbsize = (size/1024)/1024
                    print("size (mb):", mbsize)
                except:
                    mbsize = 101

                if mbsize > 100:
                    print("repo too big...(or size not measurable)")
                    shutil.rmtree(repo_destination)
                else:
                    try:

                        render_template_files = grep(repo_destination, "render_template_string")
                        flask_files = grep(repo_destination, "flask")

                        if len(flask_files) >= 1:
                            print(f"Flask found in {repo_name}")

                            if render_template_files:
                                print(f"Repository {repo_name} meets the conditions! Render template found in:")
                                for file_path in render_template_files:
                                    print(f"- {file_path}")
                                    # log files with render usage to hits.txt
                                    with open("hits.txt", 'a') as file:
                                        file.write(file_path + '\n')
                                repos_found += 1
                            else:
                                print(f"Repository {repo_name} does not meet the conditions. Deleting...")
                                shutil.rmtree(repo_destination)
                        else:
                            print(f"Flask not found in {repo_name}")
                            shutil.rmtree(repo_destination)

                    except Exception as e:
                        print("Encountered error (skipping): ", e)
                        shutil.rmtree(repo_destination)

                print("\n" + "=" * 40 + "\n")
    
    print(f"Found {repos_found} repositories meeting the conditions.")


def wait_until_report(path, report_number):
    """
    Waits until the specified report file exists in the given path.
    
    Args:
        path (str): The path where the report file is expected to be located.
        report_number (int): The number of the report file to wait for.
    
    Returns:
        None
    """
    while not os.path.exists(os.path.join(path, f"repositories_{report_number}.csv")):
        print(f"File repositories_{report_number}.csv not found. Waiting...")
        time.sleep(5)
    print(f"Found repositories_{report_number}.csv. Starting handling...")


def main():
    parser = argparse.ArgumentParser(description='Github Repository Scanner')
    parser.add_argument('--file_batch_index', type=int, default=1, required=False, help='csv number to start processing at')
    # parser.add_argument('--token', type=str, required=True, help='GitHub auth token')
    parser.add_argument('--dir', type=str, required=True, help='Directory path containing the .csv files')

    example_usage = """
    This tool will clone each of the repositories in the provided CSV file
    and check if they meet the conditions (e.g contain a certain string).
    Repositories meeting the conditions will be printed to the console.
    Recommended: redirect the output to a file for easier analysis.

    Example usage:
    python repo_scanner.py --token YOUR_GITHUB_TOKEN --dir ./urlstash
    """

    parser.epilog = example_usage
    args = parser.parse_args()
    report_number = args.file_batch_index
    path = args.dir

    # check if input path exists
    if not os.path.exists(path):
        print(f"Directory path {path} does not exist.")
        quit()

    blacklist = []
    # initialize blacklist from file, in case it exists
    blacklist_file = './blacklist.txt'
    if not os.path.exists(blacklist_file):
        print(f"{blacklist_file} does not exist. Skipping initialization of blacklist from file."
              " This is regular behaviour on fresh starts.")
    else:
        with open(blacklist_file, 'r', encoding='utf-8', errors='ignore') as file:
            tmp = list(file.readlines())
            blacklist = [el.strip() for el in tmp]
            print(f"Initialized blacklist with {len(blacklist)} URLs.")

    # main loop
    while True:
        wait_until_report(path, report_number)
        handle_report(path, report_number, blacklist)
        report_number += 1
    
if __name__ == "__main__":
    main()
