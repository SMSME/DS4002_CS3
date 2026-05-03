import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# departments to scrape and their group and IDs
dept_config = [
    # STEM
    {"name": "CS",   "id": 31, "group": "STEM"}, 
    {"name": "BIOL", "id": 5,  "group": "STEM"}, 
    {"name": "CHEM", "id": 6,  "group": "STEM"}, 
    {"name": "APMA", "id": 22, "group": "STEM"}, 
    
    # Humanities
    {"name": "SOC",  "id": 32, "group": "Humanities"}, 
    {"name": "PHIL", "id": 20, "group": "Humanities"}, 
    {"name": "HIST", "id": 15, "group": "Humanities"}, 
    {"name": "PSYC", "id": 25, "group": "Humanities"}
]

# Base URL for theCourseForum
base_url = "https://thecourseforum.com"
# User-Agent is a header that identifies the browser making the request.
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

all_reviews = []

def get_course_data_from_page(dept_id, page_num):
    # construct the URL for the department page
    url = f"{base_url}/department/{dept_id}/?page={page_num}"
    try:
        # send get request to URL and store in response
        response = requests.get(url, headers=headers)
        # create BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        courses = []
        
        # Find all course links
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Match /course/CS/2100 - we just need the code and number
            match = re.search(r"/course/([A-Z]+)/(\d+)", href)
            
            # if match is found from the above regex
            if match:
                # set the course code and number
                code = match.group(1)
                num = int(match.group(2))
                
                # filter out introductory courses and graduate courses: 1500 <= Level < 5000
                if 1500 <= num < 5000:
                    # construct the URL for the course page
                    base_course_url = f"{base_url}/course/{code}/{num}/"
                    
                    # if the course number is not already in the list
                    if not any(c['num'] == num for c in courses):
                        # add the course to the list
                        courses.append({
                            "url": base_course_url,
                            "code": code,
                            "num": num
                        })
        return courses
    except:
        return []

def get_professor_links(url):
    try:
        # send get request to URL and store in response
        response = requests.get(url, headers=headers)
        # create BeautifulSoup object out of response text
        soup = BeautifulSoup(response.text, 'html.parser')
        # store professor links in set to avoid duplicates
        prof_links = set()
        
        # find all anchor tags with href attribute
        for a in soup.find_all('a', href=True):
            # get the href attribute
            href = a['href']
            
            # Ignore sorting and filtering links, as well as links to current semester courses or all courses
            if any(x in href.lower() for x in ['sortby', 'order=', 'spring', 'fall', 'winter', 'summer', 'all', 'last_taught', 'rating', 'difficulty', 'gpa']):
                continue
            
            # match /course/14940/12013/ (two numeric IDs) for professor links
            if re.search(r"/course/\d+/\d+/?", href):
                # construct the full link
                full_link = base_url + href if href.startswith("/") else href
                # add the full link to the set
                prof_links.add(full_link)
        # return the list of professor links
        return list(prof_links)
    except:
        # return empty list if error
        return []

def scrape_reviews(url, group, dept):
    # initialize count to 0 to count the number of reviews found
    count = 0
    try:
        # send get request to URL and store in response
        response = requests.get(url, headers=headers)
        # create BeautifulSoup object out of response text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # find the course title
        title_tag = soup.find("h1")
        course_title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        # find all review cards and store in list
        review_cards = soup.find_all("div", class_="review") 
        
        # iterate through each review card
        for card in review_cards:
            # try to extract the text, date, and rating from the review card
            try:
                text_div = card.find("div", class_="review-text-full")
                if not text_div: 
                    text_div = card.find("p")
                if not text_div: 
                    continue
                text = text_div.get_text(strip=True)
                
                # if the text is less than 20 characters, skip
                if len(text) < 20: continue 
                # find the date tag
                date_tag = card.find(id="date")
                # get the text of the date tag
                date = date_tag.get_text(strip=True) if date_tag else "Unknown"

                # find the rating tag
                rating_tag = card.find(id="review-average")
                # if the rating tag is not found, find the rating tag in the class "rating-num"
                if not rating_tag: 
                    rating_tag = card.select_one(".rating-num")
                # get the text of the rating tag
                rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
                rating = rating.strip()
                # add the review to the list of all reviews
                all_reviews.append({
                    "department": dept,
                    "group": group, 
                    "course": course_title,
                    "date": date,
                    "rating": rating,
                    "text": text,
                    "url": url
                })
                # and increment the count
                count += 1
            except:
                # if error, skip
                continue
    except:
        # if error, skip
        pass
    # return the count
    return count

print("Starting Scraper")

# iterate through each department in the dept_config list
for dept in dept_config:
    print(f"\nProcessing {dept['name']} ({dept['group']})")
    # initialize set to store scraped courses and avoid duplicates
    scraped_courses = set() 
    # initialize page to 1
    page = 1
    
    # scan up to 6 pages per department to prevent infinite loops
    # get at most 10 courses per department
    while len(scraped_courses) < 10 and page <= 6:
        # get the course list from the department page
        course_list = get_course_data_from_page(dept['id'], page)
        # if no courses are found, then continue to the next department
        if not course_list: 
            if page == 1: 
                # if no courses are found on Page 1, then specify that the entire department is being skipped
                print("No courses found on Page 1, so skipping department")
            break
        
        # iterate through each course in the course list
        for course in course_list:
            # until 10 courses are scraped, continue
            if len(scraped_courses) >= 10: 
                break
            # if the course number is already in the set, then continue to the next course
            if course['num'] in scraped_courses: 
                continue
            # get the professor links from the course page
            prof_links = get_professor_links(course['url'])
            # if professor links are found, then continue
            if prof_links:
                # initialize reviews found to 0
                reviews_found = 0
                # iterate through each professor link
                for prof_link in prof_links:
                    # add the reviews to the list of all reviews and update the count
                    count = scrape_reviews(prof_link, dept['group'], dept['name'])
                    reviews_found += count
                    # sleep for 0.1 seconds to avoid overwhelming the server
                    time.sleep(0.1)
                
                if reviews_found > 0:
                    # add to scraped_courses if we have found reviews for the course
                    scraped_courses.add(course['num'])
                    print(f"Found {reviews_found} reviews for {course['code']} {course['num']}")
        # go to next page
        page += 1

# create pandas dataframe out of reviews and output to csv if not empty
df = pd.DataFrame(all_reviews)
if not df.empty:
    df.to_csv("../DATA/uva_reviews_final.csv", index=False)
    print(f"\nScraped {len(df)} total reviews")
    print(df.groupby('group').count()['text'])
else:
    print("No reviews found")