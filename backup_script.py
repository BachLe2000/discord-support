import os
import csv
import requests
from datetime import datetime
from pathlib import Path
import git


def backup_articles(zendesk_url, language):
    # Replace characters in title that cause issues
    bad_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    title = article['title']
    for char in bad_chars:
        title = title.replace(char, "-")

    # Create the path for the HTML file
    filename = f"{title}.html"
    filepath = f"{language}/{filename}"

    # Save the body of the article to a file
    with open(filepath, mode='w', encoding='utf-8') as f:
        f.write(article['body'])

    print(f"Copied {filename}!")

# Get Github token
github_token = os.getenv('GITHUB_TOKEN')

# Configure Github authentication
session = requests.Session()
session.auth = ('', github_token)

# Define the base URL of the Zendesk help center
zendesk_url = "https://support.discord.com/"

# Define the language of the articles to download
language = "en-us"

# Define the name of the backup file
backup_filename = "support_articles.json"

# Check if the backup file exists and load it
if os.path.exists(backup_filename):
    with open(backup_filename, 'r') as f:
        backup_data = json.load(f)
else:
    backup_data = {"articles": []}

# Retrieve the articles from the help center
articles_data = {"articles": []}
endpoint = f"{zendesk_url}/api/v2/help_center/{language}/articles.json"
while endpoint:
    response = session.get(endpoint)
    response.raise_for_status()
    data = response.json()

    # Append the articles to the list of articles
    for article in data['articles']:
        articles_data["articles"].append(article)

    endpoint = data.get('next_page')

# Save the articles to HTML files and create a list of the article titles
article_titles = []
for article in articles_data["articles"]:
    backup_articles(article, language)
    article_titles.append(article["title"])

# Compare the article titles with the HTML files in the backup and move any missing files to a new "deleted" directory
for article in backup_data["articles"]:
    title = article["title"]
    filename = f"{title}.html"
    if title not in article_titles and os.path.exists(filename):
        deleted_folder = f"{language}/deleted"
        if not os.path.exists(deleted_folder):
            os.makedirs(deleted_folder)
        os.rename(filename, f"{deleted_folder}/{filename}")
        print(f"Moved {filename} to {deleted_folder}")

# Save the articles to the backup file
backup_data["articles"] = articles_data["articles"]
with open(backup_filename, 'w') as f:
    json.dump(backup_data, f, indent=2)


def commit_to_github(repo_path):
    """
    Commit changes in the specified directory to a Github repository.
    """
    try:
        # Open the repository
        repo = git.Repo(repo_path)

        # Add all new and modified files
        repo.git.add('--all')

        # Commit the changes with a message
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        commit_message = f"Article Datamining - {now}"
        repo.git.commit(m=commit_message)

        # Push the changes to Github
        repo.git.push()

        print("Changes pushed to Github repository.")
    except Exception as e:
        print(f"Failed to push changes to Github repository with error: {e}")


if __name__ == "__main__":
    # Set these variables with the URL of your Zendesk help center and the language code
    zendesk_url = "https://support.discord.com"
    language = "en-us"

    # Backup the articles and commit to Github
    backup_articles(zendesk_url, language)
    commit_to_github(Path(__file__).parent)
