import mechanicalsoup
from getpass import getpass
import json
import re
import os
from pprint import pprint
from unidecode import unidecode

class LinkedInScraper():
    def __init__(self, email, password):
        self.RESULT_DIR = os.getcwd()+"/LinkedIn_Scrape_Result/"
        if not os.path.exists(self.RESULT_DIR):
            os.makedirs(self.RESULT_DIR)
        self.browser = self.start_mechanicalsoup_browser()
        self.credentialInfo = self.login(self.browser, email, password)
        
    def start_mechanicalsoup_browser(self):
        browser = mechanicalsoup.StatefulBrowser()
        return browser
    
    def login(self, browser, email, password):
        login_url = "https://www.linkedin.com/uas/login"
        browser.open(login_url)
        browser.select_form('form[action="/checkpoint/lg/login-submit"]')
        browser['session_key'] = email
        browser['session_password'] = password
        page = browser.submit_selected()
        try:
            print(page.soup.find("div", attrs={"id":"error-for-password"}).text)
        except AttributeError:
            login_info = LinkedInUserExtractor.extract_user_basic_info(source=page, kind="main")
            print("Login success using account {}!".format(login_info['name']))
        return login_info
    
    def get_user_connections(self, complete):
        friends = GetMainConnections(self.browser, self.credentialInfo, self.RESULT_DIR, complete)

class GetMainConnections():
    def __init__(self, browser, credentialInfo, RESULT_DIR, complete=False):
        self.userConnections = self.get_friends(browser, credentialInfo, RESULT_DIR, complete)
        
    def get_friends(self, browser, credentialInfo, RESULT_DIR, complete=False):
        saved_full_name = re.sub("\W","_",unidecode(credentialInfo['name'].lower()))
        RESULT_DIR = RESULT_DIR+credentialInfo['name']+"/"
        if not os.path.exists(RESULT_DIR):
            os.makedirs(RESULT_DIR)
        print("\nCollecting connections from : {}".format(credentialInfo["name"]))
        print("Complete information : {}".format(complete))
        url = "https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH"
        friends = browser.open(url)
        friends = json.loads([i for i in friends.soup.find_all("code") if '"origin":"MEMBER_PROFILE_CANNED_SEARCH"' in i.text][0].text)
        total_friends = friends['data']['paging']['total']
        print("Total friends found : {}".format(total_friends-1))
        friends = friends['data']['elements'][1]['elements']
        temp = []
        with open("{}linkedin_connections_of_{}_{}.json".format(RESULT_DIR,saved_full_name,credentialInfo['publicIdentifier']), "w") as f:
            for friend in friends:
                friend_name = friend['title']['text']
                friend_headline = friend['headline']['text']
                friend_publicIdentifier = friend['publicIdentifier']
                friend_subline = friend['subline']['text']
                friend_url = "https://www.linkedin.com/in/{}".format(friend_publicIdentifier)
                if complete:
                    friend_complete_info = LinkedInAccountScraper.get_account_public_info(browser=browser, url=friend_url, login_info=credentialInfo)
                    friend_init_info = {"name":friend_name,"headline":friend_headline,"publicIdentifier":friend_publicIdentifier,
                                        "location":friend_subline,"url":friend_url}
                    friend_complete_info = {**friend_complete_info, **friend_init_info}
                    if friend_complete_info["publicIdentifier"] != credentialInfo["publicIdentifier"]:
                        f.writelines(json.dumps(friend_complete_info)+"\n")
                        temp.append(friend_complete_info)
                else:
                    friend_init_info = {"name":friend_name,"headline":friend_headline,"publicIdentifier":friend_publicIdentifier,
                                        "location":friend_subline,"url":friend_url}
                    if friend_init_info["publicIdentifier"] != credentialInfo["publicIdentifier"]:
                        f.writelines(json.dumps(friend_init_info)+"\n")
                        temp.append(friend_init_info)
            print("{} friends collected".format(len(temp)), end="\r")
            for i in range(round(total_friends/10+0.45)):
                if i+1 != 1:
                    url_next = url+"&page={}".format(i+1)
                    friends = browser.open(url_next)
                    friends = json.loads([i for i in friends.soup.find_all("code") if '"origin":"MEMBER_PROFILE_CANNED_SEARCH"' in i.text][0].text)
                    total_friends = friends['data']['paging']['total']
                    friends = friends['data']['elements'][0]['elements']
                    for friend in friends:
                        friend_name = friend['title']['text']
                        friend_headline = friend['headline']['text']
                        friend_publicIdentifier = friend['publicIdentifier']
                        friend_subline = friend['subline']['text']
                        friend_url = "https://www.linkedin.com/in/{}".format(friend_publicIdentifier)
                        if complete:
                            friend_complete_info = LinkedInAccountScraper.get_account_public_info(browser=browser, url=friend_url, login_info=credentialInfo)
                            friend_init_info = {"name":friend_name,"headline":friend_headline,"publicIdentifier":friend_publicIdentifier,
                                                "location":friend_subline,"url":friend_url}
                            friend_complete_info = {**friend_complete_info, **friend_init_info}
                            if friend_complete_info["publicIdentifier"] != credentialInfo["publicIdentifier"]:
                                f.writelines(json.dumps(friend_complete_info)+"\n")
                                temp.append(friend_complete_info)
                        else:
                            friend_init_info = {"name":friend_name,"headline":friend_headline,"publicIdentifier":friend_publicIdentifier,
                                        "location":friend_subline,"url":friend_url}
                            if friend_init_info["publicIdentifier"] != credentialInfo["publicIdentifier"]:
                                f.writelines(json.dumps(friend_init_info)+"\n")
                                temp.append(friend_init_info)
                    print("{} friends collected".format(len(temp)), end="\r")
        friends = temp
        del(temp)
        return friends

