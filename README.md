# github_scan

This is a tool designed to collect, download and scan the code of GitHub repositories for specific criteria. Originally developed for a personal university project, this tool provides a convenient way to collect and analyze repositories based on custom requirements.

## Features

Within 48 hours, this tool can easily collect over 10,000 repository URLs, allowing you to efficiently analyze them based on your custom criteria.

- **Search Filtering**: The search supports filtering based on language, min stars, max stars, and keywords
- **Extensible Scanner**: The scanner can be extended easily, grep-like functionality is already implemented
- **Blacklist**: The blacklist feature prevents the processing of already cloned and scanned repositories, ensuring efficiency
- **Hits File**: The hits file contains the names of files/repositories that meet all specified conditions
- **Efficient Processing**: The blacklist contains a list of URLs that have already been processed, allowing for time and computational efficiency
- **GitHub Access Token**: A GitHub access token is only required for utilizing the search API in the repo_collector
- **Independent Usage**: The `repo_collector` and `repo_scanner` can be used independently or asynchronously, providing flexibility
- **Rate Limit Compliance**: The tool respects rate limits to ensure compliance with GitHub's usage policies

## Getting Started

To use this tool, you need to run two scripts either simultaneously or sequentially. Here's how to get started:

1. Run the `repo_collector` script to collect URLs of repositories and save them into CSV files in a designated directory.
2. Run the `repo_scanner` script, which watches the directory and processes the CSV files and their corresponding URLs.
3. It is recommended to redirect the output of the scripts to a file for convenient logging.

> Note: output dir and input dir of repo_collector and repo_scanner have to be the same.

> Note: this version of repo_scanner looks for flask-applications and occurences of the render_string_template function.

> Note: tested with Python 3.12.1 

## Usage

For just using it one-time the information in the Getting Started section is sufficient. 
The paragraph below is only useful if you want to continue a search/scan after it stopped/crashed.

#### repo_collector
- take note of the number of the last repo_csv generated by the repo_collector, pass that as `file_batch_index`
- take note of the last keyword that was processed by the repo_collector, pass that as `starting_point`
- with these two additional parameters, run `repo_collector` as before

It should now continue with the search it was stopped at, and create a new csv. This one search can overlap, but only for that keyword, depending on where it was aborted.

#### repo_scanner
- take note of the number of the last repo_csv that was processed by it, pass that as `file_batch_index`
- with this additional parameter, run `repo_scanner` as before

It should now continue with the cloning & grepping at the correct csv file. Within that file, some URLs might already have been processed, but that is handled by the blacklist.
