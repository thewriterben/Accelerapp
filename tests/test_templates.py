"""
Tests for template system.
"""

import pytest
from pathlib import Path
import tempfile


def test_template_manager_import():
    """Test template manager can be imported."""
    from accelerapp.templates import TemplateManager
    assert TemplateManager is not None


def test_template_manager_initialization():
    """Test template manager initialization."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        assert manager.template_dir == template_dir


def test_template_manager_render_string():
    """Test rendering template string."""
    from accelerapp.templates import TemplateManager
    
    manager = TemplateManager()
    
    template = "Hello {{ name }}!"
    context = {'name': 'World'}
    
    result = manager.render_string(template, context)
    assert result == "Hello World!"


def test_template_manager_filters():
    """Test custom filters."""
    from accelerapp.templates import TemplateManager
    
    manager = TemplateManager()
    
    # Test upper_snake_case filter
    template = "{{ name | upper_snake_case }}"
    result = manager.render_string(template, {'name': 'my device'})
    assert result == "MY_DEVICE"
    
    # Test camel_case filter
    template = "{{ name | camel_case }}"
    result = manager.render_string(template, {'name': 'my_device'})
    assert result == "myDevice"
    
    # Test pascal_case filter
    template = "{{ name | pascal_case }}"
    result = manager.render_string(template, {'name': 'my_device'})
    assert result == "MyDevice"


def test_template_manager_create_template():
    """Test creating a template."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        content = "// Generated for {{ platform }}\n"
        manager.create_template('test.j2', content)
        
        assert manager.template_exists('test.j2')


def test_template_manager_render_template():
    """Test rendering a template file."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        # Create template
        content = "Device: {{ device_name }}\n"
        manager.create_template('device.j2', content)
        
        # Render template
        result = manager.render_template('device.j2', {'device_name': 'TestDevice'})
        assert 'TestDevice' in result


def test_template_manager_nonexistent_template():
    """Test rendering nonexistent template."""
    from accelerapp.templates import TemplateManager
    
    manager = TemplateManager()
    result = manager.render_template('nonexistent.j2', {})
    assert result == ""


def test_template_manager_list_templates():
    """Test listing templates."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        manager.create_template('test1.j2', 'content1')
        manager.create_template('test2.j2', 'content2')
        
        templates = manager.list_templates()
        assert 'test1.j2' in templates
        assert 'test2.j2' in templates


def test_template_manager_platform_specific():
    """Test platform-specific template generation."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        # Create platform-specific template
        (template_dir / 'arduino').mkdir()
        manager.create_template('arduino/main.j2', '// Arduino main for {{ device }}\n')
        
        result = manager.generate_from_platform(
            'arduino', 'cpp', 'main', {'device': 'Test'}
        )
        assert 'Arduino main for Test' in result


def test_template_manager_fallback():
    """Test template fallback mechanism."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        manager = TemplateManager(template_dir)
        
        # Create generic template
        (template_dir / 'generic').mkdir()
        manager.create_template('generic/config.j2', '// Generic config\n')
        
        # Request platform-specific, should fall back to generic
        result = manager.generate_from_platform(
            'arduino', 'cpp', 'config', {}
        )
        assert 'Generic config' in result


def test_template_manager_default_context():
    """Test default context variables."""
    from accelerapp.templates import TemplateManager
    
    manager = TemplateManager()
    defaults = manager.get_template_context_defaults()
    
    assert 'project_name' in defaults
    assert 'generated_by' in defaults
    assert 'version' in defaults


def test_template_manager_add_directory():
    """Test adding additional template directory."""
    from accelerapp.templates import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            template_dir1 = Path(tmpdir1)
            template_dir2 = Path(tmpdir2)
            
            manager = TemplateManager(template_dir1)
            
            # Create template in second directory
            (template_dir2 / 'extra.j2').write_text('Extra template')
            
            # Add second directory
            manager.add_template_directory(template_dir2)
            
            # Should be able to access template from second directory
            assert manager.template_exists('extra.j2')
