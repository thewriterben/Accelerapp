"""
Tests for HIL testing framework.
"""

import pytest
import tempfile
from pathlib import Path
from accelerapp.hil import (
    HILTestFramework,
    TestCase,
    TestResult,
    HardwareInterface,
    DeviceAdapter,
    TestRunner,
)
from accelerapp.hil.framework import TestStatus
from accelerapp.hil.hardware import SimulatedHardware, PinMode


def test_hil_imports():
    """Test HIL module imports."""
    assert HILTestFramework is not None
    assert TestCase is not None
    assert TestResult is not None
    assert HardwareInterface is not None
    assert DeviceAdapter is not None
    assert TestRunner is not None


def test_test_result_creation():
    """Test test result creation."""
    result = TestResult(
        test_id='test1',
        test_name='Test 1',
        status=TestStatus.PASSED,
        message='Success',
        duration=1.5
    )
    
    assert result.test_id == 'test1'
    assert result.status == TestStatus.PASSED
    assert result.duration == 1.5


def test_test_result_to_dict():
    """Test result serialization."""
    result = TestResult(
        test_id='test1',
        test_name='Test 1',
        status=TestStatus.PASSED
    )
    
    data = result.to_dict()
    assert data['test_id'] == 'test1'
    assert data['status'] == 'passed'


def test_test_case_creation():
    """Test test case creation."""
    class SimpleTest(TestCase):
        def execute(self):
            self.assert_true(True)
    
    test = SimpleTest('test1', 'Simple Test')
    assert test.test_id == 'test1'
    assert test.name == 'Simple Test'


def test_test_case_assertions():
    """Test assertion methods."""
    class AssertionTest(TestCase):
        def execute(self):
            self.assert_equal(1, 1)
            self.assert_true(True)
            self.assert_false(False)
    
    test = AssertionTest('test1', 'Assertion Test')
    result = test.run()
    
    assert result.status == TestStatus.PASSED


def test_test_case_failed_assertion():
    """Test failed assertion."""
    class FailedTest(TestCase):
        def execute(self):
            self.assert_equal(1, 2)
    
    test = FailedTest('test1', 'Failed Test')
    result = test.run()
    
    assert result.status == TestStatus.FAILED


def test_test_case_error():
    """Test test error handling."""
    class ErrorTest(TestCase):
        def execute(self):
            raise ValueError("Test error")
    
    test = ErrorTest('test1', 'Error Test')
    result = test.run()
    
    assert result.status == TestStatus.ERROR


def test_hil_framework_initialization():
    """Test framework initialization."""
    framework = HILTestFramework()
    
    assert framework is not None
    assert len(framework.test_cases) == 0


def test_hil_framework_register_test():
    """Test registering tests."""
    framework = HILTestFramework()
    
    class DummyTest(TestCase):
        def execute(self):
            pass
    
    test = DummyTest('test1', 'Dummy')
    framework.register_test(test)
    
    assert len(framework.test_cases) == 1
    assert 'test1' in framework.test_cases


def test_hil_framework_run_test():
    """Test running a single test."""
    framework = HILTestFramework()
    
    class PassingTest(TestCase):
        def execute(self):
            self.assert_true(True)
    
    test = PassingTest('test1', 'Passing Test')
    framework.register_test(test)
    
    result = framework.run_test('test1')
    
    assert result.status == TestStatus.PASSED


def test_hil_framework_run_all_tests():
    """Test running all tests."""
    framework = HILTestFramework()
    
    class Test1(TestCase):
        def execute(self):
            pass
    
    class Test2(TestCase):
        def execute(self):
            pass
    
    framework.register_test(Test1('test1', 'Test 1'))
    framework.register_test(Test2('test2', 'Test 2'))
    
    results = framework.run_all_tests()
    
    assert len(results) == 2


def test_hil_framework_get_summary():
    """Test getting test summary."""
    framework = HILTestFramework()
    
    class PassingTest(TestCase):
        def execute(self):
            pass
    
    class FailingTest(TestCase):
        def execute(self):
            self.assert_true(False)
    
    framework.register_test(PassingTest('test1', 'Pass'))
    framework.register_test(FailingTest('test2', 'Fail'))
    
    framework.run_all_tests()
    summary = framework.get_test_summary()
    
    assert summary['total'] == 2
    assert summary['passed'] == 1
    assert summary['failed'] == 1


