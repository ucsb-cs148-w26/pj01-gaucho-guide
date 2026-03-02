# Team Evaluation Response

This response summarizes how we, as a team, are reacting to the feedback from the reviewers. We looked at all comments together on our Kanban Board and used them to decide what changes matter most right now versus what we see as future or stretch improvements.

---

## 1. Response to Feedback on USER_FEEDBACK_NEEDS.md

Overall, the feedback we received lines up well with the goals in our USER_FEEDBACK_NEEDS.md. Reviewers were able to ask real academic questions and generally found the answers helpful, which supports our North Star Metric around Academic Question Resolution.

One clear takeaway is that **trust and clarity** matter just as much as correctness. Feedback about adding citations, reducing overconfidence, and fixing small UI issues directly connects to our *Perceived Trustworthiness* and *Answer Clarity* metrics. Based on this, we are deciding to:

- Adjust chatbot responses to clearly state when information is based on general knowledge versus official UCSB sources.
- Explore adding lightweight citations or links (e.g., GOLD, department pages, or even Reddit threads when appropriate) to improve trust.
- Tune response length and wording so answers feel helpful without sounding overly confident or robotic.

These decisions reinforce our goal of making answers students would actually use for real course decisions.

---

## 2. Additional Decisions Based on Reviewer Feedback

### Section 2: Product Features as Understood by Reviewers

Reviewers clearly understood and appreciated the Chrome extension and transcript-related features. This tells us our core idea is coming across well.

**Decisions:**
- Prioritize fixing transcript logic so current classes are handled correctly, especially when prerequisites are involved.
- Improve how the chatbot reasons about past vs. in-progress courses to avoid incorrect assumptions.
- Keep the Chrome extension as a core feature and continue treating it as a major value add.

---

### Section 3: Effectiveness, Robustness, and UI/UX

Several reviewers mentioned long loading times and small UI layout issues (chat bar positioning, top bar separation).

**Decisions:**
- Investigate backend and API response times to reduce loading delays, since this directly affects *Time to First Useful Answer*.
- Make small but meaningful UI adjustments to the chat bar spacing and top bar separation to make the interface feel more polished.
- Treat UI fixes as short-term improvements since they are relatively low effort but high impact.

---

### Section 4: Helpfulness of Deployment Instructions and Repo Organization

The reviewers did not run into any blockers during deployment, which is good. That said, we want to make sure the repo stays easy to navigate as the project grows, not just right now. The Kanban board and README were not flagged as confusing, but we think there is still room to make things clearer, especially for someone coming in fresh.

**Decisions:**

- Review the README to make sure it gives a clear picture of what the project is and how everything fits together, not just how to run it.
- Keep the Kanban board organized and up to date so it actually reflects what we're working on.
- As we add features, update DEPLOYMENT.md so the instructions stay simple and accurate.
---

### Section 5: Final Closing Thoughts from Reviewers

Reviewers consistently highlighted the Chrome extension as a strong point and mentioned that the app felt solid overall, with no major errors.

**Decisions:**
- Lean into the Chrome extension as a standout feature during demos.
- Address the most impactful issues raised: trust signals (citations), transcript edge cases, and loading time.
- Treat email verification and profile editing (username changes) as stretch goals, since they improve polish but are not critical to core functionality right now.

---

## Summary

As a team, we feel encouraged by the feedback. The product is already useful, but the biggest opportunities for improvement are around trust, performance, and small UX details. Our next steps focus on making the chatbot feel more reliable and faster, while keeping the features reviewers already liked intact.
