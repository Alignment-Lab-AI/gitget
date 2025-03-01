#!/usr/bin/env python3
"""
A script to clone a GitHub repository (via SSH URL) and produce a single Markdown file
that concatenates the content of every plain text file in the repo.
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

def is_text_file(file_path: str, blocksize: int = 1024) -> bool:
    """
    Determines if a file is a plain text file by reading a block of its content.
    Returns True if the file appears to be text, False if it seems binary.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(blocksize)
            if b'\0' in chunk:
                return False
            # Define allowed characters: printable ASCII (32-126) plus common whitespace (tab, newline, carriage return)
            allowed = set(range(32, 127)) | {9, 10, 13}
            if not chunk:  # empty files are considered text
                return True
            # Count characters not in allowed set
            nontext = sum(byte not in allowed for byte in chunk)
            if nontext / len(chunk) > 0.30:
                return False
    except Exception:
        return False
    return True

def gather_files(root_dir: str) -> list:
    """
    Walks the directory tree under root_dir and returns a sorted list of (relative_path, full_path) tuples.
    The .git directory is ignored and only files that pass the plain text check are included.
    """
    files_list = []
    for current_root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for file_name in files:
            full_path = os.path.join(current_root, file_name)
            if is_text_file(full_path):
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
        description="Clone a GitHub repository and concatenate plain text files into a Markdown file."
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

        print("[INFO] Gathering plain text files from the repository...")
        files = gather_files(repo_dir)
        print(f"[INFO] {len(files)} plain text files found.")

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
