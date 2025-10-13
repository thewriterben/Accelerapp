"""
Tests for code optimization agents.
"""

import pytest
from accelerapp.agents import (
    PerformanceOptimizationAgent,
    MemoryOptimizationAgent,
    CodeQualityAgent,
    SecurityAnalysisAgent,
    RefactoringAgent
)


def test_performance_agent_initialization():
    """Test performance optimization agent initialization."""
    agent = PerformanceOptimizationAgent()
    assert agent.name == "Performance Optimization Agent"
    assert 'performance_analysis' in agent.capabilities
    assert 'bottleneck_detection' in agent.capabilities


def test_performance_agent_can_handle():
    """Test performance agent task handling."""
    agent = PerformanceOptimizationAgent()
    assert agent.can_handle("performance_analysis")
    assert agent.can_handle("bottleneck_detection")
    assert not agent.can_handle("unrelated_task")


def test_performance_analysis():
    """Test performance analysis."""
    agent = PerformanceOptimizationAgent()
    
    code = """
    void loop() {
        for(int i = 0; i < 100; i++) {
            delay(10);
        }
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    assert 'issues' in result['analysis']
    assert 'suggestions' in result['analysis']


def test_memory_agent_initialization():
    """Test memory optimization agent initialization."""
    agent = MemoryOptimizationAgent()
    assert agent.name == "Memory Optimization Agent"
    assert 'memory_analysis' in agent.capabilities
    assert 'leak_detection' in agent.capabilities


def test_memory_leak_detection():
    """Test memory leak detection."""
    agent = MemoryOptimizationAgent()
    
    code = """
    void setup() {
        char* buffer = (char*)malloc(1024);
        int* data = new int[100];
        processData(buffer, data);
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    issues = result['analysis']['issues']
    # Should detect memory allocation without deallocation
    assert any(issue['type'] == 'memory_leak' for issue in issues)


def test_memory_optimization_arduino():
    """Test Arduino-specific memory optimization."""
    agent = MemoryOptimizationAgent()
    
    code = """
    void loop() {
        Serial.println("This is a long string");
    }
    """
    
    result = agent.generate({
        'code': code,
        'language': 'cpp',
        'platform': 'arduino'
    })
    
    assert result['status'] == 'success'
    issues = result['analysis']['issues']
    # Should suggest using F() macro
    assert any('ram' in issue['type'].lower() for issue in issues)


def test_code_quality_agent_initialization():
    """Test code quality agent initialization."""
    agent = CodeQualityAgent()
    assert agent.name == "Code Quality Agent"
    assert 'quality_analysis' in agent.capabilities
    assert 'best_practices' in agent.capabilities


def test_code_quality_analysis():
    """Test code quality analysis."""
    agent = CodeQualityAgent()
    
    code = """
    void func() {
        int x = 42;
        int y = x * 2;
        if(y > 50) {
            return;
        }
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    assert 'quality_score' in result['analysis']
    assert 'grade' in result['analysis']
    assert result['analysis']['quality_score'] >= 0
    assert result['analysis']['quality_score'] <= 100


def test_quality_score_grading():
    """Test quality score to grade conversion."""
    agent = CodeQualityAgent()
    
    assert agent._score_to_grade(95) == 'A'
    assert agent._score_to_grade(85) == 'B'
    assert agent._score_to_grade(75) == 'C'
    assert agent._score_to_grade(65) == 'D'
    assert agent._score_to_grade(55) == 'F'


def test_security_agent_initialization():
    """Test security analysis agent initialization."""
    agent = SecurityAnalysisAgent()
    assert agent.name == "Security Analysis Agent"
    assert 'vulnerability_detection' in agent.capabilities
    assert 'security_audit' in agent.capabilities


def test_buffer_overflow_detection():
    """Test buffer overflow vulnerability detection."""
    agent = SecurityAnalysisAgent()
    
    code = """
    void copy_string(char* dest, char* src) {
        strcpy(dest, src);
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    vulns = result['analysis']['vulnerabilities']
    assert any(v['type'] == 'buffer_overflow' for v in vulns)
    assert any(v['severity'] == 'critical' for v in vulns)


def test_input_validation_check():
    """Test input validation checking."""
    agent = SecurityAnalysisAgent()
    
    code = """
    void process() {
        int value = Serial.read();
        // No validation
        doSomething(value);
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    vulns = result['analysis']['vulnerabilities']
    assert any('validation' in v['type'].lower() for v in vulns)


def test_security_score_calculation():
    """Test security score calculation."""
    agent = SecurityAnalysisAgent()
    
    # Code with critical vulnerability
    code = """
    void unsafe() {
        char buffer[10];
        gets(buffer);
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    score = result['analysis']['security_score']
    assert score < 100  # Should be penalized
    assert result['analysis']['risk_level'] in ['low', 'medium', 'high', 'critical']


def test_refactoring_agent_initialization():
    """Test refactoring agent initialization."""
    agent = RefactoringAgent()
    assert agent.name == "Refactoring Agent"
    assert 'code_refactoring' in agent.capabilities
    assert 'code_smells' in agent.capabilities


def test_refactoring_analysis():
    """Test refactoring analysis."""
    agent = RefactoringAgent()
    
    code = """
    void bigFunction(int a, int b, int c, int d, int e, int f) {
        // 50+ lines of code...
        """ + "\n        // line" * 50 + """
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    assert result['status'] == 'success'
    assert 'analysis' in result
    assert 'code_smells' in result['analysis']
    assert 'refactoring_suggestions' in result['analysis']


def test_long_parameter_list_detection():
    """Test detection of long parameter lists."""
    agent = RefactoringAgent()
    
    code = """
    void func(int a, int b, int c, int d, int e, int f) {
        // Code
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    smells = result['analysis']['code_smells']
    assert any('parameter' in smell['type'].lower() for smell in smells)


def test_all_agents_info():
    """Test that all agents return proper info."""
    agents = [
        PerformanceOptimizationAgent(),
        MemoryOptimizationAgent(),
        CodeQualityAgent(),
        SecurityAnalysisAgent(),
        RefactoringAgent()
    ]
    
    for agent in agents:
        info = agent.get_info()
        assert 'name' in info
        assert 'type' in info
        assert 'capabilities' in info
        assert 'version' in info
        assert 'description' in info
        assert info['version'] == '1.0.0'
