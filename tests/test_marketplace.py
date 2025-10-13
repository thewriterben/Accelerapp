"""
Tests for template marketplace.
"""

import pytest
import tempfile
from pathlib import Path
from accelerapp.marketplace import (
    TemplateRegistry,
    TemplateMetadata,
    TemplatePackage,
    TemplateSearch,
)


def test_marketplace_imports():
    """Test marketplace imports."""
    assert TemplateRegistry is not None
    assert TemplateMetadata is not None
    assert TemplatePackage is not None
    assert TemplateSearch is not None


def test_template_metadata_creation():
    """Test template metadata creation."""
    metadata = TemplateMetadata(
        id='test-template',
        name='Test Template',
        description='A test template',
        author='Test Author',
        version='1.0.0',
        category='embedded',
        tags=['arduino', 'led'],
        platforms=['arduino', 'esp32']
    )
    
    assert metadata.id == 'test-template'
    assert metadata.name == 'Test Template'
    assert len(metadata.tags) == 2


def test_template_metadata_to_dict():
    """Test metadata serialization."""
    metadata = TemplateMetadata(
        id='test',
        name='Test',
        description='Test',
        author='Author',
        version='1.0',
        category='test'
    )
    
    data = metadata.to_dict()
    assert isinstance(data, dict)
    assert data['id'] == 'test'
    assert data['name'] == 'Test'


def test_template_metadata_from_dict():
    """Test metadata deserialization."""
    data = {
        'id': 'test',
        'name': 'Test',
        'description': 'Test',
        'author': 'Author',
        'version': '1.0',
        'category': 'test',
        'tags': [],
        'platforms': [],
        'rating': 0.0,
        'downloads': 0,
        'created_at': '',
        'updated_at': '',
        'license': 'MIT',
        'dependencies': []
    }
    
    metadata = TemplateMetadata.from_dict(data)
    assert metadata.id == 'test'
    assert metadata.name == 'Test'


def test_template_package_creation():
    """Test template package creation."""
    metadata = TemplateMetadata(
        id='test',
        name='Test',
        description='Test',
        author='Author',
        version='1.0',
        category='test'
    )
    
    package = TemplatePackage(metadata)
    assert package.metadata == metadata
    assert len(package.files) == 0


def test_template_package_add_file():
    """Test adding files to package."""
    metadata = TemplateMetadata(
        id='test',
        name='Test',
        description='Test',
        author='Author',
        version='1.0',
        category='test'
    )
    
    package = TemplatePackage(metadata)
    package.add_file('main.cpp', 'int main() {}')
    
    assert len(package.files) == 1
    assert package.get_file('main.cpp') == 'int main() {}'


def test_template_package_save_load():
    """Test saving and loading packages."""
    metadata = TemplateMetadata(
        id='test',
        name='Test',
        description='Test',
        author='Author',
        version='1.0',
        category='test'
    )
    
    package = TemplatePackage(metadata)
    package.add_file('main.cpp', 'int main() {}')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir) / 'package'
        package.save_to_directory(save_dir)
        
        loaded_package = TemplatePackage.load_from_directory(save_dir)
        
        assert loaded_package.metadata.id == 'test'
        assert loaded_package.get_file('main.cpp') == 'int main() {}'


def test_template_registry_initialization():
    """Test registry initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        assert len(registry.templates) == 0


def test_template_registry_register():
    """Test template registration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        
        metadata = TemplateMetadata(
            id='test',
            name='Test',
            description='Test',
            author='Author',
            version='1.0',
            category='test'
        )
        package = TemplatePackage(metadata)
        
        assert registry.register_template(package) is True
        assert len(registry.templates) == 1


def test_template_registry_get_template():
    """Test retrieving template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        
        metadata = TemplateMetadata(
            id='test',
            name='Test',
            description='Test',
            author='Author',
            version='1.0',
            category='test'
        )
        package = TemplatePackage(metadata)
        package.add_file('test.cpp', 'code')
        
        registry.register_template(package)
        
        retrieved = registry.get_template('test')
        assert retrieved is not None
        assert retrieved.metadata.id == 'test'
        assert retrieved.get_file('test.cpp') == 'code'


def test_template_registry_delete():
    """Test template deletion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        
        metadata = TemplateMetadata(
            id='test',
            name='Test',
            description='Test',
            author='Author',
            version='1.0',
            category='test'
        )
        package = TemplatePackage(metadata)
        
        registry.register_template(package)
        assert registry.delete_template('test') is True
        assert len(registry.templates) == 0


def test_template_registry_list():
    """Test listing templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        
        for i in range(3):
            metadata = TemplateMetadata(
                id=f'test{i}',
                name=f'Test {i}',
                description='Test',
                author='Author',
                version='1.0',
                category='embedded' if i % 2 == 0 else 'web'
            )
            registry.register_template(TemplatePackage(metadata))
        
        all_templates = registry.list_templates()
        assert len(all_templates) == 3
        
        embedded_templates = registry.list_templates(category='embedded')
        assert len(embedded_templates) == 2


def test_template_search():
    """Test template search."""
    templates = [
        TemplateMetadata(
            id='arduino-led',
            name='Arduino LED',
            description='LED controller',
            author='Author',
            version='1.0',
            category='embedded',
            tags=['arduino', 'led'],
            platforms=['arduino'],
            rating=4.5,
            downloads=100
        ),
        TemplateMetadata(
            id='esp32-wifi',
            name='ESP32 WiFi',
            description='WiFi setup',
            author='Author',
            version='1.0',
            category='embedded',
            tags=['esp32', 'wifi'],
            platforms=['esp32'],
            rating=4.8,
            downloads=200
        ),
    ]
    
    search = TemplateSearch(templates)
    
    # Search by query
    results = search.search(query='LED')
    assert len(results) == 1
    assert results[0].id == 'arduino-led'
    
    # Filter by platform
    results = search.search(platform='esp32')
    assert len(results) == 1
    
    # Filter by category
    results = search.search(category='embedded')
    assert len(results) == 2
    
    # Sort by rating
    results = search.search(sort_by='rating')
    assert results[0].id == 'esp32-wifi'


def test_template_search_popular():
    """Test getting popular templates."""
    templates = [
        TemplateMetadata(
            id=f'template{i}',
            name=f'Template {i}',
            description='Test',
            author='Author',
            version='1.0',
            category='test',
            downloads=i * 10
        )
        for i in range(5)
    ]
    
    search = TemplateSearch(templates)
    popular = search.get_popular(limit=3)
    
    assert len(popular) == 3
    assert popular[0].downloads > popular[1].downloads


def test_template_search_top_rated():
    """Test getting top rated templates."""
    templates = [
        TemplateMetadata(
            id=f'template{i}',
            name=f'Template {i}',
            description='Test',
            author='Author',
            version='1.0',
            category='test',
            rating=float(i)
        )
        for i in range(5)
    ]
    
    search = TemplateSearch(templates)
    top_rated = search.get_top_rated(limit=3)
    
    assert len(top_rated) == 3
    assert top_rated[0].rating > top_rated[1].rating
