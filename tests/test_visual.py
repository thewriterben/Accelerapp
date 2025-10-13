"""
Tests for visual specification builder.
"""

import pytest
import tempfile
from pathlib import Path
from accelerapp.visual import (
    VisualSpecification,
    Component,
    Connection,
    ComponentLibrary,
    SpecificationExporter,
)


def test_visual_imports():
    """Test visual module imports."""
    assert VisualSpecification is not None
    assert Component is not None
    assert Connection is not None
    assert ComponentLibrary is not None
    assert SpecificationExporter is not None


def test_component_creation():
    """Test component creation."""
    comp = Component(
        id='comp1',
        type='led',
        name='LED1',
        properties={'pin': 13},
        position={'x': 100, 'y': 200}
    )
    
    assert comp.id == 'comp1'
    assert comp.type == 'led'
    assert comp.properties['pin'] == 13


def test_component_to_dict():
    """Test component serialization."""
    comp = Component(
        id='comp1',
        type='led',
        name='LED1',
        properties={'pin': 13},
        position={'x': 100, 'y': 200}
    )
    
    data = comp.to_dict()
    assert data['id'] == 'comp1'
    assert data['type'] == 'led'


def test_component_from_dict():
    """Test component deserialization."""
    data = {
        'id': 'comp1',
        'type': 'led',
        'name': 'LED1',
        'properties': {'pin': 13},
        'position': {'x': 100, 'y': 200}
    }
    
    comp = Component.from_dict(data)
    assert comp.id == 'comp1'
    assert comp.type == 'led'


def test_connection_creation():
    """Test connection creation."""
    conn = Connection(
        id='conn1',
        source_id='comp1',
        target_id='comp2',
        source_port='output',
        target_port='input',
        properties={}
    )
    
    assert conn.id == 'conn1'
    assert conn.source_id == 'comp1'
    assert conn.target_id == 'comp2'


def test_visual_specification_initialization():
    """Test specification initialization."""
    spec = VisualSpecification(name='Test Spec', description='Test')
    
    assert spec.name == 'Test Spec'
    assert spec.description == 'Test'
    assert len(spec.components) == 0
    assert len(spec.connections) == 0


def test_visual_specification_add_component():
    """Test adding components."""
    spec = VisualSpecification()
    
    comp_id = spec.add_component(
        'led',
        'LED1',
        properties={'pin': 13},
        position={'x': 100, 'y': 200}
    )
    
    assert comp_id is not None
    assert len(spec.components) == 1
    assert spec.components[comp_id].type == 'led'


def test_visual_specification_remove_component():
    """Test removing components."""
    spec = VisualSpecification()
    
    comp_id = spec.add_component('led', 'LED1')
    assert spec.remove_component(comp_id) is True
    assert len(spec.components) == 0


def test_visual_specification_update_component():
    """Test updating components."""
    spec = VisualSpecification()
    
    comp_id = spec.add_component('led', 'LED1', properties={'pin': 13})
    
    success = spec.update_component(
        comp_id,
        properties={'pin': 14, 'color': 'red'}
    )
    
    assert success is True
    assert spec.components[comp_id].properties['pin'] == 14
    assert spec.components[comp_id].properties['color'] == 'red'


def test_visual_specification_add_connection():
    """Test adding connections."""
    spec = VisualSpecification()
    
    comp1_id = spec.add_component('button', 'Button1')
    comp2_id = spec.add_component('led', 'LED1')
    
    conn_id = spec.add_connection(comp1_id, comp2_id)
    
    assert conn_id is not None
    assert len(spec.connections) == 1


def test_visual_specification_remove_connection():
    """Test removing connections."""
    spec = VisualSpecification()
    
    comp1_id = spec.add_component('button', 'Button1')
    comp2_id = spec.add_component('led', 'LED1')
    conn_id = spec.add_connection(comp1_id, comp2_id)
    
    assert spec.remove_connection(conn_id) is True
    assert len(spec.connections) == 0


def test_visual_specification_validate():
    """Test specification validation."""
    spec = VisualSpecification()
    
    comp1_id = spec.add_component('led', 'LED1')
    comp2_id = spec.add_component('led', 'LED1')  # Duplicate name
    
    errors = spec.validate()
    assert len(errors) > 0


