# ClinicManager Pro

A comprehensive clinic management system built with Python and Tkinter for Karachi Homoeo Clinic.

## Features

- **Patient Management**: Add, edit, and view patient profiles with detailed information.
- **Visit Tracking**: Record and manage patient visits, including history and today's appointments.
- **Dashboard**: Overview of today's visits and clinic statistics.
- **Earnings Reports**: Generate and view financial reports.
- **Data Export**: Export patient and visit data to CSV files.
- **Modern UI**: Clean, professional interface with light/dark theme support using sv-ttk.

## Requirements

- Python 3.6 or higher
- `sv-ttk` library for enhanced Tkinter theming

## Installation

1. **Clone the repository**:

   ```
   git clone https://github.com/Sanakh998/clinic-app.git
   cd clinic-app
   ```

2. **Install dependencies**:

   ```
   pip install sv-ttk
   ```

   Note: Tkinter is included with Python by default. If you encounter issues, ensure Python is installed with Tkinter support.

## Running the Application

To start the application, run the main script from the project root:

```
python main.py
```

This will launch the GUI application. The database (`clinic_data.db`) will be created automatically if it doesn't exist.

## Database

The application uses SQLite for data storage. The database file `clinic_data.db` is automatically created and is excluded from version control for privacy and security reasons.

## Project Structure

```
clinic-app/
├── main.py                 # Application entry point
├── config/
│   └── config.py           # Configuration constants and settings
├── database/
│   ├── __init__.py
│   └── database.py         # Database management and operations
├── forms/
│   ├── __init__.py
│   ├── patient_form.py     # Patient registration/editing form
│   └── visit_form.py       # Visit recording form
├── reports/
│   └── report_generator.py # Report generation utilities
├── ui/
│   ├── __init__.py
│   ├── app.py              # Main application window
│   ├── dashboard.py        # Dashboard view
│   ├── earnings_report.py  # Earnings report view
│   ├── patient_profile.py  # Patient profile view
│   ├── patients_list.py    # Patients list view
│   ├── sidebar.py          # Navigation sidebar
│   ├── styles.py           # UI styling
│   ├── table_factory.py    # Table creation utilities
│   ├── today_visits.py     # Today's visits view
│   ├── visit_cards.py      # Visit card components
│   └── visit_history.py    # Visit history view
├── utils/
│   ├── __init__.py
│   ├── center_window.py    # Window centering utility
│   ├── placeholder_entry.py # Placeholder text for entries
│   └── scrollable_frame.py # Scrollable frame widget
├── assets/                 # Static assets (if any)
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Usage

- **Dashboard**: View today's visits and clinic overview.
- **Patients**: Manage patient records.
- **Visits**: Record new visits and view history.
- **Reports**: Generate earnings and other reports.
- **Export**: Export data for external use.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details (if applicable).

## Support

For issues or questions, please open an issue on GitHub or contact the maintainer.

---

**ClinicManager Pro v1.1.0** - Developed for Karachi Homoeo Clinic
