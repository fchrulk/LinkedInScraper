from setuptools import setup

exec(open("version.py").read())

setup(
    name='LinkedInScraper',
    version=__version__,                # noqa: F821
    description='Getting data from public LinkedIn Account and still on progress to scrape possible data! ',
    author='LinkedIn',
    maintainer='Fachrul Kurniansyah',
    maintainer_email='fchrulk@outlook.com',
    url='https://github.com/fchrulk/LinkedInScraper',
    license='-',
    packages=["LinkedInScraper"],
    long_description="-",
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=['Unidecode','MechanicalSoup'],
    tests_require=["coverage"],
)