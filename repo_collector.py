import requests
import time
from datetime import datetime
import pandas as pd
import argparse
import os
from pathlib import Path

# modify this to change what repos are searched for
keyword_list = [
    "webui",
    "store",
    "shop",
    "centre",
    "webapp",
    "recipe",
    "responsive",
    "backend",
    "async",
    "django",
    "social",
    "service",
    "endpoint",
    "application",
    "flask",
    "worker",
    "log",
    "view",
    "tracker",
    "angular",
    "black",
    "calendar",
    "mongodb",
    "frontend",
    "inventory",
    "heroku",
    "tailwind",
    "middleware",
    "sqlite",
    "login",
    "upload",
    "app",
    "csrf",
    "form",
    "dashboard",
    "serializer",
    "router",
    "graphql",
    "mongo",
    "materialize",
    "realtime",
    "reservation",
    "blog",
    "session",
    "template",
    "wiki",
    "model",
    "mobile",
    "database",
    "download",
    "web2py",
    "json",
    "security",
    "forum",
    "chat",
    "actions",
    "booking",
    "server",
    "css",
    "authorization",
    "storage",
    "redis",
    "falcon",
    "bootstrap",
    "unittest",
    "migration",
    "testing",
    "websockets",
    "bulma",
    "management",
    "gallery",
    "portfolio",
    "ci",
    "mvc",
    "yaml",
    "portal",
    "sqlalchemy",
    "monitor",
    "fastapi",
    "report",
    "oauth",
    "metrics",
    "postgresql",
    "mysql",
    "pyramid",
    "jwt",
    "admin",
    "notification",
    "route",
    "monitoring",
    "cookie",
    "analytics",
    "rest",
    "task",
    "bottle",
    "webpack",
    "queue",
    "logging",
    "sql",
    "fullstack",
    "file",
    "token",
    "api",
    "deploy",
    "authentication",
    "http",
    "html",
    "coverage",
    "websocket",
    "ecommerce",
    "auth",
    "framework",
    "web",
    "desktop",
]



def extract_single_repo_info(repo):
    """
    Extracts relevant information from a single repository.

    Args:
        repo (dict): The repository data.

    Returns:
        tuple: A tuple containing the stars count, URL, and name of the repository.
    """

    stars = repo["stargazers_count"]
    url = repo["html_url"]
    name = repo["name"]
    return stars, url, name


