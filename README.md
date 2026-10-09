# 🌿 GrassMate — Your AI-Powered Outdoor Companion

**Turn your free time into a simple outdoor mission.**

GrassMate is an AI-powered outdoor companion that transforms your available time, preferred activity, interests, and mission style into a personalized outdoor experience. It helps you plan an outing, discover relevant trail records, and then encourages you to put your phone away and enjoy the outdoors.

[![View Repository](https://img.shields.io/badge/GitHub-View%20Repository-181717?logo=github)](https://github.com/Shubhamkumar-op/GrassMate)

## 📸 Screenshots

### 1. Choose Your Outdoor Mission

Select your available time, activity, interests, mission style, and optional location preferences.

![GrassMate application screenshot 1](screenshots/1.png)

### 2. Your Personalized Mission

GrassMate generates a mission with a warm-up, main activity, and cooldown.

![GrassMate application screenshot 2](screenshots/2.png)

### 3. Trail Recommendations and Details

Explore route records retrieved by GrassMate, including the available trail metadata.

![GrassMate application screenshot 3](screenshots/3.png)

[View all screenshots in the repository](https://github.com/Shubhamkumar-op/GrassMate/tree/main/screenshots)

## ✨ Features

- **Personalized missions:** Generate outdoor instructions based on activity, interest, available time, and preferred intensity.
- **Multiple activities:** Walking, hiking, running, cycling, exploring, and relaxing.
- **Interest-based challenges:** Nature, fitness, adventure, wildlife, photography, relaxation, and more.
- **Structured time plans:** Divide an outing into warm-up, main activity, and cooldown.
- **Semantic trail retrieval:** Retrieve relevant California State Parks route records using vector embeddings.
- **Location-aware search:** Search within a selected radius using manually entered coordinates.
- **Honest route information:** Display recorded segment length, listed activities, route type, and dataset category.
- **AI fallback:** Keep missions usable if the AI response cannot be parsed or generation fails.
- **Phone-away philosophy:** Read your mission, put your phone away, and go outside.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Interactive web interface |
| Ollama + Gemma 3 4B | Outdoor mission generation |
| Sentence Transformers | Text embeddings |
| BAAI/bge-base-en-v1.5 | Semantic embedding model |
| Tiger Cloud PostgreSQL | Database |
| pgvector | Vector similarity search |
| psycopg | PostgreSQL connectivity |
| python-dotenv | Environment configuration |

## 🏗️ How It Works

1. The user selects an activity, interest, mission style, and available time.
2. The application creates a search query from those preferences.
3. BGE generates an embedding for semantic retrieval.
4. PostgreSQL with pgvector retrieves relevant route records.
5. Gemma generates personalized instructions for the three mission phases.
6. Python controls the time allocation and assembles the final mission.
7. Streamlit displays the mission and retrieved route information.

## 📊 Data Source

GrassMate uses California State Parks recreational route data.

- [California State Parks GIS data](https://www.parks.ca.gov/?page_id=29682)
- [Recreational Routes dataset](https://lab.data.ca.gov/dataset/recreational_routes)

**Important data limitations**

- The dataset contains recorded route segments, not necessarily complete trails.
- Segment length must not be interpreted as the total length of a named trail.
- Route categories such as Class I, Class II, and Class III are recorded dataset values, not verified difficulty ratings.
- Recorded activity labels do not guarantee current access, conditions, or safety.
- Location search uses manually entered coordinates; the app does not automatically detect the user's location.
- The available dataset is geographically limited to California State Parks records.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- Git
- Ollama
- A PostgreSQL database hosted by Tiger Cloud or a compatible PostgreSQL provider
- A downloaded copy of the required route dataset

### 1. Clone the repository

```bash
git clone https://github.com/Shubhamkumar-op/GrassMate.git
cd GrassMate
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
DATABASE_HOST=your_database_host
DATABASE_PORT=your_database_port
DATABASE_NAME=tsdb
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
```

Use your actual database credentials locally. Never commit `.env` or publish database passwords.

### 5. Start Ollama and download the model

```powershell
ollama pull gemma3:4b
```

To verify the model works:

```powershell
ollama run gemma3:4b
```

Exit the model prompt when finished testing.

### 6. Prepare the database

Run the database schema and data-ingestion scripts included in the repository in their expected order. Ensure the route records and their 768-dimensional embeddings have been loaded before running the application.

### 7. Launch GrassMate

From the project root:

```powershell
python -m streamlit run app/streamlit_app.py
```

Open the local Streamlit URL displayed in your terminal.

## 🔐 Security

- Keep `.env` out of version control.
- Never expose database credentials in screenshots, logs, or public commits.
- Do not publish private connection strings.
- Keep database permissions limited to what the application needs.

Recommended `.gitignore` entries:

```gitignore
.venv/
__pycache__/
.env
*.pyc
```

## ⚠️ Limitations

- Trail coverage is limited to the included dataset.
- Search results depend on the available records and their metadata.
- AI-generated instructions can be imperfect and should be reviewed using common sense.
- Trail conditions, closures, permitted activities, facilities, and accessibility are not guaranteed by the dataset.
- Users should verify local conditions and follow posted rules before setting out.

## 🌱 Project Philosophy

GrassMate is designed to use technology to help people spend more time outside—not to keep them staring at a screen.

**Get your mission. Put your phone away. Touch grass.**

## 📄 License

Add your chosen open-source license before distributing the project. For example, include an MIT `LICENSE` file if you choose the MIT License.
