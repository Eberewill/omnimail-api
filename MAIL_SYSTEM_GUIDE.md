# 📧 Understanding the Global Mailing System

Building a mail system like **OmniMail** requires understanding how emails actually move across the internet. This guide breaks down the core concepts and how our architecture works.

---

## 1. The Three Main Protocols

Think of email like physical mail. You need a way to **send** it, a way for the post office to **receive/sort** it, and a way for you to **collect** it.

### **A. SMTP (Simple Mail Transfer Protocol)**
*   **Purpose:** Sending & Receiving between servers.
*   **The Analogy:** The mail truck and the sorting office.
*   **How it works:** When you send an email, your server (the client) talks to the recipient's server (the listener) over **Port 25** (or 587/465). They use a series of commands like `HELO`, `MAIL FROM`, and `RCPT TO` to agree on who is sending what.
*   **In OmniMail:** We built a custom **SMTP Receiver** using `aiosmtpd`. It acts as the "sorting office" that listens for these trucks and saves the mail to our database.

### **B. IMAP (Internet Message Access Protocol)**
*   **Purpose:** Accessing mail on a server from a device.
*   **Key Feature:** Syncing. If you delete an email on your phone, it disappears from your laptop too. The mail stays on the server.
*   **In OmniMail:** We are bypassing traditional IMAP and using a **REST API** instead. This is much easier for developers to integrate into web apps.

### **C. POP3 (Post Office Protocol v3)**
*   **Purpose:** Downloading mail to a device.
*   **Key Feature:** Once you download it, it's usually deleted from the server. It's an older method and rarely used now.

---

## 2. How OmniMail Works Under the Hood

Our system is designed to be **programmatic**. Traditional mail servers (like Postfix or Exim) are hard to control with code. OmniMail is "Code-First."

### **The Lifecycle of an Email in OmniMail:**

1.  **Ingress (The Arrival):**
    A server somewhere in the world wants to send an email to `user@your-domain.com`. It connects to our **SMTP Handler** (`app/services/smtp_handler.py`).

2.  **Validation:**
    Our handler looks at the `RCPT TO` (recipient). It queries our **PostgreSQL database** to see: *"Do we have a mailbox registered for this address?"*

3.  **Persistence:**
    If the mailbox exists, we parse the raw email data (subject, body, sender) and save it as a new row in the `emails` table.

4.  **The Webhook (Real-time Trigger):**
    Instead of making you check the database every second, OmniMail immediately fires a **Webhook**. It sends a `POST` request to your pre-configured URL with the email details. 

5.  **Access:**
    You can then use the **REST API** (`GET /mailboxes/{id}/messages`) to show that email in your own dashboard.

---

## 3. Why this is a "Senior" Project

*   **Asynchronous I/O:** We use `asyncio` so the server can handle hundreds of emails arriving at the same time without slowing down.
*   **Database Design:** Using **Foreign Keys** to link emails to specific mailboxes ensures that User A can never see User B's mail.
*   **Decoupling:** By using Webhooks, we decouple the "receiving" part of the system from the "displaying" part.

---

## 4. Key Terms for Your Resume

When talking about this project in interviews, use these keywords:
*   **"Custom SMTP Ingress"**: You didn't just use a library; you handled the raw mail protocol.
*   **"Multi-tenant Architecture"**: The system handles many users/mailboxes on one server.
*   **"Real-time Webhook Dispatcher"**: You implemented event-driven architecture.
*   **"Protocol Parsing"**: You processed raw MIME email data into structured JSON.

🦾 **Built by Williams & Agpana**
