# OmniMail API 🦾
**An Open-Source, High-Performance Mail Engine for Developers**

OmniMail API is a production-grade, multi-tenant email management system. It allows developers to programmatically create mailboxes, receive incoming emails via SMTP, and access them through a modern REST API. Designed with a "developer-first" philosophy, it's the perfect solution for building transactional email platforms, disposable email services, or custom CRM integrations.

---

## 🏗 High-Level Architecture

OmniMail is built on a distributed, asynchronous architecture to ensure reliability and low latency.

*   **REST Interface:** Built with **FastAPI** (Python 3.12+), providing sub-second response times and automated OpenAPI documentation.
*   **SMTP Ingress:** Uses **aiosmtpd** to listen for incoming mail directly on the wire, bypassing traditional, heavy mail servers.
*   **Persistence Layer:** **PostgreSQL** (compatible with Supabase/Neon) stores metadata, user accounts, and mailbox configurations.
*   **Storage:** Large email bodies and attachments are abstracted to be stored in **S3-compatible storage** (MinIO/AWS S3) or locally on disk.
*   **Security:** Multi-layer protection including **API Key-based authentication** and rate limiting.

---

## 🚀 Key Features

*   **Programmatic Mailboxes:** Create, update, and rotate mailboxes in real-time via API.
*   **Event-Driven Ingress:** Real-time processing of incoming SMTP traffic.
*   **Clean API:** Access your inbox, search through messages, and handle attachments with simple JSON endpoints.
*   **Containerized:** One-command deployment using Docker and Docker Compose.
*   **Naija Edge:** Pre-configured to run on low-power hardware (like your TV box!) making it truly free to host.

---

## 🛠 Tech Stack

*   **Core:** Python 3.12
*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **SMTP Handler:** aiosmtpd
*   **Validation:** Pydantic v2
*   **Deployment:** Docker / Docker Compose

---

## 📋 Roadmap

- [ ] Core REST API for user registration and API key generation.
- [ ] SMTP Ingress handler for receiving raw email data.
- [ ] Database schema for multi-tenant mailbox isolation.
- [ ] Support for file attachments via S3 storage.
- [ ] Webhook triggers for new incoming mail.

---

**Developed with 🦾 by Agpana & Williams**
