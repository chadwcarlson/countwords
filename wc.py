import os
import sys
from collections import Counter
from string import punctuation

# Get environment details from the GitHub Actions runner passed as arguments.
CURRENT_BRANCH=os.environ['GITHUB_BASE_REF']
CURRENT_REPO=os.environ['GITHUB_REPOSITORY']
CURRENT_SHA=os.environ['GITHUB_SHA']
CURRENT_PR=os.environ['GITHUB_REF_NAME']

# Define relevant paths from passed arguments.
ROOT_DIR=sys.argv[1]
COURSES_DIR=sys.argv[2]
COURSES_PATH = os.path.join(ROOT_DIR, COURSES_DIR)
RESULTS_FILE = os.path.join(ROOT_DIR, 'results.md')
TOTALS_FILE = os.path.join(ROOT_DIR, 'totals.txt')

def read_file(file_path):
    """Read the contents of a file.

    Based on: https://github.com/valli180/wordcounts/blob/main/src/wordcounts/wordcounts.py#L5 (MIT License)

    Parameters:
    -----------
    file_path: str
        The path to the file to read
    
    Returns:
    --------
    str
        The contents of the file
    """
    with open(file_path, 'r') as file:
        return file.read()
    
def clean_text(text):
    """Remove punctuation from string, and convert all words to lowercase.

    Based on: https://github.com/valli180/wordcounts/blob/main/src/wordcounts/wordcounts.py#L28 (MIT License)

    Parameters:
    -----------
    test: str
        The text to clean
    
    Returns:
    --------
    str
        The cleaned text
    """
    text = text.lower()
    for p in punctuation:
        text = text.replace(p, "")
    return text

def count_words(input_file):
    """Count words in a text file.

    Based on: https://github.com/valli180/wordcounts/blob/main/src/wordcounts/wordcounts.py#L53 (MIT License)

    Words are made lowercase and punctuation is removed 
    before counting.

    Parameters
    ----------
    input_file : str
        Path to text file.

    Returns
    -------
    collections.Counter
        dict-like object where keys are words and values are counts.
    """
    text = read_file(input_file)
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    return Counter(words)

def get_files(directory):
    """Get word count for all files in a directory.

    Parameters
    ----------
    directory : str
        Path to directory.
    
    Returns
    -------
    dict
        Dictionary containing path and word count (object, value) for each file (str, key).
    """
    count = {}
    running_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                key = os.path.join(root, file).split(COURSES_DIR)[-1]
                count[key] = {
                    'path': os.path.join(root, file),
                    'word_count': count_words(os.path.join(root, file)).total()
                }
                running_count += count[key]['word_count']

    return count, running_count

def get_wc_in_repo(directory, current_branch):
    """Get word count for all files in a repository's given subdirectory (i.e. "courses").
    There is no return value, but a results file is written to the repository, which contains wordcount information 
    and is piped to the GitHub Actions runner's Job summary page.

    Parameters
    ----------
    directory : str
        Path to directory.
    current_branch : str
        Name of the current branch.
    """ 
    all_files, total_wc = get_files(directory)
    with open(RESULTS_FILE, "w") as f:
        
        results = f"""
## Word Count Results (`{current_branch}`)

Total word count [^1]

**{total_wc}**

### Word count by file

| File              | Word count |
| :---------------- | :------ |
"""

        for file, wc in all_files.items():
            results += f"|[courses{file}]({file})| {wc['word_count']} |\n"  

        results += f"""| **Total** | **{total_wc}** |
        
[^1]: Word count as of current commit ([{CURRENT_SHA[:7]}](https://github.com/{CURRENT_REPO}/tree/{CURRENT_SHA})) on the [`branch_name`](https://github.com/{CURRENT_REPO}/tree/{CURRENT_BRANCH}) branch, triggered as a part of pull request [#44](https://github.com/{CURRENT_REPO}/pull/{CURRENT_PR.split("/")[0]}).
"""

        f.write(results)

    with open(TOTALS_FILE, "w") as f:
        f.write(str(total_wc))

if __name__ == '__main__':
    get_wc_in_repo(COURSES_PATH, CURRENT_BRANCH)
