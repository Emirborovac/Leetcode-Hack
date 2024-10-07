import time
import re
import json
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import openai
import pyautogui

# Initialize OpenAI API key
openai.api_key = ''
client = openai.Client(api_key=openai.api_key)

def start_driver():
    # Set up Chrome options
    options = Options()
    options.add_argument("user-data-dir=C:/Users/Ymir/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")


    driver = webdriver.Chrome(options=options)
    return driver

def reformat_cpp_code(json_data):
    try:
        data = json.loads(json_data)
        cpp_code = data.get('code', '')
        cpp_code = cpp_code.strip()
        cpp_lines = cpp_code.split('\\n')
        formatted_code = '\n'.join(cpp_lines)
        return formatted_code
    except json.JSONDecodeError:
        return "Invalid JSON input."

def save_code_to_file(formatted_code, file_path):
    with open(file_path, 'w') as file:
        file.write(formatted_code)

def reformat_article_with_gpt(combined_text):
    prompt = (
    f"Please provide the most efficient solution code for the following LeetCode problem. The solution must consume the least memory and runtime possible. "
    f"The response should be in JSON format with two keys: 'code' and 'language'. "
    f"Only include the essential function or method as required by the problem, without any tests, examples, comments, print statements, or any extra code. "
    f"Strictly follow the provided function signature and problem requirements, and do not redefine any given structs or classes; use them exactly as described."
    f"**Ignore any comments in the starter code and strictly follow the function signature provided. Do not include any comments or additional explanations in the final code.** "
    f"Ensure that the code adheres to the problem's expected input/output format and fits seamlessly into the provided class definition without requiring any external calls or instantiation. "
    f"\n\nProblem Description and Starter Code (use the function signatures provided, but ignore the comments):\n{combined_text}\n\n"
    f"**IMPORTANT:** If the starter code includes a `Solution` class, ensure that the generated code is wrapped inside this class. "
    f"If the `Solution` class does not exist, generate the necessary function without any class wrapping."
    f"If the code is not MySQL query, the code should be structured and contained as follows:\n"
    f'""class Solution {{\n'
    f"public:\n"
    f"    ........................\n"
    f"}};\"\""
    f"Generate the code in C++ and ensure it aligns perfectly with the provided definitions, unless the problem is not solved by a code, rather by a bash line."

    f"Make sure the syntax is 100% correct."
    f"\n\n**ADDITION FOR BASH PROBLEMS:**"
    f"If the problem involves text processing or shell-related tasks (e.g., manipulating files or output from files), use a Bash script to solve it."
    f"Ensure the script is efficient and follows best practices for Bash."
)

    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a genius, creative, and professional software engineer that solves complex LeetCode problems."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.2
    )

    result = response.choices[0].message.content.strip()
    
    # Print the raw result to debug what GPT returned
    print("Raw GPT response:", result)

    # Extract JSON content from the response
    try:
        json_str = re.search(r'\{.*\}', result, re.DOTALL).group()
        gpt_result = json.loads(json_str)
        return gpt_result
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Failed to decode JSON: {e}")
        return None

