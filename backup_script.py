import os
import datetime
import csv
import requests
import git

session = requests.Session()

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
        title = '<h1>' + article['title'] + '</h1>'
        filename = '{id}.html'.format(id=article['id'])
        filepath = os.path.join(backup_path, filename)
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write(title + '\n' + article['body'])
        print('{title} copied!'.format(title=article['title']))

        log.append((filename, article['title'], article['author_id']))

    endpoint = data['next_page']

with open(os.path.join(backup_path, '_log.csv'), mode='wt', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(('File', 'Title', 'Author ID'))
    for article in log:
        writer.writerow(article)

# Commit changes to repository
repo = git.Repo(os.getcwd())
repo.git.add('.')
repo.git.commit(m='Backup update for {date}'.format(date=date.strftime('%Y-%m-%d')))
repo.git.push()
