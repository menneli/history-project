```markdown
# Historical Events of the 20th Century

An interactive timeline exploring 20th-century historical events and their associated musical compositions. Built as an educational archive connecting history with cultural heritage.

## Features

- **Interactive Timeline**: Navigate through decades of historical events with smooth animations
- **Event-Music Connections**: Click on any event to discover related musical compositions
- **Search Functionality**: Quickly find specific events across the timeline
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Accessibility**: High contrast ratios and readable typography (Merriweather font)

##  Tech Stack

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy, Pydantic Settings
- **Frontend**: HTML5, CSS3 (custom properties), Vanilla JavaScript
- **Templating**: Jinja2 (server-side rendering)
- **Database**: SQLite with persistent volume (Railway)
- **Deployment**: Railway with CORS-enabled REST API
## Design System

### Color Palette
- **Primary**: `#0056b3`
- **Background**: `#f8f9fa`
- **Text**: `#222`

### Typography
- **Font Family**: Merriweather (serif)
- **Weights**: 400 (Regular), 700 (Bold)
- **Rationale**: Chosen for screen readability and scholarly appearance

##  Project Structure
├── database/
│ ├── init.py
│ ├── db.py # Database initialization
│ └── setup.py # Database setup and migrations
│
├── models/
│ ├── init.py
│ ├── connection.py # Database connection handling
│ ├── events.py # Event model/schema
│ └── songs.py # Song model/schema
│
├── services/
│ ├── init.py
│ ├── importer.py # Data import utilities
│ └── parser.py # Data parsing logic
│
├── static/
│ └── style.css # All CSS styling
│
├── templates/
│ ├── base.html # Base template with common layout
│ ├── event.html # Event detail page
│ ├── song.html # Song detail page
│ └── timeline.html # Main timeline view
│
├── .env # Environment variables
├── .gitattributes
├── app.py # FastAPI application instance
├── config.py # Configuration settings
├── main.py # Application entry point
├── LICENSE
└── README.md
```

##  Usage

1. **Browse Events**: Scroll through the timeline to explore historical events organized by decade
2. **Search**: Use the search bar to find specific events quickly
3. **Discover Music**: Click on any event card to view related musical compositions
4. **Navigate**: Use the decade markers to jump to specific time periods

##  Contributing

Contributions are welcome! If you'd like to add:
- Additional historical events
- More musical compositions
- Accessibility improvements
- Translation support

Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [License](LICENSE) file for full terms.


##  Author

Built by menneli - Solo full-stack development from concept to deployment.

##  Acknowledgments

- Historical data sourced from (mostly) Wikipedia
- Musical compositions curated from (also) Wikipedia
- Inspired by the intersection of history and cultural heritage

---
**Last Updated**: 30.04.2026
3. **Live Demo**: https://history-project-production.up.railway.app
