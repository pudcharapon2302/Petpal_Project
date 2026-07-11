# PetPal AI

A centralized platform for lost pet recovery and adoption, built to connect pet owners, adopters, and verified animal welfare organizations in one place — backed by an AI assistant that actually understands the data behind it.

## About

Losing a pet or trying to find one that needs a home usually means digging through scattered Facebook posts, shelter pages, and community groups. PetPal AI brings that into a single platform, and adds an AI layer on top so users can ask natural questions about listings and organizations instead of manually searching.

## Features

- **Pet Listings** — post and browse lost pets and adoptable pets in one place
- **Verified Organization Directory** — a vetted list of animal welfare organizations, so users know which sources to trust
- **AI Assistant (RAG)** — a chat-based assistant that answers questions about listings and organizations using real platform data, not just generic responses
- **Image-Based Matching** — upload a pet photo and let the system analyze visual features to help match lost pets with sightings or similar listings

## Tech Stack

**Backend**
- Django
- MySQL

**Frontend**
- TailwindCSS

**AI / ML**
- LangChain (RAG pipeline)
- ChromaDB (vector store)
- Gemini Multimodal API (image feature extraction)

## How the AI Assistant Works

The assistant uses Retrieval-Augmented Generation instead of relying purely on a language model's built-in knowledge:

1. Listings and organization data are embedded and stored in ChromaDB
2. When a user asks a question, relevant records are retrieved based on similarity
3. LangChain passes that context to the language model to generate a grounded, accurate response

This keeps answers tied to actual platform data — current listings, real organizations — rather than generic or outdated information.

## Image Matching

Pet photos are processed through the Gemini Multimodal API to extract visual features (breed characteristics, coloring, markings). These features feed into the search and matching logic, making it easier to connect a lost pet report with a sighting, even when descriptions alone wouldn't be enough.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/pudcharapon2302/Petpal_Project.git
cd Petpal_Project

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see .env.example)
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | MySQL connection string |
| `GEMINI_API_KEY` | API key for Gemini Multimodal API |
| `SECRET_KEY` | Django secret key |

## Project Structure

```
Petpal_Project/
├── manage.py
├── petpal/          # Django project settings
├── apps/             # Django apps (listings, organizations, chat, etc.)
├── static/            # TailwindCSS assets
├── templates/
└── requirements.txt
```

## Author

**Pudcharapon Yindiram**
Data Science and Software Innovation, Ubon Ratchathani University
mr.golf0900@gmail.com