def test_simulated_hardware_connect():
    """Test simulated hardware connection."""
    hardware = SimulatedHardware()
    
    assert hardware.connect() is True
    assert hardware.is_connected() is True


def test_simulated_hardware_digital_io():
    """Test digital I/O."""
    hardware = SimulatedHardware()
    hardware.connect()
    
    hardware.digital_write(13, True)
    assert hardware.digital_read(13) is True
    
    hardware.digital_write(13, False)
    assert hardware.digital_read(13) is False


def test_simulated_hardware_analog_io():
    """Test analog I/O."""
    hardware = SimulatedHardware()
    hardware.connect()
    
    hardware.analog_write(5, 128)
    assert hardware.analog_read(5) == 128


def test_simulated_hardware_reset():
    """Test hardware reset."""
    hardware = SimulatedHardware()
    hardware.connect()
    
    hardware.digital_write(13, True)
    hardware.reset()
    
    assert hardware.digital_read(13) is False


def test_device_adapter_initialization():
    """Test device adapter initialization."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino')
    
    assert adapter.device_type == 'arduino'
    assert adapter.initialized is False


def test_device_adapter_initialize():
    """Test device initialization."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino')
    
    assert adapter.initialize() is True
    assert adapter.initialized is True


def test_device_adapter_test_led():
    """Test LED testing."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino')
    adapter.initialize()
    
    result = adapter.test_led(13, duration=0.1)
    assert result is True


def test_device_adapter_test_button():
    """Test button testing."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino')
    adapter.initialize()
    
    # Simulate button state
    hardware.digital_write(2, True)
    
    result = adapter.test_button(2)
    assert result is not None


def test_device_adapter_test_analog_sensor():
    """Test analog sensor testing."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino')
    adapter.initialize()
    
    # Simulate sensor value
    hardware.analog_write(0, 512)
    
    result = adapter.test_analog_sensor(0)
    assert result == 512


def test_device_adapter_get_info():
    """Test getting device info."""
    hardware = SimulatedHardware()
    adapter = DeviceAdapter(hardware, 'arduino', config={'test': 'value'})
    adapter.initialize()
    
    info = adapter.get_device_info()
    
    assert info['device_type'] == 'arduino'
    assert info['initialized'] is True
    assert info['connected'] is True


def test_test_runner_initialization():
    """Test runner initialization."""
    framework = HILTestFramework()
    runner = TestRunner(framework)
    
    assert runner.framework == framework


def test_test_runner_run_tests():
    """Test running tests with runner."""
    framework = HILTestFramework()
    
    class SimpleTest(TestCase):
        def execute(self):
            self.assert_true(True)
    
    framework.register_test(SimpleTest('test1', 'Simple'))
    
    runner = TestRunner(framework)
    report = runner.run_tests()
    
    assert 'summary' in report
    assert 'results' in report
    assert report['summary']['total'] == 1


def test_test_runner_save_json_report():
    """Test saving JSON report."""
    framework = HILTestFramework()
    
    class SimpleTest(TestCase):
        def execute(self):
            pass
    
    framework.register_test(SimpleTest('test1', 'Simple'))
    
    runner = TestRunner(framework)
    runner.run_tests()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'report.json'
        runner.save_report(filepath, report_format='json')
        
        assert filepath.exists()


def test_test_runner_save_html_report():
    """Test saving HTML report."""
    framework = HILTestFramework()
    
    class SimpleTest(TestCase):
        def execute(self):
            pass
    
    framework.register_test(SimpleTest('test1', 'Simple'))
    
    runner = TestRunner(framework)
    runner.run_tests()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'report.html'
        runner.save_report(filepath, report_format='html')
        
        assert filepath.exists()
        content = filepath.read_text()
        assert '<html>' in content


def test_test_runner_get_latest_report():
    """Test getting latest report."""
    framework = HILTestFramework()
    
    class SimpleTest(TestCase):
        def execute(self):
            pass
    
    framework.register_test(SimpleTest('test1', 'Simple'))
    
    runner = TestRunner(framework)
    runner.run_tests()
    
    report = runner.get_latest_report()
    assert report is not None
    assert 'summary' in report
