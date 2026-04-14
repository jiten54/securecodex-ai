# 🛡️ SecureCodeX
<img width="1917" height="868" alt="Screenshot 2026-04-14 123633" src="https://github.com/user-attachments/assets/71dd091d-9a6c-4f51-9224-0f5706aa6633" />
<img width="1916" height="878" alt="Screenshot 2026-04-14 123525" src="https://github.com/user-attachments/assets/d9f102c3-b4b8-4116-b728-267df7f86956" />
<img width="1918" height="870" alt="Screenshot 2026-04-14 123432" src="https://github.com/user-attachments/assets/c0a71d95-a745-4948-b4e5-43e5e163f8af" />
<img width="1917" height="882" alt="Screenshot 2026-04-14 123228" src="https://github.com/user-attachments/assets/8ee16459-b351-401c-87cf-32947806c6f0" />
<img width="1904" height="981" alt="Screenshot 2026-04-14 123812" src="https://github.com/user-attachments/assets/45c7afa5-9e7c-41b1-bdf6-7ecf4c91f15f" />

### AI-Powered Code Obfuscation & Protection Platform

SecureCodeX is a **production-grade SaaS application** designed to protect source code from reverse engineering using advanced obfuscation techniques and AI-driven security analysis.

Built with a **full-stack architecture**, SecureCodeX enables developers to securely upload, analyze, and obfuscate code while maintaining performance and scalability.

---

## 🚀 Live Features

* 🔐 **Secure Authentication**

  * JWT-based login system
  * API Key authentication (`X-API-Key`) for SaaS usage

* 📂 **Code Upload & Processing**

  * Upload `.py` and `.js` files
  * Asynchronous processing pipeline
  * Real-time job status tracking

* 🧠 **AI-Powered Code Analysis**

  * Detects:

    * API keys
    * Hardcoded secrets
    * Sensitive logic
  * Suggests optimal obfuscation strategies
  * Optional deep analysis using Gemini AI

* 🔄 **Advanced Obfuscation Engine**

  * Variable renaming
  * String encoding
  * Dead code injection
  * Control flow modification

* 🔑 **API Key Management**

  * Generate secure API keys (`scx_...`)
  * Integrate with CI/CD pipelines
  * Automate code protection workflows

* ⚙️ **Production-Ready Backend**

  * Logging system
  * Global error handling
  * Rate limiting (anti-abuse)
  * Secure file storage (UUID-based)

---

## 🛠️ Tech Stack

### Frontend

* React (Vite)
* Tailwind CSS
* Framer Motion
* Axios
* Lucide Icons

### Backend

* Node.js (Express)
* JWT Authentication
* Bcrypt
* Multer (File Uploads)

### AI Integration

* Google Gemini API (`@google/genai`)

---

## 🧱 System Architecture

Client (React UI)
↓
API Layer (Express Backend)
↓
Authentication (JWT / API Key)
↓
Processing Engine (Async Jobs)
↓
Obfuscation Engine + AI Module
↓
Storage (Local / Cloud Ready)

---

## 📖 How It Works

1. **Sign Up / Login**
2. **Upload Code File** (`.py` / `.js`)
3. **Select Obfuscation Level**
4. **Process Code (Async Job)**
5. **Download Protected Code**
6. *(Optional)* Analyze code using AI before obfuscation

---

## 📂 Project Structure

```bash
securecodex/
│
├── frontend/        # React UI
├── backend/         # Express API
├── services/        # AI + Obfuscation logic
├── uploads/         # Uploaded files
├── processed/       # Obfuscated output
```

---

## ⚡ Key Highlights

* Designed using **clean architecture principles**
* Implements **real-world SaaS patterns**
* Combines **Backend + AI + Security + UI**
* Scalable and extensible for production deployment

---

## 🔐 API Usage Example

```bash
curl -H "X-API-Key: YOUR_KEY" \
https://api.securecodex.com/v1/files/upload
```

---


---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/your-username/securecodex.git
cd securecodex
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Application

```bash
npm run dev
```

---

## 🧠 Future Improvements

* Docker & cloud deployment (AWS / Render)
* Multi-language obfuscation support
* Advanced AST transformations
* Role-based access control (RBAC)
* WebSocket-based real-time updates

---


## 🤝 Contributing

Contributions are welcome. Please open an issue or submit a pull request.

---

## 📧 Contact

* LinkedIn: https://www.linkedin.com/in/jiten-moni-das-01b3a032b
* GitHub: https://github.com/jiten54

---

## ⭐ If you found this useful

Give it a ⭐ on GitHub and support the project!
