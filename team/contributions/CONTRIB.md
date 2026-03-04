# Team Contributions

## Wendy:

**Code Contributions:**  
I primarily worked on building the frontend of our chatbot. Some of the main features I implemented include:  
- Chat history  
- Transcript attach file  
- Light/dark mode toggle  
- UCSB mascot logo loading screen and animation  
- CSS styling and overall frontend layout  

**Non-Coding Contributions:**  
I collaborated with Krystelle on frontend design decisions. I also helped manage team workflow by making sure **scrums were added, retrospective outcomes were recorded**, and tasks were completed before deadlines.  

**Notes on GitHub Contributors Graph:**  
The contributor graph accurately reflects the amount of work and effort I put into the project, as I made a large number of commits across the frontend and team directory files.  

However, the graph doesn’t fully capture all contributions from some of my teammates:  
- Samuel and Tej handled most of the backend work, even though they have fewer commits showing on GitHub.  
- Ria and Nick focused heavily on backend testing, which is critical work but not always reflected in commit count.  
- Krystelle and Anjali worked extensively on planning, the profile page, and OAuth setup, which involved substantial effort outside of GitHub commits.  

Overall, the graph shows a good picture of my contributions, but it doesn’t tell the full story for everyone. Every team member contributed meaningfully to coding, testing, planning, and design.

Nick 

## Nick 

**Code Contributions:**
-I created an initial frontend of the chatbot for proof of concept with just a chatbox before Wendy and Krystelle went off and made it look much more production ready.
-I utilized a pytho library to scrape a pdf, for students to send in their transcript as context for the chatbot, and the chatbot accurately turns that transcript into a json file to base future classes off of.

**Non-Coding Contributions:**  
In the first couple weeks, I was the scribe for the scrums and sprint meetings, keeping things documented in the github, until that got passed off.

**Notes on GitHub Contributors Graph:**
The graph is accurate for me, as I had a couple big tasks that got implemented in a couple commits in the backend, as well as being the first to push a working React frontend, which shows in the amount of lines I added. 

For others, the github contributors graph isn't so accurate. Anjali and Krystelle, although with a low commit count, worked tirelessly on the Oauth page and the profile page, not much code, but essential to the project.
Samuel and Tej did a lot of work on the Backend, specifically with the APIS, scrapers, and Tej made sure the project connected from top to bottom before the second code freeze.
Ria and Wendy's contributions are accurately shown in the graph.
Every team member contributed meaningfully to coding, testing, planning, and design.
Samuel


## Krystelle:

**Code Contributions:**  
I primarily worked on the frontend design: 
-Editable profile page and connected OAuth
-Frontend layout and CSS styling


**Non-Coding Contributions:**  
* Worked with Wendy on the initial frontend design
* Collaborated with the team and designed the UCSB mascot logo

**Notes on GitHub Contributors Graph**
The contributor graph shows what I contributed and can be see within the frontend layout. Although, the amount of commit counts does not accurately show everyone’s contributions. For me, I primarily worked  by giving my implementation and creative ideas with the frontend and OAuth outside of commits.

Anjali

### Ria

Code Contributions:

I primarily worked on building the Reddit data ingestion pipeline and assisting with backend database integration. Some of the main contributions I made include:

* Implemented the Reddit scraping workflow to collect course-related discussions from relevant subreddits.
* Processed and structured scraped Reddit data so it could be used in the ingestion pipeline.
* Helped prepare Reddit data for embedding and indexing so it could be retrieved through the RAG system.
* Assisted with integrating and organizing data within the Firebase database to support the chatbot backend.

Non-Coding Contributions:

* Participated in sprint planning, standups, and retrospectives throughout the quarter.
* Helped review team documentation and contributed to organizing project structure.

Notes on GitHub Contributors Graph:

The contributor graph reflects some of the coding work I contributed, particularly related to the Reddit scraping pipeline and backend support. Overall, while commit counts show some activity, they do not fully capture the collaborative work involved in backend integration, data preparation, and testing that helped the system function end-to-end.

### Tej

I contributed to the architecture, backend development, and deployment of the Gaucho Guider system.

A major portion of my work involved integrating the Reddit data pipeline into the project’s retrieval-augmented generation (RAG) system. I incorporated the Reddit scraper developed by Ria into the ingestion workflow and configured the vector database infrastructure using Pinecone to store and query embeddings generated from the scraped course discussion data.

I was also responsible for deploying the full application stack and ensuring that the system could run reliably in a production environment. This included configuring the backend services, managing environment setup, and integrating the different components of the pipeline so that the frontend chatbot interface could communicate effectively with the retrieval system.

Another contribution was integrating the chatbot functionality with the Gold Lens interface so that users could access Gaucho Guider directly through the UCSB course review environment. This required coordinating the interaction between the UI layer and the backend RAG system.

During development I also migrated the embedding workflow from Ollama to Google’s Gemini embedding model. This change improved embedding generation reliability and allowed us to simplify parts of the infrastructure while maintaining consistent retrieval performance.

Additionally, I implemented the UCSB course API scraper that collects official course information and feeds it into the system’s knowledge base. This allowed Gaucho Guider to combine structured course metadata with unstructured student discussion data from Reddit.

Beyond individual features, I helped guide several technical and architectural decisions throughout the project. I led discussions around the design of the RAG pipeline, model selection, and the overall system integration strategy to ensure the different components of the project worked together cohesively.
