
# LeetCode Cracker: API-Powered Problem Solving with GPT-4o

## Overview

This project is an approach to showcase my skills with API integrations, using the **OpenAI GPT-4o API** and **prompt engineering**. It demonstrates how accurate you can go with GPT coding when you know how to design your prompts. The entire process, from scraping the problems to solving them and submitting the solutions, is automated. 

Initially, my rank on LeetCode was above **2 million**. After running this project, my rank reached **170** within just 15 days! 

![Rank Change](./rank-1.png)

![Rank Change](./rank-2.png)

Not only did my rank improve, but I also scored higher than **99.9%** of the users across hard, medium, and easy problems! ![Performance](./performance.png)

## Prerequisites

To get started, you will need the following:

1. Python 3.7+
2. Google Chrome (latest version)
3. Selenium
4. WebDriverManager
5. OpenAI Python API
6. PyAutoGUI
7. Pandas

## How it Works

### Step 1: Scraping the Problems

First, you need to scrape the problem links from LeetCode using the provided `scrape.py` script. If you want to focus on a certain type of problems (e.g., Easy, Medium, or Hard), you can manually adjust your filters on the [LeetCode Problems Page](https://leetcode.com/problemset/all/) and copy the custom URL. This allows you to scrape only the problems you're interested in. Here’s the block where you can change the URL:

```python
# In scrape.py
driver.get("https://leetcode.com/problemset/?status=NOT_STARTED&page=1") # Change this URL based on your custom filters.
```

Run the script:

```bash
python scrape.py
```

This will scrape all the problems listed on the LeetCode page and save them to `problems-database.xlsx`.

### Step 2: Solving the Problems

Once you have the list of problems, run the `solver.py` script to solve them. This script uses **GPT-4o** to generate solutions based on the problem description and starter code.

To adjust the generated code's language, log in to your LeetCode account, navigate to any problem, and manually select the target language in the code editor. This selection ensures the solution generated will be in the desired language.

The results will be saved back into the `problems.xlsx` file, along with the solution, the programming language used, and whether the submission was successful.

Run the script:

```bash
python solver.py
```

### Step 3: Analytics and Results

Based on my personal analytics, the **acceptance rate** achieved through this method is **around 87%**, which is impressive given the complexity of some of the problems. ![Acceptance Rate](./acceptance.png)

## Key Features

- **Customizable Scraping**: Adjust filters directly on LeetCode and update the scrape URL to focus on specific problem types.
- **Flexible Language Support**: You can choose which language GPT-4 generates solutions for by adjusting your language preference on LeetCode before running the solver.
- **No Reliance on Other People's Solutions**: This script does not scrape solutions. It uses GPT-4 to independently solve problems based on problem descriptions and starter code.
- **Collaborate and Enhance**: Anyone who wishes to collaborate or enhance this code is welcome to contribute!

## Conclusion

This project demonstrates the power of combining **Selenium**, **OpenAI's GPT API**, and proper **prompt engineering** to automate and solve coding problems at a high level. The results show an impressive improvement in rank and problem-solving capabilities.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests to improve the code or add new features.

---

For any issues or inquiries, please contact me. I'm open to collaboration and excited to continue enhancing this project.
