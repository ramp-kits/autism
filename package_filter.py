
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import click

PYPI_URL = "https://pypi.org/project/{project_name}/#history"

def get_releases(request):

    soup = BeautifulSoup(request, 'html.parser')
    releases = list()

    for release in soup.find_all('div', class_='release'):
        release_version = release.find('p', class_='release__version').text.strip()
        if not is_numeric(release_version):
            continue
        release_date = try_parsing_date(release.find('time').text.strip())
        releases.append({'version': release_version, 'date': release_date})

    sorted_packages = sorted(releases, key=lambda s: list(map(int, s['version'].split('.'))))

    return sorted_packages


def is_numeric(s):
    for char in s:
        if not char.isdigit() and char not in [" ", ".", ","]:
            return False

    return True


def try_parsing_date(text):
    for fmt in ('%d.%m.%Y', '%d/%m/%Y', '%b %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    click.echo('Not valid date format. Try to use one of this: <31.12.2018>, <31/12/2019> or <2018-12-31>')
    sys.exit(0)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-b', '--before', help='Get latest package before specified date')
@click.argument('packages', nargs=-1, type=click.UNPROCESSED)
def cli(before, packages):
    target_date = try_parsing_date(before) if before else datetime.today()

    required_packages = list()
    not_found = list()

    for package in packages:
        project_url = PYPI_URL.format(project_name=package)
        r = requests.get(project_url)
        if r.status_code is not 200:
            not_found.append(package)
            continue

        releases = get_releases(r.text)
        last_release = None
        for idx, release in enumerate(releases):
            release_date = release['date']
            if release_date > target_date:
                if last_release and last_release['date'] <= release_date:
                    continue
            last_release = release

        required_packages.append({'package': package,
                                  'release_date': last_release['date'],
                                  'release_version': last_release['version']})


    print('pip install ' + ' '.join('{}=={}'.format(p['package'], str(p['release_version'])) for p in required_packages))
    if len(not_found) > 0:
        print('\nCould not find the following packages: {}'.format(' '.join(p for p in not_found)))

if __name__ == '__main__':
    cli()