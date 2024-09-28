from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import sys
import os
from datetime import datetime
import logging

#configure logging
logging.basicConfig(level=logging.INFO, filename='scraper.log', format='%(asctime)s - %(levelname)s - %(message)s')
#print(os.getcwd())

# Specify the location of the edge Driver
edge_driver_path = 'C:/Users/William/Documents/EdgeDriver/msedgedriver.exe'

# Create edge options and set the binary location
edge_options = EdgeOptions()

# Create a new instance of the edge driver with edge options
driver = webdriver.Edge()

# Read the input file (CSV file in the same directory)

input_file = 'C:/Users/William/Documents/hackGT/uHaul Webscraper/input.csv'
input_data = pd.read_csv(input_file)
extracted_data = []


# Read the last successful index from a file
last_successful_index = 0

if os.path.exists('last_successful_index.txt'):
    with open('last_successful_index.txt', 'r') as f:
        try:
            last_successful_index = int(f.read().strip())
        except ValueError:
            last_successful_index = 0

# Process count
processed_count = 0

# Retry function
def retry_scrape(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to scrape {url}")
            driver.get(url)  # Open the webpage
            sleep(3)  # Wait for the page to load
            return True  # Return success
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            sleep(2 ** attempt)  # Exponential backoff
            if attempt == max_retries - 1:
                logging.error(f"Failed after {max_retries} attempts to load {url}.")
                return False  # Return failure

    # If we've already processed this row, skip it
for index, row in input_data.iterrows():
    if index < last_successful_index:
         continue
    
    pickup_location_input = row['Pick Up Location']
    dropoff_location_input = row['Drop Off Location']

    if not retry_scrape('https://www.uhaul.com/Truck-Rentals/'):
        logging.error("Failed to load U-Haul page after multiple attempts. Skipping...")
        continue
    try:
        # Check for CAPTCHA
        captcha_elements = driver.find_elements(By.XPATH, "/html/body/main/div/div/div/div/div/div/p")
        if captcha_elements and "Please solve the captcha to continue." in captcha_elements[0].text:
            print("Error: Captcha Detected! Please enable your VPN, or visit Uhaul.com to resolve the captcha, and then restart the program.")
            with open('last_successful_index.txt', 'w') as f:
                f.write(str(index))
            sys.exit(1)

        # Find the pickup location input field using its XPath
        pickup_location = driver.find_element(by='xpath', value='/html/body/main/div[1]/div/div/div[1]/div[2]/div/div[1]/form/fieldset/div/div[2]/div[1]/label/input')
        # Clear any existing value in the pickup location input field
        pickup_location.clear()
        # Take input for Pick up
        pickup_location.send_keys(pickup_location_input)

        # Find the drop-off location input field using its XPath
        dropoff_location = driver.find_element(by='xpath', value='/html/body/main/div[1]/div/div/div[1]/div[2]/div/div[1]/form/fieldset/div/div[2]/div[2]/label/input')
        dropoff_location.clear()
        # Take input DROP OFF
        dropoff_location.send_keys(dropoff_location_input)

        # Get the current date and format it as 'MM/DD/YYYY'
        current_date = datetime.now().strftime('%m/%d/%Y')

        # Find the date input field using its XPath
        date_input = driver.find_element(by='xpath', value='/html/body/main/div[1]/div/div/div[1]/div[2]/div/div[1]/form/fieldset/div/div[2]/div[3]/label/input')
        # Clear any existing date in the field
        date_input.clear()
        # Type the current date into the field
        date_input.send_keys(current_date)

        # Find the "Get Rates" button using its XPath
        get_rates_button = driver.find_element(by='xpath', value='/html/body/main/div[1]/div/div/div[1]/div[2]/div/div[1]/form/fieldset/div/div[2]/div[4]/button')
        # Click the "Get Rates" button
        get_rates_button.click()

        # Give the page time to load
        sleep(5)

        # Wait for the element to be visible
        #wait = WebDriverWait(driver, 10)  # 10 seconds timeout
        #pickup_location = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div/div[1]/div[1]/form/fieldset/div/div[2]/div[1]/label/input')))

        # Extract the pickup and dropoff locations
        locations_xpath = "//h1"
        locations_element = driver.find_element(By.XPATH, locations_xpath)
        

        locations_text = locations_element.text.strip()

        try:
            pickup_location, dropoff_location = locations_text.split(" to ")
        except ValueError:
            print("Error: Unexpected format for locations_text:", locations_text)
            with open('last_successful_index.txt', 'w') as f:
                f.write(str(index))
            break
            #sys.exit(1)

        pickup_location = pickup_location.split("for ")[1] if "for " in pickup_location else pickup_location
        dropoff_location = dropoff_location.split(" on ")[0] if " on " in dropoff_location else dropoff_location

        # Locate and extract the truck types
        truck_type_xpath = "//h3[@class='text-2x']"
        truck_types_elements = driver.find_elements(By.XPATH, truck_type_xpath)
        truck_types = [element.text.strip() for element in truck_types_elements]

        # Locate and extract the rates
        rate_xpath = "//b[@class='block text-3x medium-text-2x text-callout medium-text-base']"
        rate_elements = driver.find_elements(By.XPATH, rate_xpath)
        rates = [element.text.strip() for element in rate_elements]

        # Locate and extract the moving types
        moving_type_xpath = "//dd[@class='text-bold text-xl']"
        moving_type_elements = driver.find_elements(By.XPATH, moving_type_xpath)
        moving_types = [element.text.strip() for element in moving_type_elements]


        # Build the DataFrame
        for truck_type, rate, moving_type in zip(truck_types, rates, moving_types):
            extracted_data.append({
                "Pickup Location": pickup_location,
                "Dropoff Location": dropoff_location,
                "Rate": rate,
                "Truck Type": truck_type,
                "Moving Type": moving_type,
                "Date": current_date
            })

    except Exception as e:  #added
            print(f"Error at index {index}: {e}")  #added
            # Save the data on error  #added
            output_filename = "uhauloutput.xlsx"  #added
            if os.path.exists(output_filename):  #added
                output_data = pd.read_excel(output_filename)  #added
                output_data = output_data.append(extracted_data, ignore_index=True)  #added
            else:  #added
                output_data = pd.DataFrame(extracted_data)  #added

            output_data.to_excel(output_filename, index=False)  #added
            with open('last_successful_index.txt', 'w') as f:  #added
             f.write(str(index))  #added

        # Re-raise the exception to terminate the script  #added
            raise e  #added

    processed_count += 1
    if processed_count == 200: #I set this number to 50, so that the program will only run the first 50 available sets. By changing the numbers, you can control the amount of requests to run.
        break

# Save to Excel
output_filename = "uhauloutput.xlsx"
if os.path.exists(output_filename):
    output_data = pd.read_excel(output_filename)
    output_data = pd.concat([output_data, pd.DataFrame(extracted_data)], ignore_index=True)
else:
    output_data = pd.DataFrame(extracted_data)

output_data.to_excel(output_filename, index=False)

# Close the driver
driver.quit()