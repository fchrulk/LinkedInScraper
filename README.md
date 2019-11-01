# LinkedInScraper
Getting data from public LinkedIn Account and still on progress to scrape possible data!

## Getting started
This package allow you to get possible public information data on LinkedIn using Python 3.6
Right now, it only can be used to login and retrieve information of your current connections, get full company information by LinkedIn url, get employees data from company, and search company by keyword.
The development is still quite far away. 

My advice is not to over-take data, maybe just take 50 ~ 100 data per day. LinkedIn can limit data retrieval by notifying "restricted accounts". If this happens, you need to verify your account using a resident card or similar card. So, take your own risk.

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
Or this way if you running on Jupyter Notebook
```
from LinkedInScraper import LinkedInScraper

# Login using your account
scraper = LinkedInScraper.LinkedInScraper(email="your-email", password="your-password")

# Get current connections
scraper.get_user_connections(complete=True)

# Search companies by keyword
scraper.search_companies_by_keyword(keyword="social media")

# Get full information of company
scraper.get_company(url="https://www.linkedin.com/company/upwork", save_as='json')

# Get complete information of employees on a company
## save_as="csv" can be use
scraper.search_employees_by_company(companyName="Upwork", companyUrn="4827017", complete_information=True, save_as='json')

# Get basic information of employees on a company
## save_as="csv" can be use
scraper.search_employees_by_company(companyName="Upwork", companyUrn="4827017", complete_information=False, save_as='json')

```
The folder "LinkedIn_Scrape_Result" will be generated to store the output (JSON Format) after scrape proccess finished.


### Built with
* [**MechanicalSoup**](https://github.com/MechanicalSoup/MechanicalSoup/) - Core package

## Authors

* **Fachrul Kurniansyah** - *LinkedInScraper* - [fchrulk](https://github.com/fchrulk)

#### Feel Free to Discuss :relieved:
:id:LinkedIn&emsp;: [Fachrul Kurniansyah](https://www.linkedin.com/in/fchrulk)<br>
:e-mail:Email&emsp;: fachrul.kurniansyah@gmail.com