def test_visual_specification_to_dict():
    """Test specification serialization."""
    spec = VisualSpecification(name='Test')
    comp_id = spec.add_component('led', 'LED1')
    
    data = spec.to_dict()
    
    assert data['name'] == 'Test'
    assert len(data['components']) == 1


def test_visual_specification_from_dict():
    """Test specification deserialization."""
    data = {
        'id': 'spec1',
        'name': 'Test',
        'description': 'Test spec',
        'components': {
            'comp1': {
                'id': 'comp1',
                'type': 'led',
                'name': 'LED1',
                'properties': {},
                'position': {}
            }
        },
        'connections': {},
        'metadata': {}
    }
    
    spec = VisualSpecification.from_dict(data)
    assert spec.name == 'Test'
    assert len(spec.components) == 1


def test_component_library_initialization():
    """Test component library initialization."""
    library = ComponentLibrary()
    
    assert len(library.components) > 0


def test_component_library_get_component():
    """Test getting component definition."""
    library = ComponentLibrary()
    
    led = library.get_component('led')
    assert led is not None
    assert led.type == 'led'
    assert led.name == 'LED'


def test_component_library_list_components():
    """Test listing components."""
    library = ComponentLibrary()
    
    all_components = library.list_components()
    assert len(all_components) > 0
    
    output_components = library.list_components(category='output')
    assert len(output_components) > 0


def test_component_library_get_categories():
    """Test getting categories."""
    library = ComponentLibrary()
    
    categories = library.get_categories()
    assert len(categories) > 0
    assert 'input' in categories or 'output' in categories


def test_component_library_search():
    """Test searching components."""
    library = ComponentLibrary()
    
    results = library.search_components('led')
    assert len(results) > 0


def test_specification_exporter_to_json():
    """Test exporting to JSON."""
    spec = VisualSpecification(name='Test')
    spec.add_component('led', 'LED1')
    
    exporter = SpecificationExporter(spec)
    json_str = exporter.to_json()
    
    assert isinstance(json_str, str)
    assert 'Test' in json_str


def test_specification_exporter_to_yaml():
    """Test exporting to YAML."""
    spec = VisualSpecification(name='Test')
    spec.add_component('led', 'LED1')
    
    exporter = SpecificationExporter(spec)
    yaml_str = exporter.to_yaml()
    
    assert isinstance(yaml_str, str)
    assert 'Test' in yaml_str


def test_specification_exporter_to_accelerapp_config():
    """Test exporting to Accelerapp config."""
    spec = VisualSpecification(name='Test Device')
    spec.add_component('microcontroller', 'MCU', properties={'platform': 'arduino'})
    spec.add_component('led', 'LED1', properties={'pin': 13})
    
    exporter = SpecificationExporter(spec)
    config = exporter.to_accelerapp_config()
    
    assert config['device_name'] == 'Test Device'
    assert config['platform'] == 'arduino'
    assert len(config['peripherals']) == 2


def test_specification_exporter_save_load_json():
    """Test saving and loading JSON."""
    spec = VisualSpecification(name='Test')
    spec.add_component('led', 'LED1')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'spec.json'
        
        exporter = SpecificationExporter(spec)
        exporter.save_json(filepath)
        
        loaded_spec = SpecificationExporter.load_json(filepath)
        assert loaded_spec.name == 'Test'


def test_specification_exporter_save_load_yaml():
    """Test saving and loading YAML."""
    spec = VisualSpecification(name='Test')
    spec.add_component('led', 'LED1')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'spec.yaml'
        
        exporter = SpecificationExporter(spec)
        exporter.save_yaml(filepath)
        
        loaded_spec = SpecificationExporter.load_yaml(filepath)
        assert loaded_spec.name == 'Test'


def test_specification_exporter_save_accelerapp_config():
    """Test saving Accelerapp config."""
    spec = VisualSpecification(name='Test Device')
    spec.add_component('led', 'LED1', properties={'pin': 13})
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'config.yaml'
        
        exporter = SpecificationExporter(spec)
        exporter.save_accelerapp_config(filepath)
        
        assert filepath.exists()
