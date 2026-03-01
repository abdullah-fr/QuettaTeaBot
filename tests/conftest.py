"""
Pytest configuration and custom report generation
"""

import pytest
import time
from pathlib import Path


# Store test results
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'duration': 0,
    'tests': []
}

start_time = None


def pytest_sessionstart(session):
    """Called at the start of test session"""
    global start_time
    start_time = time.time()


def pytest_runtest_logreport(report):
    """Called for each test phase (setup, call, teardown)"""
    if report.when == 'call':
        test_results['total'] += 1

        test_info = {
            'name': report.head_line if hasattr(report, 'head_line') else report.nodeid.split('::')[-1],
            'path': report.nodeid,
            'duration': report.duration,
            'status': 'passed'
        }

        if report.passed:
            test_results['passed'] += 1
            test_info['status'] = 'passed'
        elif report.failed:
            test_results['failed'] += 1
            test_info['status'] = 'failed'
        elif report.skipped:
            test_results['skipped'] += 1
            test_info['status'] = 'skipped'

        test_results['tests'].append(test_info)


def pytest_sessionfinish(session, exitstatus):
    """Called at the end of test session"""
    global start_time

    if start_time:
        test_results['duration'] = time.time() - start_time

    # Generate custom HTML report
    try:
        from tests.utils.report_generator import generate_html_report

        report_path = generate_html_report(test_results)
        print(f"\n✨ Custom HTML report generated: {report_path}")
    except Exception as e:
        print(f"\n⚠️  Could not generate custom report: {e}")


@pytest.fixture
def project_root():
    """Fixture to get project root directory"""
    return Path(__file__).parent.parent
