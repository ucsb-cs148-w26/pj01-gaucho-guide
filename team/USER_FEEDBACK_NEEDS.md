# User Feedback Needs

## What Is Live Right Now

At this stage, Gaucho Guider is a **web-based chatbot interface** that allows UCSB students to log in with their UCSB email and ask academic planning questions in natural language.  

The browser extension, transcript parsing, and long-term planners are not yet deployed, so the metrics below focus **only on the chat experience**, since that is what users will interact with during the demo.

Our core question for feedback is:  
**Does the chatbot give students useful, clear, and trustworthy course-planning help?**

---

## North Star Metric

### Academic Question Resolution Rate

**Definition**  
The percentage of users who feel the chatbot answered their academic question well enough that they would actually use the information to make a course decision.

**Why this represents user value**  
Students are not here just to chat — they want answers they can act on. If the response helps them decide what class to take (or not take), the product is doing its job.

**How to measure (in-class script)**  
1. Ask the tester to type a real academic question they might actually ask (e.g.,  
   *“What are some more laid-back CS courses at UCSB?”*).
2. Let them read the chatbot’s response.
3. Ask:  
   **“Would this answer help you make a real course decision?”** (Yes / Somewhat / No)

**What to record**  
- Yes = success  
- Somewhat = partial success  
- No = failure  

**Success definition**  
- ≥ 70% of users answer **Yes** or **Somewhat**

**Target for Wednesday (early stage)**  
- ≥ 60% Yes or Somewhat

---

## Supporting Metrics

### 1. Answer Clarity Score

**Definition**  
How clear and easy to understand the chatbot’s response feels to students.

**Why this matters**  
Even correct information isn’t useful if it’s confusing, too long, or sounds robotic.

**How to measure**  
After reading the response, ask:  
**“How clear was this answer?”** (1–5 scale)

**What to record**  
- Average clarity score across testers

**Success definition**  
- Average score ≥ 4.0

---

### 2. Perceived Trustworthiness

**Definition**  
Whether students trust the chatbot’s advice enough to take it seriously.

**Why this matters**  
Course planning is high-stakes. If users don’t trust the response, they won’t rely on the product.

**How to measure**  
Ask:  
**“How much do you trust this answer?”** (1–5 scale)

**What to record**  
- Average trust score

**Success definition**  
- Average score ≥ 3.8

---

### 3. Time to First Useful Answer

**Definition**  
How long it takes a user to receive a response they consider helpful.

**Why this matters**  
One major goal of Gaucho Guider is saving students time compared to searching Reddit, GOLD, and other sites.

**How to measure**  
- Start timing when the user hits “Send”
- Stop timing when the response fully appears

**What to record**  
- Time in seconds

**Success definition**  
- ≤ 10 seconds for the first response

---

### 4. Productive Follow-Up Rate

**Definition**  
The percentage of users who ask a follow-up question that *builds on* the previous response, rather than rephrasing the same question to get a better answer.

**Why this matters**  
Follow-up questions can mean two very different things:
- The user is engaged and wants more detail, or
- The original answer wasn’t useful, so they are trying again.

This metric helps distinguish between those two cases.

**How to measure**  
After the first response, observe whether the user’s next message:
- **Builds on the answer** (asks for clarification, examples, or next steps), or
- **Retries the same question** with different wording.

**What to record**
- Productive follow-up  
- Retry / clarification attempt  
- No follow-up

**Success definition**
- ≥ 40% of users have a **productive follow-up**
- ≤ 30% of users retry the same question due to confusion

---

## What Feedback We Want From the Sister Team

Please focus feedback on:

- Where answers felt **unclear, too generic, or too confident**
- What information you expected but didn’t get
- Whether the tone felt helpful or frustrating
- What would make you trust the answer more
- Whether you would actually use this instead of Google, Reddit, or asking friends

“Looks good” is less helpful than pointing out **specific moments** where the chatbot helped or failed.

---

## What We’ll Use This For

We will use these metrics to:
- Tune response length and tone
- Identify gaps in academic knowledge
- Decide what features (transcripts, planners, GOLD Lens) should be prioritized next
- Track improvement across future iterations

Our goal is not perfection yet — it’s learning where the chatbot is already helping and where it clearly isn’t.
