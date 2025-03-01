#!/usr/bin/env python3
"""
A script to clone a GitHub repository (via SSH URL) and produce a single Markdown file
that concatenates the content of every file in the repo (only including files with certain extensions).
Each file is preceded by a clearly delimited header showing its relative path in the repo.

Usage:
    python3 gitget.py <github_repo_url>

Example:
    python3 gitget.py https://github.com/repo/name
    (or if aliased with start.sh, 'gitget https://github.com/repo/name')

This will create a file named "name.md" in your current working directory.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from multiprocessing import Pool, cpu_count
import asyncio
import aiofiles
from tqdm import tqdm

def convert_https_to_ssh(url: str) -> str:
    """
    Converts an HTTPS GitHub URL to its SSH equivalent.
    e.g. https://github.com/username/repo  -> git@github.com:username/repo.git
    """
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
        path = path.rstrip("/")
        if not path.endswith(".git"):
            path += ".git"
        return f"git@github.com:{path}"
    else:
        return url

def extract_repo_name(url: str) -> str:
    """
    Extracts the repository name from the GitHub URL.
    e.g. https://github.com/username/repo  -> repo
    """
    url = url.rstrip("/")
    repo = url.split("/")[-1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return repo

def clone_repository(ssh_url: str, dest_dir: str) -> None:
    """
    Clones the repository using the provided SSH URL into dest_dir.
    """
    try:
        subprocess.check_call(["git", "clone", ssh_url, dest_dir])
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error: Unable to clone repository {ssh_url}. Details: {e}")

def gather_files(root_dir: str) -> list:
    """
    Walks the directory tree under root_dir and returns a sorted list of (relative_path, full_path) tuples.
    Only files with extensions in the allowed_ext set are included.
    The .git directory is ignored.
    """
    allowed_ext = {'.txt', '.md', '.py', '.cpp', '.js'}  # extend this set as needed
    files_list = []
    for current_root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext in allowed_ext:
                full_path = os.path.join(current_root, file_name)
                rel_path = os.path.relpath(full_path, root_dir)
                files_list.append((rel_path, full_path))
    files_list.sort(key=lambda x: x[0])
    return files_list

def read_file_content(file_tuple):
    """
    Reads the content of a file given as (relative_path, full_path).
    Returns a tuple of (relative_path, content) or an error message if reading fails.
    """
    rel_path, full_path = file_tuple
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        content = f"[Error reading file: {e}]"
    return rel_path, content

async def write_markdown_async(file_results, output_file: str) -> None:
    """
    Asynchronously writes the file contents into a Markdown file.
    Each file's content is preceded by a delimiter header.
    """
    delimiter_length = 80
    async with aiofiles.open(output_file, "w", encoding="utf-8") as md:
        for rel_path, content in file_results:
            delimiter = "\n" + ("-" * delimiter_length) + f" {rel_path} " + ("-" * delimiter_length) + "\n"
            await md.write(delimiter)
            await md.write(content)
            await md.write("\n")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clone a GitHub repository and concatenate selected files into a Markdown file."
    )
    parser.add_argument("repo_url", help="The GitHub repository URL (HTTPS) to clone.")
    args = parser.parse_args()

    # Convert provided HTTPS URL to SSH URL
    ssh_url = convert_https_to_ssh(args.repo_url)
    repo_name = extract_repo_name(args.repo_url)
    # Ensure the output lands in the user's current working directory
    output_file = os.path.join(os.getcwd(), f"{repo_name}.md")

    temp_dir = tempfile.mkdtemp(prefix="repo_clone_")
    try:
        repo_dir = os.path.join(temp_dir, "repo")
        print(f"[INFO] Cloning repository using SSH URL '{ssh_url}' into temporary directory...")
        clone_repository(ssh_url, repo_dir)
        print("[INFO] Repository cloned successfully.")

        print("[INFO] Gathering files from the repository (filtering by allowed extensions)...")
        files = gather_files(repo_dir)
        print(f"[INFO] {len(files)} files found with allowed extensions.")

        print("[INFO] Reading file contents concurrently using multiprocessing with progress bar...")
        with Pool(cpu_count()) as pool:
            file_contents = list(tqdm(pool.imap(read_file_content, files),
                                      total=len(files),
                                      desc="Reading files"))
        
        print(f"[INFO] Writing Markdown file '{output_file}' asynchronously using aiofiles...")
        asyncio.run(write_markdown_async(file_contents, output_file))
        print(f"[INFO] Markdown file '{output_file}' generated successfully.")
    except Exception as error:
        sys.exit(f"[ERROR] {error}")
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
