"""Utility methods for the README-AI tool."""

import re
import tempfile
from pathlib import Path
from typing import List

import git
from tiktoken import get_encoding

import conf


def is_valid_git_repo(url: str) -> bool:
    """Check if a given URL is a valid git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            git.Repo.clone_from(url, temp_dir, depth=1)
        except git.GitCommandError:
            return False
        return True


def clone_repository(url: str, repo_path: Path) -> None:
    """Clone a repository to a temporary directory."""
    try:
        git.Repo.clone_from(url, repo_path, depth=1)
    except git.exc.GitCommandError as exc:
        raise ValueError(f"Error cloning repository: {exc}") from exc


def extract_username_reponame(url):
    """Extract username and repository name from a GitHub URL."""
    pattern = r"https?://github.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)

    if match:
        username, reponame = match.groups()
        return f"{username}/{reponame}"
    else:
        return "Invalid GitHub URL"


def adjust_max_tokens(max_tokens: int, prompt: str, target: str = "Hello!") -> int:
    """Adjust the maximum number of tokens based on the specific prompt."""
    is_valid_prompt = prompt.strip().startswith(target.strip())
    adjusted_max_tokens = max_tokens if is_valid_prompt else max_tokens // 3
    return adjusted_max_tokens


def get_token_count(text: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens


def truncate_text_tokens(text: str, encoding_name: str, max_tokens: int) -> str:
    """Truncate a text string to a maximum number of tokens."""
    encoding = get_encoding(encoding_name)
    encoded_text = encoding.encode(text)[:max_tokens]
    truncated_text = encoding.decode(encoded_text)
    return truncated_text


def is_valid_file(helper: conf.ConfigHelper, path: Path) -> bool:
    """Checks if a file is valid for processing."""
    ignore_dirs = helper.ignore_files.get("directories", [])
    ignore_files = helper.ignore_files.get("filenames", [])
    ignore_extensions = helper.ignore_files.get("extensions", [])
    return (
        path.is_file()
        and all(dir not in path.parts for dir in ignore_dirs)
        and path.name not in ignore_files
        and path.suffix not in ignore_extensions
    )


def is_valid_url(url: str) -> bool:
    """Check if a given string is a valid URL."""
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,63}|[A-Z]{2,63}\.[A-Z]{2,63}))"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(regex.match(url))


def flatten_list(nested_list: List) -> List:
    """Flattens a nested list."""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def format_sentence(text: str) -> str:
    """Clean and format the generated text from the model."""
    # Remove non-letter characters from the beginning of the string
    text = re.sub(r"^[^a-zA-Z]*", "", text)

    # Remove extra white space around punctuation except for '('
    text = re.sub(r"\s*([)'.!,?;:])(?!\.\s*\w)", r"\1", text)

    # Remove extra white space before opening parentheses
    text = re.sub(r"(\()\s*", r"\1", text)

    # Replace multiple consecutive spaces with a single space
    text = re.sub(" +", " ", text)

    # Remove extra white space around hyphens
    text = re.sub(r"\s*-\s*", "-", text)

    return text.strip().strip('"')
