"""
Test runner for executing HIL tests.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
from .framework import HILTestFramework, TestResult, TestStatus


class TestRunner:
    """
    Manages test execution and reporting.
    """
    
    def __init__(self, framework: HILTestFramework):
        """
        Initialize test runner.
        
        Args:
            framework: HIL test framework
        """
        self.framework = framework
        self.reports: List[Dict[str, Any]] = []
    
    def run_tests(
        self,
        test_ids: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run tests and generate report.
        
        Args:
            test_ids: Specific test IDs to run (None for all)
            verbose: Enable verbose output
            
        Returns:
            Test report dictionary
        """
        if test_ids:
            results = []
            for test_id in test_ids:
                result = self.framework.run_test(test_id)
                results.append(result)
                if verbose:
                    self._print_result(result)
        else:
            results = self.framework.run_all_tests()
            if verbose:
                for result in results:
                    self._print_result(result)
        
        summary = self.framework.get_test_summary()
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': summary,
            'results': [r.to_dict() for r in results],
        }
        
        self.reports.append(report)
        
        return report
    
    def _print_result(self, result: TestResult):
        """Print test result to console."""
        status_symbols = {
            TestStatus.PASSED: '✓',
            TestStatus.FAILED: '✗',
            TestStatus.ERROR: '⚠',
            TestStatus.SKIPPED: '○',
        }
        
        symbol = status_symbols.get(result.status, '?')
        print(f"{symbol} {result.test_name} ({result.duration:.3f}s)")
        
        if result.message and result.status != TestStatus.PASSED:
            print(f"  {result.message}")
    
    def save_report(self, filepath: Path, report_format: str = 'json'):
        """
        Save test report to file.
        
        Args:
            filepath: Output file path
            report_format: Report format (json, html)
        """
        if not self.reports:
            return
        
        latest_report = self.reports[-1]
        
        if report_format == 'json':
            with open(filepath, 'w') as f:
                json.dump(latest_report, f, indent=2)
        
        elif report_format == 'html':
            html = self._generate_html_report(latest_report)
            filepath.write_text(html)
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report."""
        summary = report['summary']
        results = report['results']
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HIL Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .error {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>HIL Test Report</h1>
    <p>Generated: {report['timestamp']}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {summary['total']}</p>
        <p class="passed">Passed: {summary['passed']}</p>
        <p class="failed">Failed: {summary['failed']}</p>
        <p class="error">Errors: {summary['error']}</p>
        <p>Pass Rate: {summary['pass_rate']:.1f}%</p>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration (s)</th>
            <th>Message</th>
        </tr>
"""
        
        for result in results:
            status_class = result['status']
            html += f"""        <tr>
            <td>{result['test_name']}</td>
            <td class="{status_class}">{result['status']}</td>
            <td>{result['duration']:.3f}</td>
            <td>{result['message']}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>"""
        
        return html
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest test report.
        
        Returns:
            Latest report or None
        """
        return self.reports[-1] if self.reports else None
    
    def clear_reports(self):
        """Clear all stored reports."""
        self.reports.clear()
