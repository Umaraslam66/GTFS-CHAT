
**Purpose:** Build the complete frontend for a minimalistic conversational GTFS-Sweden data exploration app.
**Scope:** Frontend only. Must follow professional design, UX, structure, and styling standards.

---

## **1. Product Overview**

Build a frontend UI for an application that allows users to query Swedish GTFS data in natural language.
The UI consists of:

* A **clean conversation interface**
* A minimal **assistant pane**
* A simple **data result viewer**
* A modular **component structure**
* A minimal theme that feels Scandinavian: calm, clean, neutral colors

No backend logic needed; mock API calls are fine.

---

## **2. Core Design Principles (Mandatory)**

### **Minimalism**

* Use a restrained color palette: soft grey, white, muted blue accents.
* Zero visual clutter.
* Maximum whitespace.
* No shadows unless subtle and necessary.

### **Professionalism**

* Typography hierarchy: clear headings, medium-weight body text, consistent spacing.
* All interactive elements should feel intentional and unobtrusive.
* Responsive design must be perfect on desktop + mobile.

### **Modern Scandinavian Aesthetic**

* Soft rounded corners (4–6px)
* Neutral tones
* Clean grids and spacing rules
* No flashy gradients, animations, or large decorative elements.

### **Accessibility**

* High-contrast text
* Keyboard navigation
* ARIA labels for key components

---

## **3. Required Screens & Components**

### **A. Main Screen**

A vertically centered layout with:

1. **Header Bar**

   * App name: *GTFS Sweden Chat*
   * Minimal top border or left padding indicator instead of full bar
   * Right side: placeholder for settings icon (no functionality)

2. **Chat Interface**

   * User messages on the right
   * Agent messages on the left
   * Bubbles are subtle rectangles with soft corners
   * Max-width constraint for readability

3. **Message Input Area**

   * Sticky bottom
   * Wide input field with placeholder: *Ask anything about Swedish train schedules…*
   * Send button using a minimalist icon

4. **Results Renderer**
   Whenever the agent returns structured data (e.g., tables):

   * Display a clean data card under the agent’s message
   * Table styling:

     * No heavy borders
     * Soft alternating row background
     * Responsive scroll on mobile

5. **Map Placeholder (Optional for Future Use)**

   * Insert a modular component that can later render a map
   * Clean grey canvas with text “Map coming soon…”

---

## **4. Component Architecture Requirements**

### Use the following structure (React example, but agent can adapt):

```
/src
  /components
    ChatContainer.jsx
    MessageBubble.jsx
    MessageInput.jsx
    DataTable.jsx
    TopBar.jsx
    LoadingIndicator.jsx
  /layouts
    MainLayout.jsx
  /styles
    globals.css
    variables.css
```

### Guiding Principles

* Keep components small and single-purpose.
* Enforce strict separation of layout vs. components.
* Styling should use:

  * CSS variables for theme colors,
  * Flexbox and grid layout patterns,
  * Consistent spacing scale (4px increment system).

---

## **5. Detailed Styling Instructions**

### **Typography**

* Base font: Inter, SF Pro, or Roboto
* Font sizes:

  * h1: 20–24px
  * body: 15–16px
  * caption: 13px

### **Spacing**

* Use a modular scale: 4px, 8px, 12px, 20px, 32px
* Vertical rhythm must be consistent across chat messages.

### **Color Tokens**

```
--color-bg: #ffffff;
--color-surface: #f7f7f7;
--color-border: #e5e5e5;
--color-text: #1e1e1e;
--color-text-secondary: #6b7280;
--color-primary: #3b82f6;  /* muted blue */
```

### **Chat Bubble Style**

Agent bubble:

* Background: var(--color-surface)
* Border: 1px solid var(--color-border)
* Text-left

User bubble:

* Background: var(--color-primary) with 90% opacity
* Text-right
* White text

### **Buttons**

* Border-radius: 6px
* No heavy shadows
* Hover state: subtle darkening
* Icon-based send button

---

## **6. UX Rules**

1. Messages should animate in with a *10–20ms fade & slide up*.
2. The input bar must never jump or resize unexpectedly.
3. Tables auto-expand vertically but stay scrollable horizontally.
4. The layout must avoid floating elements or overlapping containers.
5. The app must work beautifully on mobile.

---

## **7. Deliverables from the AI Agent**

The agent must generate:

### **A. Complete Frontend Code**

* React, Next.js, Vue, or plain HTML/CSS/JS depending on your preference.
* Fully styled components.
* Modular structure.
* Sample mock data responses.

### **B. Example UI States**

* Empty state (new user)
* Chat with multiple messages
* Loading state
* Data table response state
* Error state (e.g., invalid question)

### **C. Documentation**

Short explanation for:

* Component structure
* Styling system
* How to replace mock API with real backend endpoints

---

## **8. Strict Requirements**

The agent must not:

* Add backend logic
* Add advertising, branding fluff, cartoons
* Use bright colors or gradients
* Add unnecessary animations
* Ignore accessibility

The agent must:

* Keep the UI minimal, Scandinavian, and extremely clean.
* Follow the design tokens and typography specified.
* Make everything production-quality and easy to extend.