def check_authentication(token):
    """
    Checks if the authentication is successful by making a request to the GitHub API.
    Prints the authentication status and the username if successful.
    """

    user_url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    response = requests.get(user_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        print(f"Authentication successful. Welcome, {user_data['login']}!")
        return True
    else:
        print(f"Authentication failed. Status code: {response.status_code}")
        print(response.json())
        return False


def handleRateLimit(response, retries, max_retries):
    """
    Handles rate limit exceeded scenarios.

    Args:
        response (Response): The response object.
        retries (int): The number of retries made.
        max_retries (int): The maximum number of retries allowed.

    Returns:
        bool: True if the rate limit was handled successfully, False otherwise.
    """
    if 'Retry-After' in response.headers:
        retry_after_seconds = int(response.headers['Retry-After'])
        print("Rate limit exceeded. " +
              f"Waiting for {retry_after_seconds}s.")
        time.sleep(retry_after_seconds)
    elif 'X-RateLimit-Reset' in response.headers and 'X-RateLimit-Remaining' in response.headers:
        reset_timestamp = int(response.headers['X-RateLimit-Reset'])
        current_timestamp = int(datetime.utcnow().timestamp())
        wait_time = max(0, reset_timestamp - current_timestamp + 1)  # Adding 1 second to be safe
        print("Rate limit exceeded." +
              f" Waiting for {wait_time} seconds.")
        time.sleep(wait_time)
    else:
        if retries < max_retries:
            wait_time = 60 * (2 ** retries)
            print(f"Rate limit exceeded. Waiting {wait_time}s before retrying.")
            return retries + 1
        else:
            print("Rate limit exceeded. Max retries reached. Exiting.")
            return -1


def search_github_repositories(token,
                               query,
                               language="Python",
                               min_stars=10,
                               max_stars=14):
    """
    Searches for GitHub repositories based on the provided query and filters.

    Args:
        query (str): The search query.
        language (str, optional): The programming language to filter the repositories. Defaults to "Python".
        min_stars (int, optional): The minimum number of stars to filter the repositories. Defaults to 10.
        max_stars (int, optional): The maximum number of stars to filter the repositories. Defaults to 14.

    Returns:
        list: A list of tuples containing the stars count, URL, and name of the repositories.
    """
    base_url = "https://api.github.com/search/repositories"
    headers = {
        "Authorization": f"token {token}"
    } 
    repositories = []
    page = 1
    per_page = 50
    retries = 0
    max_retries = 5  # You can adjust this based on your requirements

    params = {
        "q": f"{query} language:{language} stars:{min_stars}..{max_stars}",
        "per_page": "50",
        "page": page,
    }

    page_results = None
    while True:
        time.sleep(1)
        print("----------")
        print("status:")
        print("term: ", query)
        print("page: ", page)
        print("----------")
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            # update previous result to reflect previous value
            prev_results = page_results
            page_results = response.json()["items"]

            if page_results == prev_results and prev_results != None:
                # always getting same results...
                # no idea why this happens, but often the result stays the same across pages?
                print("Stopping due to repeating output..")
                break

            # iterate through results and extract info
            for res in page_results:
                repo_info = extract_single_repo_info(res)
                # stars, url, name = repo_info
                repositories.append(repo_info)

            if len(page_results) < per_page:
                # if page length not maxed out, its likely the last page
                print("Encountered last page.")
                break
            else:
                # otherwise increment page indicator
                page += 1
                print("Moving to next page: ", page)

        elif response.status_code == 403:  # Rate limit exceeded
            return_value = handleRateLimit(response, retries, max_retries)
            if return_value == -1:
                break
            else:
                retries = return_value
        
        # no other response codes are expected
        else:
            print(f"Error: {response.status_code}")
            break

    return repositories


def append_to_csv(file_path, data):
    """
    Appends the provided data to a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        data (str): The data to append to the CSV file.
    """
    with open(file_path, 'a', encoding='utf-8') as csv_file:
        csv_file.write(data)


def remove_duplicates_and_save(file_path):
    df = pd.read_csv(file_path)
    rows_before = df.shape[0]  # count rows
    df_no_duplicates = df.drop_duplicates()
    rows_after = df_no_duplicates.shape[0]  # count rows
    df_no_duplicates.to_csv(file_path, index=False) # save back to original path
    print(f"Duplicate removal changed row count: {rows_before} -> {rows_after}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Github Repository URL Collector')
    parser.add_argument('--min_stars', type=int, default=11, help='Minimum number of stars')
    parser.add_argument('--max_stars', type=int, default=13, help='Maximum number of stars')
    parser.add_argument('--language', type=str, default='python', help='Programming language')
    parser.add_argument('--token', type=str, required=True, help='GitHub auth token')
    parser.add_argument('--file_batch_index', type=int, default=0, help='Index of the latest "repositories_" csv file (optional, only if continue)')
    parser.add_argument('--starting_point', type=str, default='webui', help='Next term to be queried (optional, only if continue)')
    parser.add_argument('--out', type=str, required=True, help='Output directory path')

    example_usage = """
    This tool will search for GitHub repositories based on the provided
    keywords and filters. For each keyword, it performs a search and
    iterates through the result pages. It will collect the URLs of
    matching repos and store them in CSV files at regular intervals.

    Example usage:
    python repo_collector.py --token YOUR_GITHUB_TOKEN --out ./urlstash
    """

    parser.epilog = example_usage
    args = parser.parse_args()
    min_stars = args.min_stars
    max_stars = args.max_stars
    language = args.language
    token = args.token
    file_batch_index = args.file_batch_index
    starting_point = args.starting_point
    output_path = args.out

    # check that output path exists and token is valid
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    elif os.listdir(output_path):
        print("Warning: The output directory is not empty. You have 5 seconds to abort.")
        time.sleep(5)
    if not check_authentication(token):
        print("Exiting.")
        exit()

    # for statistics
    global_count = 0

    # main loop
    reached_starting_point = False
    for term in keyword_list:

        if term == starting_point:
            # skip all keywords until starting_point is reached
            reached_starting_point = True

        if term != starting_point and not reached_starting_point:
            # skip all keywords until starting_point is reached
            print(f"Skipping term: {term} to resume at set starting point ({starting_point})")
            continue

        # process keyword : search for it
        print(f"currently at: {term}, already collected: {global_count} repos")
        repositories = search_github_repositories(token, 
                                                  term,
                                                  language=language,
                                                  min_stars=min_stars,
                                                  max_stars=max_stars)
        
        # for statistics
        global_count += len(repositories)

        # increment output csv number
        file_batch_index += 1
        print(f"Increase file_batch_index to {file_batch_index}")

        # construct output path
        output_path_iteration = Path(output_path) / f"repositories_{file_batch_index}.csv"

        # actually write to csv at output path
        for repo_info in repositories:
            stars, url, name = repo_info
            append_to_csv(output_path_iteration, f"{name}, {stars}, {url}\n")

        print(f"Repositories appended to '{output_path_iteration}'")
        remove_duplicates_and_save(output_path_iteration)
        print("Sleeping for 60s before searching for next keyword...")
        time.sleep(60)
