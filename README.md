
# GitGet

GitGet is a utility that helps you clone a GitHub repository using SSH, parse all of its files, and concatenate them into a single Markdown file with clear delimiters. It comes with two scripts:

1. **`gitget.py`**  
   A Python script that:
   - Converts a provided GitHub HTTPS URL into an SSH URL.
   - Clones the repository into a temporary directory.
   - Uses multiprocessing with a progress bar (via `tqdm`) to read all files concurrently.
   - Asynchronously writes a single Markdown file (named after the repository) into your current working directory, where each file is clearly delimited.

2. **`install_gitget.sh`**  
   A shell script that:
   - Moves `gitget.py` from your working directory to a standard location (e.g. `$HOME/.local/bin` on Linux or `$HOME/bin` on macOS).
   - Renames the script to `gitget` and marks it as executable.
   - Sets up a permanent alias (`gitget`) in your shell configuration file (Bash on Linux, Zsh on macOS) so you can run the command from anywhere.

## Features

- **SSH URL Conversion:** Automatically converts HTTPS GitHub URLs to SSH URLs.
- **Multiprocessing & Progress Bar:** Leverages multiprocessing with `tqdm` to show progress while reading files.
- **Asynchronous File Writing:** Uses `aiofiles` for non-blocking file writes.
- **Easy Installation:** A helper shell script moves the utility into your user path and sets up a convenient alias.

## Requirements

- Python 3.6+
- Git
- A Unix-like environment (Linux/macOS)

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

## Usage

After installing the utility, you can simply use the alias:

```bash
gitget <github_repo_url>
```

For example:

```bash
gitget https://github.com/username/repository
```

This command will:
- Clone the repository via SSH.
- Concatenate all repository files into a Markdown file named `repository.md` in your current working directory.

## Installation Instructions

Below are the steps to install GitGet by cloning its repository and running the installation script.

### For Linux

Open your terminal and paste the following commands:

```bash
git clone https://github.com/Alignment-Lab-AI/gitget.git
cd gitget
pip install -r requirements.txt
./install_gitget.sh
```

After running these commands, restart your terminal or run:

```bash
source ~/.bashrc
```

to load the new alias.

### For macOS

Open your terminal and paste the following commands:

```bash
git clone https://github.com/Alignment-Lab-AI/gitget.git
cd gitget
pip install -r requirements.txt
./install_gitget.sh
```

After running these commands, restart your terminal or run:

```bash
source ~/.zshrc
```

to load the new alias.

## Setting Up SSH Access on GitHub

To allow GitGet to clone repositories via SSH, follow these steps:

1. **Generate an SSH Key (if you don’t already have one):**

   Open your terminal and run:

   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

   If your system doesn’t support Ed25519, use RSA:

   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

   Follow the prompts and accept the default file location.

2. **Add Your SSH Key to the SSH Agent:**

   Start the SSH agent in the background:

   ```bash
   eval "$(ssh-agent -s)"
   ```

   Add your SSH private key to the agent:

   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

   (Replace `id_ed25519` with `id_rsa` if you generated an RSA key.)

3. **Add the SSH Key to Your GitHub Account:**

   Display your public SSH key with:

   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

   Copy the output, then go to [GitHub SSH settings](https://github.com/settings/keys) and click on **"New SSH key"**. Paste your key there and save it.

4. **Test Your SSH Connection:**

   Run:

   ```bash
   ssh -T git@github.com
   ```

   You should see a message like:

   ```
   Hi username! You've successfully authenticated, but GitHub does not provide shell access.
   ```

Now you’re ready to use GitGet!
```

---

Below is the `requirements.txt` file:

```txt
aiofiles
tqdm
```

These files together provide everything you need to install and use GitGet. Enjoy!
