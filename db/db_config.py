"""
Database configuration module for managing database paths based on version.
"""

from pathlib import Path
from typing import Tuple

class DatabaseConfig:
    """Manages database paths for different database versions."""
    
    def __init__(self, db_version: str = "main"):
        """
        Initialize database configuration.
        
        Args:
            db_version: Database version identifier (e.g., "main", "secondary", etc.)
        """
        self.db_version = db_version
        
    def get_database_paths(self) -> Tuple[Path, Path]:
        """
        Get the paths for both databases based on the version.
        
        Returns:
            Tuple of (problems_db_path, images_db_path)
        """
        if self.db_version == "main":
            # Default main database - keep in original location for backward compatibility
            base_dir = Path("db")
            problems_db = base_dir / "math_problems.db"
            images_db = base_dir / "math_images.db"
        else:
            # Version-specific database - parallel to main db directory
            version_dir = Path(f"db_{self.db_version}")
            version_dir.mkdir(parents=True, exist_ok=True)
            problems_db = version_dir / "math_problems.db"
            images_db = version_dir / "math_images.db"
            
        return problems_db, images_db
    
    def ensure_directories(self):
        """Ensure all necessary directories exist."""
        problems_db, images_db = self.get_database_paths()
        problems_db.parent.mkdir(parents=True, exist_ok=True)
        images_db.parent.mkdir(parents=True, exist_ok=True)