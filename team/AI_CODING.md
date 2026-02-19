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


## Samuel

**AI Tool Used:** ChatGPT

**Experiment Description:**
I used ChatGPT to help develop a Mermaid graph generator in Cursor for this week’s lab. The goal was to generate diagrams (e.g., workflows and system structures) that could be easily included in project documentation. ChatGPT helped with Mermaid syntax, debugging rendering issues, and refining diagram structure.

**Outcomes Produced:**

* Generated Mermaid diagrams for workflows and component relationships
* Fixed syntax and rendering errors
* Integrated diagram generation into the development workflow
* Created reusable templates for future documentation

**Reflection on Usefulness:**
ChatGPT sped up diagram creation and troubleshooting compared to manually referencing documentation. It made it easier to iterate quickly and produce clean visuals for technical documentation.

**Validation and Responsible Use:**

* Manually reviewed diagrams to ensure accuracy
* Tested Mermaid code locally for correct rendering
* Verified diagrams matched the actual system design

# AI-Assisted Development Report

## Nicholas Kamenica

### AI Tool Used
Cursor (AI-assisted coding)

### Experiment Description
I used Cursor's AI assistance to create an initial proof-of-concept front-end chatbot interface in React. The goal was to quickly validate whether React was the right framework for our chatbot implementation and identify any unexpected technical issues early in the development process. Cursor helped generate the basic component structure and text box interface.

### Outcomes Produced
* Basic chatbot interface with text input box
* Hardcoded response system ("I am an ai chatbot")
* Functional React component structure
* Proof-of-concept demonstrating React viability for the project

### Reflection on Usefulness
Cursor was valuable for rapidly prototyping the initial interface and confirming that React would work without major obstacles. This allowed me to validate the technical approach before investing significant time in manual development. Going forward, I can use AI tools to generate rough drafts of front-end components, then apply my React knowledge to refine and formalize the implementation.

### Validation and Responsible Use
* Tested the generated code to ensure it ran without errors
* Reviewed the React component structure for best practices
* Used the AI output as a starting point, planning to refactor and improve the code manually
* Verified the proof-of-concept met initial requirements before proceeding


## Anjali – OAuth Authentication Implementation
**AI Tool Used** 

For this experiment, I used OpenAI ChatGPT and Anthropic Claude to help with implementing OAuth authentication and debugging backend issues. I mainly asked for short explanations, small code snippets, and help understanding errors while setting up login flows and running the app locally.

**What Was Built / Produced**

With AI assistance, I implemented OAuth login and callback routes, added token verification for protected endpoints, and configured environment variables for client IDs and secrets. I also used the tools to debug dependency problems and runtime errors when trying to start the backend and run the model, which helped me fix missing packages, environment setup issues, and configuration mistakes more quickly.

**Reflection**
**Usefulness of the AI Tool**

The tools were most useful for quickly explaining concepts like OAuth and JWTs and for generating starter code and troubleshooting tips. They saved time during setup and debugging and helped me move forward when I was stuck, making development faster and more educational overall.

**Ensuring Correctness, Understanding, and Fair Use** 

I reviewed all generated code, compared it with documentation, and tested everything locally to make sure it worked correctly. I avoided copying large blocks without understanding them and adjusted the output to match our project, ensuring the final implementation was accurate and appropriate to use.

## Tej - Linking backend and frontend to create a clean workflow 
**AI Tool Used** 

For this experiment, I utilized GPT 5.2 High in order to create the api and tune the validation schema in order to properly setup our backend and frontend calls to the chatbot, including the responses. GPT helped immensely as it saved time creating api calls, and having to manually type out all the schemas we needed. 

**Usefulness** 

The tools were very useful as not only did it explain how it was able to create the pipeline, but also allow me to actively change and edit the code in a way I deemed was more suitable for the project. 

## Krystelle – Profile Page Implementation
**AI Tool Used** : Claude

For this experiment, I used Claude to implement a profile page, used with addition to the OAuth to make it specific towards UCSB students. I asked how we can make it look not only visually pleasing, but also functional. 


**What Was Built / Produced**

With the AI assistance from Claude, I was able to make the profile page connected with OAuth and editable to change information if needed. I was given short explanations of what I needed to do and a list of ways to improve its aesthetic. 

**Reflection**
**Usefulness of the AI Tool**

This tool was useful to clearly and efficiently explain what I needed to do to implement that with our current frontend (with React). The given code was short, but it gave a list of ways to improve its design in different ways.

**Ensuring Correctness, Understanding, and Fair Use** 

I reviewed all generated code and compared it with a previous React and frontend project I worked on to ensure that the code has similar layouts. I tested it locally first to try that all buttons are functional and avoided copying large blocks of code without fully testing it and ensuring that it's correct and what I was looking for.




