"""
Tests for knowledge module.
"""

import pytest
from pathlib import Path
import tempfile


def test_knowledge_base_import():
    """Test knowledge base import."""
    from accelerapp.knowledge import KnowledgeBase, KnowledgeEntry
    assert KnowledgeBase is not None
    assert KnowledgeEntry is not None


def test_template_manager_import():
    """Test template manager import."""
    from accelerapp.knowledge import TemplateManager, Template, TemplateCategory
    assert TemplateManager is not None
    assert Template is not None
    assert TemplateCategory is not None


def test_pattern_analyzer_import():
    """Test pattern analyzer import."""
    from accelerapp.knowledge import PatternAnalyzer, CodePattern
    assert PatternAnalyzer is not None
    assert CodePattern is not None


def test_offline_docs_import():
    """Test offline docs import."""
    from accelerapp.knowledge import OfflineDocumentation, DocEntry
    assert OfflineDocumentation is not None
    assert DocEntry is not None


def test_knowledge_base_initialization():
    """Test knowledge base initialization."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        assert kb is not None
        assert kb.entries == {}


def test_knowledge_base_add_entry():
    """Test adding entry to knowledge base."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        
        entry = kb.add_entry(
            entry_id="test1",
            content="This is a test entry about firmware development",
            category="firmware"
        )
        
        assert entry is not None
        assert entry.id == "test1"
        assert "test1" in kb.entries


def test_knowledge_base_search():
    """Test knowledge base search."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        
        # Add some entries
        kb.add_entry("entry1", "Arduino firmware development", category="firmware")
        kb.add_entry("entry2", "Python SDK development", category="software")
        kb.add_entry("entry3", "React UI development", category="ui")
        
        # Rebuild index for search
        kb.rebuild_index()
        
        # Search for firmware
        results = kb.search("firmware", limit=5)
        assert len(results) > 0


def test_knowledge_base_update():
    """Test updating knowledge base entry."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        
        kb.add_entry("test1", "Original content")
        result = kb.update_entry("test1", content="Updated content")
        
        assert result is True
        entry = kb.get_entry("test1")
        assert entry.content == "Updated content"


