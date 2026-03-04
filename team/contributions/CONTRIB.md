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

Samuel

Krystelle

Anjali

Ria

Tej

I contributed to the architecture, backend development, and deployment of the Gaucho Guider system.

A major portion of my work involved integrating the Reddit data pipeline into the project’s retrieval-augmented generation (RAG) system. I incorporated the Reddit scraper developed by Ria into the ingestion workflow and configured the vector database infrastructure using Pinecone to store and query embeddings generated from the scraped course discussion data.

I was also responsible for deploying the full application stack and ensuring that the system could run reliably in a production environment. This included configuring the backend services, managing environment setup, and integrating the different components of the pipeline so that the frontend chatbot interface could communicate effectively with the retrieval system.

Another contribution was integrating the chatbot functionality with the Gold Lens interface so that users could access Gaucho Guider directly through the UCSB course review environment. This required coordinating the interaction between the UI layer and the backend RAG system.

During development I also migrated the embedding workflow from Ollama to Google’s Gemini embedding model. This change improved embedding generation reliability and allowed us to simplify parts of the infrastructure while maintaining consistent retrieval performance.

Additionally, I implemented the UCSB course API scraper that collects official course information and feeds it into the system’s knowledge base. This allowed Gaucho Guider to combine structured course metadata with unstructured student discussion data from Reddit.

Beyond individual features, I helped guide several technical and architectural decisions throughout the project. I led discussions around the design of the RAG pipeline, model selection, and the overall system integration strategy to ensure the different components of the project worked together cohesively.
