TEST_CASES = [
    # ── 10 Real Product Prompts ──────────────────────────────────────
    {
        "id": "real_01",
        "type": "real",
        "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    },
    {
        "id": "real_02",
        "type": "real",
        "prompt": "Create an e-commerce store with product listings, shopping cart, checkout with Stripe payments, order tracking, and admin panel to manage inventory."
    },
    {
        "id": "real_03",
        "type": "real",
        "prompt": "Build a project management tool like Trello with boards, lists, cards, due dates, team members, and notifications."
    },
    {
        "id": "real_04",
        "type": "real",
        "prompt": "Create a doctor appointment booking system with patient login, doctor profiles, available slots, booking, and email reminders."
    },
    {
        "id": "real_05",
        "type": "real",
        "prompt": "Build a learning management system with courses, video lessons, quizzes, student progress tracking, and instructor dashboard."
    },
    {
        "id": "real_06",
        "type": "real",
        "prompt": "Create a multi-tenant SaaS invoicing app where businesses can create invoices, track payments, manage clients, and export PDF reports."
    },
    {
        "id": "real_07",
        "type": "real",
        "prompt": "Build a food delivery app with restaurant listings, menu, cart, order placement, delivery tracking, and driver management."
    },
    {
        "id": "real_08",
        "type": "real",
        "prompt": "Create a HR management system with employee profiles, leave requests, payroll, attendance tracking, and manager approvals."
    },
    {
        "id": "real_09",
        "type": "real",
        "prompt": "Build a social media platform with user profiles, posts, likes, comments, follow system, and a news feed."
    },
    {
        "id": "real_10",
        "type": "real",
        "prompt": "Create a real estate listing platform where agents can post properties, buyers can search and filter, and schedule viewings."
    },

    # ── 10 Edge Cases ────────────────────────────────────────────────
    {
        "id": "edge_01",
        "type": "edge",
        "category": "vague",
        "prompt": "Build me an app."
    },
    {
        "id": "edge_02",
        "type": "edge",
        "category": "vague",
        "prompt": "I need a website for my business."
    },
    {
        "id": "edge_03",
        "type": "edge",
        "category": "conflicting",
        "prompt": "Build an app that is completely free but also has paid premium features. All users should be admins but also have restricted access."
    },
    {
        "id": "edge_04",
        "type": "edge",
        "category": "conflicting",
        "prompt": "Create a private app that is also fully public. Users should not need to login but all data must be private and secure."
    },
    {
        "id": "edge_05",
        "type": "edge",
        "category": "incomplete",
        "prompt": "Build a booking system with payments."
    },
    {
        "id": "edge_06",
        "type": "edge",
        "category": "incomplete",
        "prompt": "Create a dashboard with analytics."
    },
    {
        "id": "edge_07",
        "type": "edge",
        "category": "overloaded",
        "prompt": "Build an app with login, payments, chat, video calls, AI recommendations, blockchain wallet, social feed, marketplace, CRM, ERP, inventory, HR, payroll, analytics, and mobile support all in one."
    },
    {
        "id": "edge_08",
        "type": "edge",
        "category": "overloaded",
        "prompt": "Create a platform that does everything Airbnb, Uber, Amazon, Slack, and Salesforce do combined."
    },
    {
        "id": "edge_09",
        "type": "edge",
        "category": "ambiguous",
        "prompt": "Build something for managing things with users and some kind of payment."
    },
    {
        "id": "edge_10",
        "type": "edge",
        "category": "ambiguous",
        "prompt": "Make an app for my team."
    },
]