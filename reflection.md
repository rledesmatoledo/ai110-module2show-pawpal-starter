# PawPal+ Project Reflection

## 1. System Design

1. Create or edit task for pet that includes the duration or the priority of the task.
2. Create a daily plan based on what the owner availability is.
3. View the plan and give reasons behind why it chose that plan.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I used four main classes. Owner holds a name and a list of pets. Pet holds its name, species, breed, and a list of tasks. Task holds the details of one care item (name, duration, priority, category, and whether it recurs). Scheduler does the actual work: it takes a pet's tasks and the available time, prioritizes them, and builds a daily plan with reasoning. I kept the scheduling logic in Scheduler so Pet and Task stay simple data holders. I also added a DailyPlan to hold the result and its reasoning, plus Priority and Recurrence enums so those fields have fixed values instead of loose strings.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. I had the AI review my design and made two changes. I removed explain_reasoning() from Scheduler since DailyPlan already had a reasoning field, so it was storing the same thing twice. I also added a deferred_tasks list to DailyPlan to show tasks that didn't fit in the time available.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
