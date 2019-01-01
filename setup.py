from setuptools import setup

exec(open("version.py").read())

setup(
    name='LinkedInScraper',
    version=__version__,
    description='Getting data from public LinkedIn Account and still on progress to scrape possible data! ',
    author='Fachrul Kurniansyah',
    maintainer='Fachrul Kurniansyah',
    maintainer_email='fchrulk@outlook.com',
    url='https://github.com/fchrulk/LinkedInScraper',
    packages=["LinkedInScraper"],
    install_requires=['Unidecode','MechanicalSoup'],
)
