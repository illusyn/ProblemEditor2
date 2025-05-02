# Math Editor Directory Structure

```
math_editor/
│
├── config_loader.py               # Configuration loading utilities
├── db_interface.py                # Database interface abstraction
├── editor.py                      # Core editor functionality
├── markdown_parser.py             # Markdown parsing utilities
├── math_editor.py                 # Main application entry point
│
├── core/                          # Core functionality
│   ├── __init__.py
│   └── preview_manager.py         # Preview management
│
├── ui/                            # User interface components
│   ├── __init__.py
│   ├── category_panel.py          # Category selection panel
│   ├── menu_manager.py            # Application menu management
│   │
│   └── dialogs/                   # Dialog components
│       ├── __init__.py
│       └── preferences_dialog.py  # User preferences interface
│
├── db/                            # Data handling and persistence
│   ├── __init__.py
│   ├── math_db.py                 # Math content database
│   └── math_image_db.py           # Math image storage
│
├── preview/                       # Preview functionality
│   ├── __init__.py
│   ├── latex_compiler.py          # LaTeX compilation
│   └── pdf_viewer.py              # PDF viewing component
│
├── converters/                    # Format conversion utilities
│   ├── __init__.py
│   └── image_converter.py         # Image conversion utilities
│
├── managers/                      # State and resource management
│   ├── __init__.py
│   ├── config_manager.py          # Configuration management
│   ├── file_manager.py            # File operations coordination
│   ├── image_manager.py           # Image resource management
│   └── template_manager.py        # Template management
│
├── docs/                          # Documentation
│   ├── architecture/              # Architecture documentation
│   │   └── project_structure.md   # Project structure documentation
│   │
│   └── guidelines/                # Development guidelines
│       └── code_spec.md           # Code Implementation Specification
│
├── .editorconfig                  # Editor configuration
├── README.md                      # Project overview
└── requirements.txt               # Dependencies
```

Each directory contains modules that adhere to the single responsibility principle, with clear separation of concerns and logical organization according to the Code Implementation Specification Framework.
