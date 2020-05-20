from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import math

class Norwegian:
	cruise_urls = []
	cruise_details = []

	def get_cruise_urls(self):
		driver = webdriver.Firefox()
		driver.get("https://www.ncl.com/vacations")
		time.sleep(10)
		try: #close popup that occasionally appears
		    driver.find_element_by_id('simplemodal-close-img').click()
		    print "HTML popup closed."
		except:
			print "No HTML popup found."
		time.sleep(2)
		cruise_count_element = driver.find_element_by_class_name("c78_counter")
		cruise_count = cruise_count_element.find_elements_by_css_selector('span')
		print "Found " + cruise_count[1].text + " cruises."
		iterations = int(math.ceil(int(cruise_count[1].text)/20.0)) #how many times do we need to load more results on the page?
		print "Iterations: " + str(iterations)
		time.sleep(1)
		x = 1
		print("Expanding page...")
		print "Iteration: " + str(x) + "/" + str(iterations)
		while x < iterations: #can change this to 1 to just get first page to test
			more_button = driver.find_element_by_css_selector('.btn.btn-primary.btn-lg') #find "view more results" button
			driver.execute_script("return arguments[0].scrollIntoView();", more_button) #get "view more results" button in view
			driver.execute_script("window.scrollBy(0, -180);") #get "view more results" button in view
			if iterations - x > 1:
				print "Showing results " + str(x * 20) + "/" + cruise_count[1].text
			else:
				print "Showing results " + str(int(cruise_count[1].text) ) + "/" + cruise_count[1].text
			print "Iteration: " + str(x+1) + "/" + str(iterations) + "..."
			time.sleep(3)
			more_button.click()
			time.sleep(1)
			x +=1
		listings=[];
		print("Finding cruise URL's...")
		listings = driver.find_elements_by_class_name("c91_cta")
		for cruise in listings: #find all the cruise urls
			href = cruise.find_element_by_css_selector('a').get_attribute('href')
			if "booking" not in href:
				self.cruise_urls.append(href.split("?")[0]) #get only cruise portion of url, not all the extra arguments
		print("Finished finding cruise URL's")
		driver.close()

	def parse_urls(self):
		number_of_urls = len(self.cruise_urls)
		x = 1
		for url in self.cruise_urls:
			try:
				driver = webdriver.Firefox()
				print "URL: " + str(x) + "/" + str(number_of_urls)
				driver.get(url) #load a cruise page
				time.sleep(1)
				cruise_title = driver.find_element_by_class_name("c66_title")
				cruise_duration_and_boat = driver.find_element_by_class_name("c66_label")
				cruise_embark_port = driver.find_element_by_class_name("c66_subtitle")
				ports_raw = driver.find_element_by_class_name("c237_body")
				ports_list = ports_raw.text.split("\n")
				ports = ""
				for line in ports_list:
					if "," in line:
						ports += line.rstrip()
						ports += "-->"
				ports = ports[:-3]
				print cruise_title.text
				print cruise_duration_and_boat.text
				print cruise_embark_port.text
				print ports
				sailings = driver.find_elements_by_class_name("c158_list_item")
				cabins = driver.find_elements_by_class_name("c154_header")
				this_cruise_details = []
				for sailing in sailings: #for each sailing listing for this particular cruise
					saildates =  sailing.find_element_by_class_name("c160_date").text
					prices =  sailing.find_elements_by_class_name("c164_header")
					cabin_pricing = {}
					indiv_cruise_dict = {}
					indiv_cruise_dict["saildates"] = saildates
					indiv_cruise_dict["cruise_name"] = cruise_title.text + ", " + cruise_duration_and_boat.text + ", " + cruise_embark_port.text
					indiv_cruise_dict["ports"] = ports
					CABIN_TYPES = ["INSIDE", "BALCONY", "OCEANVIEW"] #I only care about these three common cabins
					for cabin_type, cabin_price in zip(cabins,prices):
						if cabin_type.text in CABIN_TYPES:
							indiv_cruise_dict[cabin_type.text] = cabin_price.text
					this_cruise_details.append(indiv_cruise_dict)
				self.cruise_details.append(this_cruise_details)
				x+=1
				driver.close()
			except Exception as e:
				print e
				driver.close()

if __name__ == "__main__":
	start = time.time()
	webscraper = Norwegian()
	webscraper.get_cruise_urls()
	print "Found " + str(len(webscraper.cruise_urls)) + " cruise URLs."
	webscraper.parse_urls()
	print webscraper.cruise_details
	end = time.time()
	print("Time Elapsed: " + str(end - start).split(".")[0] + " seconds.")

