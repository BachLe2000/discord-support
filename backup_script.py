import os
import csv
import requests
from datetime import date
from pathlib import Path
import git


def backup_articles(zendesk_url, language):
    """
    Download all the articles from a Zendesk help center in the specified language,
    and store them as HTML files in a local directory named after today's date and the language.
    """
    # Get Github token
    github_token = os.getenv('GITHUB_TOKEN')

    # Configure Github authentication
    session = requests.Session()
    session.auth = ('', github_token)

    # Create the backup directory with the right name
    backup_path = Path(date.today().strftime('%Y-%m-%d'), language.lower())
    backup_path.mkdir(parents=True, exist_ok=True)

    # Retrieve the articles from the help center
    endpoint = f"{zendesk_url}/api/v2/help_center/{language}/articles.json"
    while endpoint:
        response = session.get(endpoint)
        response.raise_for_status()
        data = response.json()

        # Save each article to a file
        for article in data['articles']:
            try:
                filename = f"{article['title']}.html"
                filepath = backup_path / filename

                # Save the body of the article to a file
                with filepath.open(mode='w', encoding='utf-8') as f:
                    f.write(article['body'])

                print(f"Copied {filename}!")
            except Exception as e:
                print(f"Failed to save article {article['id']} with error: {e}")

        endpoint = data.get('next_page')


def commit_to_github(repo_path):
    """
    Commit any changes in the specified directory to a Github repository.
    """
    try:
        # Open the repository
        repo = git.Repo(repo_path)

        # Add all new and modified files
        repo.git.add('--all')

        # Commit the changes with a message
        commit_message = f"Backup update for {date.today()}"
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
