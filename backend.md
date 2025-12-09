
# **BACKEND OVERVIEW FOR GTFS SWEDEN CONVERSATIONAL APP**

*(Prepared for the backend AI agent, assuming the frontend is complete and ready to connect.)*

---

## **1. Project Context (High-Level Narrative)**

We are building a conversational application that allows users to explore Swedish GTFS (General Transit Feed Specification) railway data **through natural language**.

The **frontend is already designed and implemented**. It provides:

* A clean, minimalistic chat interface
* A results viewer for tables/maps
* A structured message flow
* A stable messaging API endpoint expectation

Your goal as the **backend agent** is to design and implement the backend system that powers the natural-language querying, GTFS data access, reasoning, and structured response generation.

The product must enable users—transport planners, commuters, analysts, and curious visitors—to simply ask questions about train schedules, routes, connections, frequencies, stops, service patterns, and receive accurate, data-grounded answers.

The backend is responsible for stitching everything together behind the scenes.

---

## **2. BMAD Method Breakdown**

### **B — BEHAVIOR**

What the backend must *do* in response to user actions.

1. **Accept natural language questions** coming from the frontend chat interface.
2. **Interpret the question** using an LLM and determine the required data operation.
3. **Translate the question into executable actions**, mainly SQL queries over the imported GTFS Sweden dataset.
4. **Execute queries against a local GTFS database** (stops, routes, trips, stop_times, calendars, shapes).
5. **Return structured results**:

   * Tables (departures, stop sequences, service days, travel options)
   * Summaries (earliest/next departure, fastest route)
   * Metadata (warnings, ambiguities)
6. **Convert raw results into clean, readable output** to pass back to the frontend.
7. **Handle follow-up questions** by maintaining context.
8. **Respond gracefully** to incomplete, ambiguous, or invalid user queries.
9. **Provide consistent, predictable JSON output** so the frontend can render the conversation cleanly.
10. **Enforce safeguards**, e.g., prevent full database dumps, overly heavy queries, etc.

---

### **M — MOTIVATION**

Why this backend exists and what problem it solves.

1. **GTFS data is complex and not human-friendly.**
   Users cannot easily look into multiple files—trips, stops, calendars, shapes—and manually interpret relationships.

2. **Transportation questions are inherently multi-step.**
   Example: “What trains go from Stockholm C to Göteborg after 14:00 on Sunday?”
   This requires:

   * Mapping names → stop_ids
   * Matching service days
   * Filtering trips
   * Extracting stop_times
   * Returning only valid connections

3. **Users prefer conversational exploration instead of scripting.**
   Analysts, hobbyists, and commuters can get insights without learning SQL or reading GTFS documentation.

4. **Swedish railway data is rich and underutilized.**
   A conversational backend makes it accessible, queryable, and educational.

5. **The frontend needs a reliable backend pipeline** that converts human-language into structured data reliably.

The backend allows all this by being the system that understands intent, executes the logic, and returns structured answers cleanly.

---

### **A — ABILITY**

What capabilities the backend must provide to enable the required behaviors.

1. **GTFS Import & Data Preparation**

   * Download and load GTFS Sweden static dataset
   * Ensure normalized tables for reliable querying
   * Maintain indices for fast query execution

2. **Natural Language Interpretation**

   * Understand user intent
   * Detect stops, routes, dates, times, directions
   * Handle vague references (“morning”, “later trains”, “this connection”)

3. **Query Planning & Generation**

   * Choose the correct tables
   * Handle multi-join lookups
   * Generate optimized SQL queries

4. **Query Execution**

   * Run database queries safely and efficiently
   * Prevent runaway or full-dump queries

5. **Result Processing**

   * Summaries: shorten verbose datasets
   * Formatting: convert query results into frontend-friendly JSON
   * Classification: tell frontend what kind of data is being sent

6. **Session-level Memory**

   * Maintain context for follow-ups
   * E.g., user asks: “Show me departures from Malmö C” → “Only the high-speed ones now”

7. **Error Handling**

   * Missing stop names
   * Invalid times
   * No matching services
   * Dataset inconsistencies

8. **Frontend Integration**

   * Expose clean API endpoints
   * Maintain a stable message schema
   * Guarantee predictable responses

---

### **D — DETERMINATION**

What constraints and commitments guide backend behavior.

1. **Accuracy over guesswork**

   * If data is not available, say so
   * No hallucinations

2. **Consistency of API outputs**

   * Always return predictable JSON structures
   * Include metadata for the frontend to render tables, summaries, or messages

3. **Safety**

   * Enforce query limits
   * Detect nonsensical or impossible requests

4. **Clarity**

   * Backend explanations should be simple and readable
   * Avoid overly technical language in user-facing responses

5. **Modularity**

   * Natural language reasoning separated from query execution
   * Query engine separated from data ingestion

6. **Extensibility**

   * Ready to incorporate GTFS-RT later for live delays
   * Backend should not require redesign when new features are added

7. **Frontend-Compatible**

   * Backend must return data in a format the existing frontend can consume without adjustments
   * Must support the chat-flow paradigm perfectly

---

## **3. User Storyline (End-to-End Flow)**

### **Personas**

* A commuter checking train options
* A transport analyst exploring timetable patterns
* A curious traveler trying to understand service frequencies
* A student exploring Swedish transport datasets

### **User Flow**

1. User opens the app.
2. They type a natural question:
   “Which trains go from Uppsala to Stockholm tomorrow morning?”
3. Frontend passes the message to backend.
4. Backend interprets the question: detect locations, time window, travel direction.
5. Backend converts understanding into SQL queries.
6. Backend executes queries on the GTFS database.
7. Backend formats results into a structured JSON payload:

   * a summary
   * a data table
   * metadata such as service_id, travel times, earliest departure
8. Frontend displays the result cleanly.
9. User asks a follow-up:
   “Show only the fast ones.”
10. Backend uses context to refine results.
11. Conversation continues fluidly.

The backend owns the intelligence, correctness, and structure of this entire flow.

---

## **4. The Backend’s Single Guiding Principle**

**The backend must translate human language into correct GTFS-grounded answers through structured reasoning, safe execution, and clean integration with the frontend.**

All of its behaviors derive from that principle.

---

## **5. What the Backend AI Agent Should Do Next**

With this overview, the backend agent should now:

1. Define backend architecture that matches the BMAD behavior requirements.
2. Build natural-language → intent → SQL → result pipeline.
3. Create clean, consistent API endpoints for the frontend.
4. Implement safe query execution and context handling.
5. Ensure all outputs follow a structured schema for rendering in the existing frontend.
6. Prepare mocks or sample interactions to validate the design.

---