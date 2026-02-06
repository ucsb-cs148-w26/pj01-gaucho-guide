## Wendy Contreras Martinez – Light/Dark Mode Improvements 
## AI Tool Used

For this experiment, I used Gemini to help improve the light/dark mode implementation in our React app. The goal was to fix a styling issue where dark mode did not cover the entire screen and to make the theme toggle look and feel better.

## What Was Built / Produced

The first change fixed an issue where the background color only changed inside the React container instead of the whole page. The solution was to move the data-theme attribute to the HTML <body> using a useEffect hook, so the theme applies to the entire browser window.

The second change was replacing a basic checkbox with a custom toggle switch. The toggle changes between a day and night look using CSS variables, and includes sun and moon icons that fade in and out depending on the selected theme. The animation and movement of the switch were also improved to feel smoother.

## Reflection

### Usefulness of the AI Tool

The AI was helpful for quickly generating ideas and implementation details, especially for the CSS animations and transitions. Writing the toggle animation and timing functions by hand would have taken longer, and the AI gave a solid starting point that I could adjust afterward. It was most useful for speeding up UI experimentation rather than producing final code right away.

### Ensuring Correctness, Understanding, and Fair Use

The output still needed to be checked carefully. I made sure the data-theme attribute matched the CSS selectors and variables defined in :root, otherwise the theme would not update correctly. I also verified that the SVG icons were imported or defined inline properly to avoid dependency issues. After generating the code, I tested the theme switching manually to make sure everything worked consistently across the page. The AI output worked as a starting point, but changes were still needed to make it fit our project correctly.



## Ria Singh

**AI Tool Used:** ChatGPT

**Experiment Description:**  
I used ChatGPT while developing and testing the Reddit scraper for GauchoGuider. The goal was to evaluate how well the scraper retrieved relevant posts from Reddit based on different keywords (e.g., housing, classes, professors). ChatGPT helped me generate commands to run the scraper locally, suggest test cases with different query parameters, and interpret the output to verify whether the scraped content was relevant and complete.

**Outcomes Produced:**
- Ran the scraper locally with multiple keyword variations
- Exported and reviewed scraped results (CSV/JSON)
- Identified which queries returned useful UCSB-related content
- Confirmed that the scraper was collecting titles, text, and metadata correctly

**Reflection on Usefulness:**  
ChatGPT was helpful for quickly generating test scenarios and troubleshooting local execution issues. It reduced the time needed to figure out command formats and debugging steps. Going forward, this tool could be useful for testing data pipelines, writing small utilities, and validating scraping or preprocessing workflows.

**Validation and Responsible Use:**  
- I manually inspected the scraped data to ensure it was accurate and relevant.
- I verified that the commands worked correctly in the local environment.
- I cross-checked outputs against actual Reddit pages when results looked unusual.
