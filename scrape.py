import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import selenium  # Explicit import to handle exceptions
import time
# Set up Chrome options
options = Options()
options.add_argument("user-data-dir=C:/Users/<USER>/AppData/Local/Google/Chrome/User Data")# add your user path
options.add_argument("profile-directory=Default")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")

# Set up the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the site
driver.get("https://leetcode.com/problemset/?status=NOT_STARTED&page=1")# This link is Customizable according to your preferneces, you can adjust it manually on Leetcode problems page, and then copy the URL to here.
print("Page loaded.")

# Scroll the dropdown button into view and click it
try:
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-listbox-button-:ra:"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_button)
    dropdown_button.click()
    print("Dropdown button clicked.")
except Exception as e:
    print(f"Failed to click dropdown button: {e}")

# Select the "100 / page" option by its visible text
try:
    hundred_per_page_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "100 / page")]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", hundred_per_page_option)
    hundred_per_page_option.click()
    print("Selected 100 / page option.")
except Exception as e:
    print(f"Failed to select 100 / page option: {e}")

# Refresh the page to ensure the changes take effect
driver.refresh()
print("Page refreshed after selecting 100 / page.")

# Initialize list to hold problem data
problems = []

# Maximum retries for stale elements or other issues
MAX_RETRIES = 3

try:
    while True:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Wait for the problem container to load
                print("Waiting for the problem container to load...")
                time.sleep(5)
                problem_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[4]/div[2]/div[1]/div[4]/div[2]/div/div/div[2]'))
                )
                print("Problem container loaded.")

                # Get all the problem elements within the container
                problem_elements = problem_container.find_elements(By.XPATH, './/div[@role="row"]')
                print(f"Found {len(problem_elements)} problem elements.")

                # Extract the title and URL from each problem element
                for problem in problem_elements:
                    driver.execute_script("arguments[0].scrollIntoView(true);", problem)
                    title_element = problem.find_element(By.XPATH, './/div[@role="cell"][2]//a')
                    title = title_element.text
                    url = title_element.get_attribute('href')
                    problems.append({"Title": title, "URL": url})
                print(f"Extracted {len(problems)} problems so far.")

                # Check if there is a next page
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="next"]'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    next_button.click()
                    print("Clicked next page.")
                    time.sleep(2)  # Wait for the dynamic content to load

                    # Refresh the page to stabilize the DOM
                    driver.refresh()
                    print("Page refreshed after clicking next.")
                except Exception as e:
                    print(f"No more pages or failed to click next: {e}")
                    break
                retry_count = 0  # Reset retry count after successful page load
            except (selenium.common.exceptions.StaleElementReferenceException, selenium.common.exceptions.NoSuchElementException) as e:
                retry_count += 1
                print(f"Encountered an issue: {e}. Retrying... ({retry_count}/{MAX_RETRIES})")
                driver.refresh()  # Refresh and try again
                time.sleep(3)  # Give some time for the page to reload
            if retry_count == 0:  # If successful, no need to retry
                break
        if retry_count >= MAX_RETRIES:
            print("Reached maximum retry attempts. Moving to the next page or stopping.")
            break

finally:
    # Ensure data is saved even if an error occurs
    if problems:
        # Convert the list of problems to a DataFrame
        df = pd.DataFrame(problems)
        # Save the DataFrame to an Excel file
        df.to_excel("problems-database.xlsx", index=False)
        print("Scraping completed and saved to problems.xlsx")
    else:
        print("No problems were scraped.")

    # Close the webdriver
    driver.quit()
