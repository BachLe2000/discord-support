import os
import datetime
import csv
import requests
import git

# Get Github token
github_token = os.getenv('GITHUB_TOKEN')

# Configure Github authentication
session = requests.Session()
session.auth = ('', github_token)

# Replace zendesk and language
# e.g. zendesk = 'https://support.awesomepandas.com'
# language = 'en-US'

zendesk = 'https://support.discord.com/'
language = 'en-US'

date = datetime.date.today()
backup_path = os.path.join(str(date), language)
if not os.path.exists(backup_path):
    os.makedirs(backup_path)

log = []

endpoint = zendesk + '/api/v2/help_center/{locale}/articles.json'.format(locale=language.lower())
while endpoint:
    response = session.get(endpoint)
    if response.status_code != 200:
        print('Failed to retrieve articles with error {}'.format(response.status_code))
        exit()
    data = response.json()

    for article in data['articles']:
        article_id = article['id']
        filename = '{article_id}.html'.format(article_id=article_id)
        filepath = os.path.join(backup_path, filename)
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write(article['body'])
        print('{filename} copied!'.format(filename=filename))

        log.append((filename, article['title'], article['author_id']))

    endpoint = data['next_page']

with open(os.path.join(backup_path, '_log.csv'), mode='wt', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(('File', 'Title', 'Author ID'))
    for article in log:
        writer.writerow(article)

# Commit changes to repository
try:
    repo = git.Repo(os.getcwd())
    repo.git.add('.')
    repo.git.commit(m='Backup update for {date}'.format(date=date.strftime('%Y-%m-%d')))
    repo.git.push()
    print("Changes pushed to Github repository.")
except Exception as e:
    print(f"Failed to push changes to Github repository with error: {e}")