class LinkedInAccountScraper():
    def get_account_public_info(browser, url, login_info, enable_information=False):
        page = browser.open(url)
        stored_info, target_basic_info = LinkedInUserExtractor.extract_user_basic_info(source=page, kind="target", login_info=login_info)
        target_complete_info = LinkedInUserExtractor.extract_complete_information(browser=browser, stored_info=stored_info, target_basic_info=target_basic_info)
        result = {**target_basic_info, **target_complete_info}
        if enable_information:
            print("Success getting information from : {}".format(url))
        return result

class LinkedInUserExtractor():
    def if_else(key, obj):
        if key in obj:
            value = obj[key]
        else:
            value = None
        return value
    
    def extract_user_basic_info(source, kind, login_info=""):
        info = []
        soup = source.soup.find_all("code")
        for i in soup:
            try:
                i = json.loads(i.text)
            except:
                pass
            if 'data' in i:
                if kind == "target":
                    if i['included'] != [] and login_info["entityUrn_re"] not in str(i):
                        for j in i['included']:
                            info.append(j)
                else:
                    if i['included'] != []:
                        info = i['included']
                        break
        for i in info:
            if "$type" in i:
                if i["$type"] == "com.linkedin.voyager.identity.shared.MiniProfile":
                    target_user_full_name = "{} {}".format(i['firstName'],i['lastName'])
                    target_objectUrn = i['objectUrn']
                    target_occupation = i['occupation']
                    target_entityUrn = i['entityUrn']
                    target_publicIdentifier = i['publicIdentifier']
                    break
        try:
            target_entityUrn_re = re.findall(r"fs_miniProfile:(\S+)$",target_entityUrn)[0]
        except UnboundLocalError:
            for c,i in enumerate(info):
                print(c)
                pprint(i)
                print("\n\n\n")
        target_user_info = {"name":target_user_full_name,"objectUrn":target_objectUrn,"entityUrn":target_entityUrn,
                            "occupation":target_occupation,"publicIdentifier":target_publicIdentifier,
                            "entityUrn_re":target_entityUrn_re}
        if kind == "target":
            temp = []
            for i in info:
                if target_entityUrn_re in str(i):
                    temp.append(i)
            info = temp
            del(temp)
            return info, target_user_info
        else:
            return target_user_info
        
    def extract_complete_information(browser, stored_info, target_basic_info):
        target_friends = 0
        work_experience = []
        education = []
        certification = []
        language = []
        organization = []
        publication = []
        skilled_on = []
        for i in stored_info:
            ## total friends
            if i['$type'] == "com.linkedin.voyager.common.FollowingInfo":
                target_friends = i['followerCount']

            ## work experience
            if i['$type'] == "com.linkedin.voyager.identity.profile.Position":
                work_companyName = i['companyName']
                work_companyUrn = LinkedInUserExtractor.if_else("companyUrn",i)
                work_jobDescription = LinkedInUserExtractor.if_else('description',i)
                work_locationName = LinkedInUserExtractor.if_else('locationName',i)
                work_title = LinkedInUserExtractor.if_else('title',i)
                if 'company' in i:
                    if "industries" in i['company']:
                        work_companyIndustries = i['company']['industries']
                    else:
                        work_companyIndustries = None
                    if "employeeCountRange" in i['company']:
                        if "start" in i['company']['employeeCountRange'] and "end" in i['company']['employeeCountRange']:
                            work_companyEmployee = "{} - {}".format(i['company']['employeeCountRange']['start'],i['company']['employeeCountRange']['end'])
                        elif "start" not in i['company']['employeeCountRange'] and "end" in i['company']['employeeCountRange']:
                            work_companyEmployee = "0 - {}".format(i['company']['employeeCountRange']['end'])
                        elif "start" in i['company']['employeeCountRange'] and "end" not in i['company']['employeeCountRange']:
                            work_companyEmployee = "{} - ~".format(i['company']['employeeCountRange']['start'])
                        else:
                            work_companyEmployee = None
                    else:
                        work_companyEmployee = None
                else:
                    work_companyIndustries = None
                    work_companyEmployee = None
                if "timePeriod" in i:
                    if "year" in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate']:
                        work_timePeriod = "{}/{}".format(i['timePeriod']['startDate']['year'],i['timePeriod']['startDate']['month'])
                    elif "year" not in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate']:
                        work_timePeriod = "-/{}".format(i['timePeriod']['startDate']['month'])
                    elif "year" in i['timePeriod']['startDate'] and "month" not in i['timePeriod']['startDate']:
                        work_timePeriod = "{}/-".format(i['timePeriod']['startDate']['year'])
                    else:
                        work_timePeriod = None
                        
                else:
                    work_timePeriod = None
                work_experience.append({"companyName":work_companyName,
                                        "companyUrn":work_companyUrn,
                                        "jobDescription":work_jobDescription,
                                        "locationName":work_locationName,
                                        "title":work_title,
                                        "companyIndustries":work_companyIndustries,
                                        "timePeriod":work_timePeriod})

            ## education
            if i['$type'] == "com.linkedin.voyager.identity.profile.Education":
                edu_schoolName = i['schoolName']
                edu_schoolUrn = LinkedInUserExtractor.if_else('schoolUrn',i)
                edu_degreeName = LinkedInUserExtractor.if_else('degreeName',i)
                edu_degreeUrn = LinkedInUserExtractor.if_else('degreeUrn',i)
                edu_fieldOfStudy = LinkedInUserExtractor.if_else('fieldOfStudy',i)
                edu_fieldOfStudyUrn = LinkedInUserExtractor.if_else('fieldOfStudyUrn',i)
                edu_activities = LinkedInUserExtractor.if_else('activities',i)
                edu_description = LinkedInUserExtractor.if_else('description',i)
                if "timePeriod" in i:
                    if "startDate" in i['timePeriod'] and "endDate" in i['timePeriod']:
                        edu_timePeriod = "{} - {}".format(i['timePeriod']['startDate']['year'],i['timePeriod']['endDate']['year'])
                    elif "startDate" not in i['timePeriod'] and "endDate" in i['timePeriod']:
                        edu_timePeriod = "Undefined - {}".format(i['timePeriod']['endDate']['year'])
                    elif "startDate" in i['timePeriod'] and "endDate" not in i['timePeriod']:
                        edu_timePeriod = "{} - Present".format(i['timePeriod']['startDate']['year'])
                    else:
                        edu_timePeriod = None
                else:
                    edu_timePeriod = None
                    
                education.append({"schoolName":edu_schoolName,
                                  "schoolUrn":edu_schoolUrn,
                                  "degreeName":edu_degreeName,
                                  "degreeUrn":edu_degreeUrn,
                                  "fieldOfStudy":edu_fieldOfStudy,
                                  "fieldOfStudyUrn":edu_fieldOfStudyUrn,
                                  "activities":edu_activities,
                                  "description":edu_description,
                                  "timePeriod":edu_timePeriod})

            ## certification
            if i['$type'] == "com.linkedin.voyager.identity.profile.Certification":
                cert_authority = LinkedInUserExtractor.if_else('authority',i)
                cert_companyUrn = LinkedInUserExtractor.if_else('companyUrn',i)
                cert_licenseNumber = LinkedInUserExtractor.if_else('licenseNumber',i)
                cert_name = LinkedInUserExtractor.if_else('name',i)
                if "timePeriod" in i:
                    period = i['timePeriod']
                    if 'startDate' in i['timePeriod'] and 'endDate' in i['timePeriod']:
                        if "year" in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate'] and "year" in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "{}/{} - {}/{}".format(period['startDate']['year'],period['startDate']['month'],
                                                                     period['endDate']['year'],period['endDate']['month'])
                        elif "year" in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate'] and "year" in i['timePeriod']['endDate'] and "month" not in i['timePeriod']['endDate']:
                            cert_timePeriod = "{}/{} - {}/-".format(period['startDate']['year'],period['startDate']['month'],
                                                                     period['endDate']['year'])
                        elif "year" in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate'] and "year" not in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "{}/{} - -/{}".format(period['startDate']['year'],period['startDate']['month'],
                                                                    period['endDate']['month'])
                        elif "year" in i['timePeriod']['startDate'] and "month" not in i['timePeriod']['startDate'] and "year" in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "{}/- - {}/{}".format(period['startDate']['year'],
                                                                    period['endDate']['year'],period['endDate']['month'])
                        elif "year" not in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate'] and "year" in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "-/{} - {}/{}".format(period['startDate']['month'],
                                                                    period['endDate']['year'],period['endDate']['month'])
                        else:
                            print("173")
                            pprint(i['timePeriod'])
                    elif 'startDate' not in i['timePeriod'] and 'endDate' in i['timePeriod']:
                        if "year" in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "Undefined - {}/{}".format(period['endDate']['year'],period['endDate']['month'])
                        elif "year" in i['timePeriod']['endDate'] and "month" not in i['timePeriod']['endDate']:
                            cert_timePeriod = "Undefined - {}/-".format(period['endDate']['year'])
                        elif "year" not in i['timePeriod']['endDate'] and "month" in i['timePeriod']['endDate']:
                            cert_timePeriod = "Undefined - -/{}".format(period['endDate']['month'])
                        else:
                            print("183")
                            pprint(i['timePeriod'])
                    elif 'startDate' in i['timePeriod'] and 'endDate' not in i['timePeriod']:
                        if "year" in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate']:
                            cert_timePeriod = "{}/{} - No expires".format(period['startDate']['year'],period['startDate']['month'])
                        elif "year" in i['timePeriod']['startDate'] and "month" not in i['timePeriod']['startDate']:
                            cert_timePeriod = "{}/- - No expires".format(period['startDate']['year'])
                        elif "year" not in i['timePeriod']['startDate'] and "month" in i['timePeriod']['startDate']:
                            cert_timePeriod = "-/{} - No expires".format(period['startDate']['month'])
                        else:
                            print("193")
                            pprint(i['timePeriod'])
                    else:
                        cert_timePeriod = None
                else:
                    cert_timePeriod = None
                cert_url = LinkedInUserExtractor.if_else('description',i)
                certification.append({"authority":cert_authority,
                                      "companyUrn":cert_companyUrn,
                                      "licenseNumber":cert_licenseNumber,
                                      "name":cert_name,
                                      "timePeriod":cert_timePeriod,
                                      "url":cert_url})

            ## language
            if i['$type'] == "com.linkedin.voyager.identity.profile.Language":
                lang_name = i['name']
                lang_proficiency = LinkedInUserExtractor.if_else('proficiency',i)
                language.append({"name":lang_name,"proficiency":lang_proficiency})

            ## organization
            if i['$type'] == "com.linkedin.voyager.identity.profile.Organization":
                org_name = LinkedInUserExtractor.if_else('name',i)
                org_position = LinkedInUserExtractor.if_else('position',i)
                if "timePeriod" in i:
                    if "startDate" in i['timePeriod'] and "endDate" in i['timePeriod']:
                        org_timePeriod = "{} - {}".format(i['timePeriod']['startDate']['year'],i['timePeriod']['endDate']['year'])
                    elif "startDate" not in i['timePeriod'] and "endDate" in i['timePeriod']:
                        org_timePeriod = "Undefined - {}".format(i['timePeriod']['endDate']['year'])
                    elif "startDate" in i['timePeriod'] and "endDate" not in i['timePeriod']:
                        org_timePeriod = "{} - Present".format(i['timePeriod']['startDate']['year'])
                    else:
                        org_timePeriod = None
                else:
                    org_timePeriod = None
                organization.append({"name":org_name,"position":org_position,"timePeriod":org_timePeriod})

            ## publication
            if i['$type'] == "com.linkedin.voyager.identity.profile.Publication":
                pub_name = LinkedInUserExtractor.if_else('name',i)
                if "date" in i:
                    if "year" in i['date'] and "month" in i['date'] and "day" in i['date']:
                        pub_date = "{}/{}/{}".format(i['date']['year'],i['date']['month'],i['date']['day'])
                    
                    elif "year" not in i['date'] and "month" in i['date'] and "day" in i['date']:
                        pub_date = "-/{}/{}".format(i['date']['month'],i['date']['day'])
                    elif "year" in i['date'] and "month" not in i['date'] and "day" in i['date']:
                        pub_date = "{}/-/{}".format(i['date']['year'],i['date']['day'])
                    elif "year" in i['date'] and "month" in i['date'] and "day" not in i['date']:
                        pub_date = "{}/{}/-".format(i['date']['year'],i['date']['month'])
                        
                    elif "year" in i['date'] and "month" not in i['date'] and "day" not in i['date']:
                        pub_date = "{}/-/-".format(i['date']['year'])
                    elif "year" not in i['date'] and "month" in i['date'] and "day" not in i['date']:
                        pub_date = "-/{}/-".format(i['date']['month'])
                    elif "year" not in i['date'] and "month" not in i['date'] and "day" in i['date']:
                        pub_date = "-/-/{}".format(i['date']['day'])
                    else:
                        pub_date = None
                else:
                    pub_date = None
                pub_description = LinkedInUserExtractor.if_else('description',i)
                pub_publisher = LinkedInUserExtractor.if_else('publisher',i)
                pub_url = LinkedInUserExtractor.if_else('url',i)
                publication.append({"name":pub_name,
                                    "date":pub_date,
                                    "description":pub_description,
                                    "publisher":pub_publisher,
                                    "url":pub_url})

            ## skill
            skill = []
            if i['$type'] == "com.linkedin.voyager.identity.profile.SkillView":
                for r in range(i['paging']['total']):
                    skill = []
                    code = "({},{})".format(target_basic_info['entityUrn_re'],r)
                    skill_ = browser.open("https://www.linkedin.com/in/{}/detail/skills/{}".format(target_basic_info['publicIdentifier'],code))
                    skill_ = skill_.soup.find_all("code")
                    skills = []
                    for s in skill_:
                        if "profile.Skill" in s.text and code in s.text:
                            skills.append(s.text)
                    try:
                        skills = [s for s in json.loads(skills[1])['included'] if "name" in s]
                        for s in skills:
                            skill.append({"name":s['name']})
                    except:
                        pass
                    if len(skill) == i['paging']['total']:
                        break
                skilled_on = skill
                del(skill)
                
        email, phone, address, twitter = LinkedInUserExtractor.get_contact_info(browser, target_basic_info['publicIdentifier'])
        target_complete_info = {"friends":target_friends,"experience":work_experience,"education":education,
                                "language":language,"certification":certification,"organization":organization,
                                "publication":publication,"skill":skilled_on,"email":email,"phone":phone,"address":address,
                                "twitter":twitter}
        return target_complete_info
    
    def get_contact_info(browser, publicIdentifier):
        url = "https://www.linkedin.com/in/{}/detail/contact-info/".format(publicIdentifier)
        contact = browser.open(url)
        try:
            contact = json.loads([i for i in contact.soup.find_all('code') if "profile.ProfileContactInfo" in str(i)][0].text)
            if 'emailAddress' in contact['data']:
                email = contact['data']['emailAddress']
            else:
                email = None
            phone = []
            if "phoneNumbers" in contact['data']:
                for p in contact['data']['phoneNumbers']:
                    phone.append({p['type'].lower():p['number']})
            if 'address' in contact['data']:
                address = contact['data']['address']
            else:
                address = None
            twitter = []
            if "twitterHandles" in contact['data']:
                for t in contact['data']['twitterHandles']:
                    twitter.append(t)
            return email, phone, address, twitter
        except:
            print(contact.soup.prettify())
            print(url)

