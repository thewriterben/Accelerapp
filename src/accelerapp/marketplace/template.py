"""
Template metadata and package structures.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class TemplateMetadata:
    """
    Metadata for a code template.
    """
    id: str
    name: str
    description: str
    author: str
    version: str
    category: str
    tags: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    rating: float = 0.0
    downloads: int = 0
    created_at: str = ""
    updated_at: str = ""
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'version': self.version,
            'category': self.category,
            'tags': self.tags,
            'platforms': self.platforms,
            'rating': self.rating,
            'downloads': self.downloads,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'license': self.license,
            'dependencies': self.dependencies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create from dictionary."""
        return cls(**data)


class TemplatePackage:
    """
    Complete template package with files and metadata.
    """
    
    def __init__(
        self,
        metadata: TemplateMetadata,
        files: Optional[Dict[str, str]] = None
    ):
        """
        Initialize template package.
        
        Args:
            metadata: Template metadata
            files: Dictionary of filename -> content
        """
        self.metadata = metadata
        self.files = files or {}
    
    def add_file(self, filename: str, content: str):
        """
        Add a file to the package.
        
        Args:
            filename: Name of the file
            content: File content
        """
        self.files[filename] = content
    
    def get_file(self, filename: str) -> Optional[str]:
        """
        Get file content.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content or None
        """
        return self.files.get(filename)
    
    def list_files(self) -> List[str]:
        """Get list of all files."""
        return list(self.files.keys())
    
    def save_to_directory(self, directory: Path):
        """
        Save package to directory.
        
        Args:
            directory: Target directory
        """
        directory.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata_path = directory / 'template.json'
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
        
        # Save files
        files_dir = directory / 'files'
        files_dir.mkdir(exist_ok=True)
        
        for filename, content in self.files.items():
            file_path = files_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
    
    @classmethod
    def load_from_directory(cls, directory: Path) -> 'TemplatePackage':
        """
        Load package from directory.
        
        Args:
            directory: Source directory
            
        Returns:
            TemplatePackage instance
        """
        # Load metadata
        metadata_path = directory / 'template.json'
        with open(metadata_path, 'r') as f:
            metadata_dict = json.load(f)
        
        metadata = TemplateMetadata.from_dict(metadata_dict)
        
        # Load files
        files = {}
        files_dir = directory / 'files'
        if files_dir.exists():
            for file_path in files_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(files_dir)
                    files[str(relative_path)] = file_path.read_text()
        
        return cls(metadata, files)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert package to dictionary."""
        return {
            'metadata': self.metadata.to_dict(),
            'files': self.files,
        }
