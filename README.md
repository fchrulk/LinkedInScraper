# LinkedInScraper
Getting data from public LinkedIn Account and still on progress to scrape possible data!

## Getting started
This package allow you to get possible public information data on LinkedIn using Python 3.6
Right now, it only can be used to login and retrieve information of your current connections.
The development is still quite far away.

### Prerequisites
I am running on Windows OS, Python 3.6. Below are the packages that I use to create this script.
```
Unidecode==1.0.22
MechanicalSoup==0.11.0
```

### Installing
* Just use pip to installation
```
pip install git+https://github.com/fchrulk/LinkedInScraper/
```

### Example
Here it is an example to start
```
from LinkedInScraper import LinkedInScraper
import argparse

def main():
	scraper = LinkedInScraper.LinkedInScraper(email=args['email'], password=args["password"])
	scraper.get_user_connections(complete=False)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("-email", required=True, type=str, help="Input your LinkedIn email to login")
	ap.add_argument("-password", required=True, type=str, help="Input your LinkedIn password to login")
	args = vars(ap.parse_args())

	main()
```

### Built with
* [**MechanicalSoup**](https://github.com/MechanicalSoup/MechanicalSoup/) - Core package

## Authors

* **Fachrul Kurniansyah** - *LinkedInScraper* - [fchrulk](https://github.com/fchrulk)

You can visit my LinkedIn [here](https://www.linkedin.com/in/fchrulk).

Email : [fchrulk@outlook.com]

