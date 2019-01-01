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
	