def test_knowledge_base_delete():
    """Test deleting entry."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        
        kb.add_entry("test1", "Test content")
        assert "test1" in kb.entries
        
        result = kb.delete_entry("test1")
        assert result is True
        assert "test1" not in kb.entries


def test_knowledge_base_stats():
    """Test knowledge base statistics."""
    from accelerapp.knowledge import KnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(storage_dir=Path(tmpdir))
        
        kb.add_entry("e1", "Content 1", category="firmware")
        kb.add_entry("e2", "Content 2", category="software")
        kb.add_entry("e3", "Content 3", category="firmware")
        
        stats = kb.get_stats()
        assert stats["total_entries"] == 3
        assert stats["categories"]["firmware"] == 2
        assert stats["categories"]["software"] == 1


def test_template_manager_initialization():
    """Test template manager initialization."""
    from accelerapp.knowledge import TemplateManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = TemplateManager(storage_dir=Path(tmpdir))
        assert tm is not None
        assert tm.templates == {}


def test_template_manager_add_template():
    """Test adding template."""
    from accelerapp.knowledge import TemplateManager, Template, TemplateCategory
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = TemplateManager(storage_dir=Path(tmpdir))
        
        template = Template(
            id="template1",
            name="Arduino Template",
            category=TemplateCategory.FIRMWARE,
            content="void setup() { {{setup_code}} }",
            variables=["setup_code"]
        )
        
        tm.add_template(template)
        assert "template1" in tm.templates


def test_template_manager_get_template():
    """Test getting template."""
    from accelerapp.knowledge import TemplateManager, Template, TemplateCategory
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = TemplateManager(storage_dir=Path(tmpdir))
        
        template = Template(
            id="template1",
            name="Test Template",
            category=TemplateCategory.FIRMWARE,
            content="test content"
        )
        tm.add_template(template)
        
        retrieved = tm.get_template("template1")
        assert retrieved is not None
        assert retrieved.id == "template1"


def test_template_manager_render():
    """Test rendering template with variables."""
    from accelerapp.knowledge import TemplateManager, Template, TemplateCategory
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = TemplateManager(storage_dir=Path(tmpdir))
        
        template = Template(
            id="template1",
            name="Test",
            category=TemplateCategory.FIRMWARE,
            content="Hello {{name}}, value is {{value}}",
            variables=["name", "value"]
        )
        tm.add_template(template)
        
        rendered = tm.render_template("template1", {"name": "World", "value": "42"})
        assert rendered == "Hello World, value is 42"


def test_template_manager_list_templates():
    """Test listing templates."""
    from accelerapp.knowledge import TemplateManager, Template, TemplateCategory
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = TemplateManager(storage_dir=Path(tmpdir))
        
        tm.add_template(Template("t1", "T1", TemplateCategory.FIRMWARE, "c1"))
        tm.add_template(Template("t2", "T2", TemplateCategory.SOFTWARE, "c2"))
        tm.add_template(Template("t3", "T3", TemplateCategory.FIRMWARE, "c3"))
        
        all_templates = tm.list_templates()
        assert len(all_templates) == 3
        
        firmware_templates = tm.list_templates(category=TemplateCategory.FIRMWARE)
        assert len(firmware_templates) == 2


def test_pattern_analyzer_initialization():
    """Test pattern analyzer initialization."""
    from accelerapp.knowledge import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    assert analyzer is not None
    assert analyzer.patterns == {}


def test_pattern_analyzer_analyze():
    """Test analyzing code."""
    from accelerapp.knowledge import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    
    c_code = """
    void setup() {
        for (int i = 0; i < 10; i++) {
            digitalWrite(LED, HIGH);
        }
    }
    """
    
    results = analyzer.analyze(c_code, "c")
    assert results["language"] == "c"
    assert results["line_count"] > 0
    assert "loop_pattern" in results["patterns"]


def test_pattern_analyzer_record_pattern():
    """Test recording patterns."""
    from accelerapp.knowledge import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    
    analyzer.record_pattern(
        pattern_id="loop1",
        pattern_type="for_loop",
        code_snippet="for (int i = 0; i < n; i++)"
    )
    
    assert "loop1" in analyzer.patterns
    assert analyzer.patterns["loop1"].frequency == 1
    
    # Record same pattern again
    analyzer.record_pattern(
        pattern_id="loop1",
        pattern_type="for_loop",
        code_snippet="for (int i = 0; i < n; i++)"
    )
    
    assert analyzer.patterns["loop1"].frequency == 2


def test_pattern_analyzer_common_patterns():
    """Test getting common patterns."""
    from accelerapp.knowledge import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    
    analyzer.record_pattern("p1", "type1", "code1")
    analyzer.record_pattern("p2", "type2", "code2")
    analyzer.record_pattern("p2", "type2", "code2")  # Increment frequency
    analyzer.record_pattern("p3", "type3", "code3")
    
    common = analyzer.get_common_patterns(limit=2)
    assert len(common) <= 2
    assert common[0].pattern_id == "p2"  # Should be first (highest frequency)


def test_offline_docs_initialization():
    """Test offline documentation initialization."""
    from accelerapp.knowledge import OfflineDocumentation
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = OfflineDocumentation(docs_dir=Path(tmpdir))
        assert docs is not None
        # Should have default docs
        assert len(docs.entries) > 0


def test_offline_docs_add_entry():
    """Test adding documentation entry."""
    from accelerapp.knowledge import OfflineDocumentation, DocEntry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = OfflineDocumentation(docs_dir=Path(tmpdir))
        
        entry = DocEntry(
            id="test-doc",
            title="Test Documentation",
            content="This is test documentation content",
            category="test",
            tags=["test", "demo"]
        )
        
        docs.add_entry(entry)
        assert "test-doc" in docs.entries


def test_offline_docs_search():
    """Test searching documentation."""
    from accelerapp.knowledge import OfflineDocumentation, DocEntry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = OfflineDocumentation(docs_dir=Path(tmpdir))
        
        docs.add_entry(DocEntry(
            id="doc1",
            title="Firmware Guide",
            content="Guide for firmware development",
            category="guide",
            tags=["firmware"]
        ))
        
        results = docs.search("firmware")
        assert len(results) > 0
        assert any("firmware" in r.title.lower() for r in results)


def test_offline_docs_get_by_category():
    """Test getting docs by category."""
    from accelerapp.knowledge import OfflineDocumentation, DocEntry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = OfflineDocumentation(docs_dir=Path(tmpdir))
        
        docs.add_entry(DocEntry("d1", "Doc 1", "Content", "guide", []))
        docs.add_entry(DocEntry("d2", "Doc 2", "Content", "api", []))
        docs.add_entry(DocEntry("d3", "Doc 3", "Content", "guide", []))
        
        guide_docs = docs.get_by_category("guide")
        assert len(guide_docs) >= 2
