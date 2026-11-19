
# PROJECT ARCHITECTURE

## 1. Project Overview

**Project Name:** [Data_Fix]

**Description:** [Data fix autonomous data quality and repair engine is our project for today's hackathon so we must build a user friendly, impressive creative app which accepts info from user for exam if is college database so student name registration number age phone number and if any other organisations so their info ,soo how much the app be , car speedometer boosters inspired animation and whole.... Opening animation to upcoming windows interfaces for user after e selects desires options in app such as enter data , displaying data purity quality ect , download option with option of only his class or department or whole clg for example.... So yeaaa firstly analysing this create many pictures showing one after another of how user wud experience pictorially and keep the colours combination of black blue yellow red since even speedometer inspired it is]

## 2. Technology Stack

### Frontend
- Framework: React
- Language: JavaScript
- Styling: Tailwind CSS
- State Management: Context API

### Backend
- Runtime: Node.js
- Framework: Express.js
- Language: JavaScript

### Database
- Database: MongoDB
- ORM/ODM: Mongoose

### Tools
- Version Control: Git & GitHub
- Code Editor: VS Code

## 3. Project Folder Structure

Data_Fix/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── assets/
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   │   └── ai/
│   │   ├── middleware/
│   │   ├── models/
│   │   └── config/
│   └── package.json
│
├── database/
│   ├── schema/
│   └── migrations/
│
├── AI_INSTRUCTIONS.md
├── PROJECT_ARCHITECTURE.md
├── API_CONTRACTS.md
├── .env.example
├── .gitignore
└── README.md
Update this structure to match the actual repository. Do not create folders just because they appear in this example.

## 4. Architecture Explanation

### Frontend
Describe the frontend structure and responsibilities.

### Backend
Describe the backend structure and responsibilities.

### Database
Describe database tables, relationships and responsibilities.

## 5. Application Workflow

Explain how data moves through the application:

User → Frontend → API → Backend → Database → Backend → Frontend → User

## 6. Environment Configuration

List required environment variables and their purpose.

Never include actual passwords, API keys or secrets.

## 7. Development Commands

Document the verified commands required to install, run, test and build the application.

## 8. Important Development Rules

- Follow AI_INSTRUCTIONS.md.
- Follow the agreed API contracts.
- Keep the architecture consistent.
- Update this document whenever the architecture changes.

## 9. AI Architecture

AI Provider: [Provider Name]
AI Model: [Model Name]

AI Integration Location:
backend/services/ai/

Responsibilities:
- Process AI requests.
- Manage communication with the AI provider.
- Handle AI responses.
- Handle provider errors.
- Keep API credentials secure.

Environment Variables:
- AI_PROVIDER
- AI_MODEL
- AI_API_KEY

Security:
AI API credentials must never be exposed
to the frontend.