def process_problem(url, title):
    # Start the browser and open the problem URL
    driver = start_driver()
    driver.get(url)
    print(f"Opened URL: {url}")

    # Retry logic for fetching problem description and starter code
    for attempt in range(12):  # Increased to 12 attempts for robustness
        try:
            # Fetch problem description
            description_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[4]/div/div[1]'))
            )
            problem_description = description_element.text
            print(f"Fetched problem description.")

            # Fetch starter code
            starter_code_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="editor"]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[5]'))
            )
            starter_code_lines = starter_code_element.find_elements(By.CLASS_NAME, 'view-line')
            starter_code = "\n".join([line.text for line in starter_code_lines])

            # Handle empty starter code
            if starter_code.strip() == "":
                print(f"Starter code is empty, retrying... (Attempt {attempt + 1}/12)")
                driver.refresh()
                time.sleep(3 + attempt)  # Exponential backoff
                continue

            print(f"Fetched starter code snippet:\n{starter_code}")
            break
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
            print(f"Error detected, retrying... (Attempt {attempt + 1}/12): {e}")
            driver.refresh()  # Refresh the page
            time.sleep(3 + attempt)  # Exponential backoff
            continue  # Retry the loop after refresh

        if attempt == 11:  # If the last attempt fails, quit the driver and return failed
            driver.quit()
            print(f"Failed to retrieve necessary elements after 12 attempts: {e}")
            return None, None, "Failed"

    # Combine the problem description and starter code
    combined_text = f"{problem_description}\n\nStarter Code:\n{starter_code}"
    print(combined_text)

    # Get the response from GPT
    gpt_result = reformat_article_with_gpt(combined_text)
    if not gpt_result:
        print("No valid GPT response was received.")
        driver.quit()
        return None, None, "Failed"

    print(f"Received GPT result: {gpt_result}")

    # Create a unique file name based on the problem title
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    file_path = os.path.join(r"C:\Users\Ymir\Desktop\Git Adventure\Leetcode-Cracker\solutions", f"{safe_title}.cpp")

    # Reformat the code and save it
    formatted_code = reformat_cpp_code(json.dumps(gpt_result))
    save_code_to_file(formatted_code, file_path)
    print(f"Saved reformatted code to {file_path}.")

    # Close the browser after fetching the description and starter code
    driver.quit()
    print("Closed the browser.")

    # Open the code in VS Code and copy it
    os.system(f'code "{file_path}"')
    time.sleep(1.5)

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    print("Copied code from VS Code.")

    pyautogui.hotkey('ctrl', 'w')
    print("Closed the VS Code tab.")

    # Reopen the browser and visit the problem page again
    driver = start_driver()
    driver.get(url)
    print(f"Reopened URL: {url}")

    # Retry logic for interacting with the editor and pasting the code
    for attempt in range(12):  # Increased to 12 attempts for robustness
        try:
            editor_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[8]/div/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[5]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", editor_field)
            time.sleep(5)

            # Clear the editor
            editor_field.click()
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            pyautogui.press('backspace')

            # Verify that the editor is empty
            editor_content = driver.execute_script("return arguments[0].innerText;", editor_field)
            if editor_content.strip() == "":
                print("Confirmed that the code editor is cleared.")
                break  # Exit the retry loop on success
            else:
                print("Failed to clear the code editor properly. Retrying...")
                continue
        except (StaleElementReferenceException, TimeoutException) as e:
            print(f"Stale element detected while interacting with the editor, retrying... (Attempt {attempt + 1}/12): {e}")
            driver.refresh()
            time.sleep(3 + attempt)
            continue

        if attempt == 11:  # If the last attempt fails
            print("Failed to clear the editor after 12 attempts. Aborting.")
            driver.quit()
            return None, None, "Failed"

    # Paste the copied code into the editor
    editor_field.click()
    time.sleep(0.25)
    pyautogui.hotkey('ctrl', 'v')
    print("Pasted the code into the editor.")

    # Click the "Run" button and check the result
    try:
        run_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e-locator='console-run-button']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", run_button)
        time.sleep(0.5)
        run_button.click()
        print("Clicked the Run button.")
    except Exception as e:
        print(f"Failed to click the Run button: {e}")
        driver.quit()
        return None, None, "Failed"

    # Check the result status
    try:
        result_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@data-e2e-locator,'console-result')]"))
        )
        result_text = result_element.get_attribute('outerHTML')

        if 'Accepted' in result_text:
            print("Status: Accepted")

            # Click the "Submit" button if the solution is accepted
            try:
                submit_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e-locator='console-submit-button']"))
                )
                submit_button.click()
                print("Clicked the Submit button.")

                # Wait for the submission result
                submission_result_element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@data-e2e-locator='submission-result']"))
                )
                submission_result_text = submission_result_element.text

                if 'Accepted' in submission_result_text:
                    print("Submission Status: Accepted")
                    driver.quit()
                    return formatted_code, "C++", "Yes"
                else:
                    print(f"Submission Status: {submission_result_text}")
                    driver.quit()
                    return formatted_code, "C++", "No"

            except Exception as e:
                print(f"Failed to submit the solution or fetch submission result: {e}")
                driver.quit()
                return formatted_code, "C++", "No"
        elif 'Wrong Answer' in result_text:
            print("Status: Wrong Answer")
            driver.quit()
            return formatted_code, "C++", "No"
        elif 'Compile Error' in result_text:
            print("Status: Compile Error")
            driver.quit()
            return formatted_code, "C++", "No"
        else:
            print("Status: Unknown - Please check manually")
            driver.quit()
            return formatted_code, "C++", "No"
    except Exception as e:
        print(f"Failed to retrieve the result status: {e}")
        driver.quit()
        return None, None, "Failed"

def process_problems_from_excel(file_path):
    df = pd.read_excel(file_path)

    for index, row in df.iterrows():
        title = row['Title']
        url = row['URL']
        print(f"Processing problem: {title} - {url}")
        
        solution, language, submission_status = process_problem(url, title)
        
        df.at[index, 'Solution'] = solution
        df.at[index, 'Programming Language'] = language
        df.at[index, 'Status'] = submission_status
        df.at[index, 'Submitted?'] = submission_status

        df.to_excel(file_path, index=False)
        print(f"Updated Excel sheet with the result for: {title}")

    print("All problems processed.")

excel_file_path = r"C:\Users\Ymir\Desktop\Git Adventure\Leetcode-Cracker\problems-database.xlsx"
process_problems_from_excel(excel_file_path)

print("Script completed.")
