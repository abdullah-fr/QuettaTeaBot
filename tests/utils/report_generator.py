"""
Custom HTML Test Report Generator
Generates beautiful, Bootstrap-styled test reports
"""

import json
from datetime import datetime
from pathlib import Path


def generate_html_report(test_results, output_path="reports/test_report.html"):
    """
    Generate a visually appealing HTML test report with Bootstrap styling

    Args:
        test_results: Dictionary containing test results
        output_path: Path to save the HTML report
    """

    # Ensure reports directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    total_tests = test_results.get('total', 0)
    passed = test_results.get('passed', 0)
    failed = test_results.get('failed', 0)
    skipped = test_results.get('skipped', 0)
    duration = test_results.get('duration', 0)
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    # Get test details
    tests = test_results.get('tests', [])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quetta Tea Bot - Test Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {{
            --primary-color: #6366f1;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --info-color: #3b82f6;
            --dark-bg: #1e293b;
            --card-bg: #ffffff;
        }}

        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 2rem 0;
        }}

        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .header-card h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .header-card .subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .stats-card {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .stats-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}

        .stat-box {{
            text-align: center;
            padding: 1rem;
        }}

        .stat-number {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }}

        .stat-label {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            font-weight: 600;
        }}

        .progress-card {{
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .progress {{
            height: 30px;
            border-radius: 15px;
            background-color: #e2e8f0;
        }}

        .progress-bar {{
            border-radius: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .test-list-card {{
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .test-item {{
            border-left: 4px solid #e2e8f0;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            background: #f8fafc;
            transition: all 0.3s ease;
        }}

        .test-item:hover {{
            background: #f1f5f9;
            transform: translateX(5px);
        }}

        .test-item.passed {{
            border-left-color: var(--success-color);
        }}

        .test-item.failed {{
            border-left-color: var(--danger-color);
        }}

        .test-item.skipped {{
            border-left-color: var(--warning-color);
        }}

        .test-name {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}

        .test-path {{
            font-size: 0.85rem;
            color: #64748b;
            font-family: 'Courier New', monospace;
        }}

        .test-duration {{
            font-size: 0.85rem;
            color: #64748b;
        }}

        .badge-custom {{
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .icon-box {{
            width: 60px;
            height: 60px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }}

        .icon-box.success {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }}

        .icon-box.danger {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }}

        .icon-box.warning {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }}

        .icon-box.info {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 3rem;
            padding: 2rem;
        }}

        .footer a {{
            color: white;
            text-decoration: none;
            font-weight: 600;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .header-card h1 {{
                font-size: 1.8rem;
            }}

            .stat-number {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container report-container">
        <!-- Header -->
        <div class="header-card">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1><i class="bi bi-cup-hot-fill"></i> Quetta Tea Bot</h1>
                    <p class="subtitle mb-0">Automated Test Report</p>
                </div>
                <div class="text-end">
                    <div class="fs-5">{datetime.now().strftime('%B %d, %Y')}</div>
                    <div class="opacity-75">{datetime.now().strftime('%I:%M %p')}</div>
                </div>
            </div>
        </div>

        <!-- Summary Statistics -->
        <div class="summary-grid">
            <div class="stats-card">
                <div class="stat-box">
                    <div class="icon-box info mx-auto">
                        <i class="bi bi-list-check"></i>
                    </div>
                    <div class="stat-number text-primary">{total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
            </div>

            <div class="stats-card">
                <div class="stat-box">
                    <div class="icon-box success mx-auto">
                        <i class="bi bi-check-circle-fill"></i>
                    </div>
                    <div class="stat-number text-success">{passed}</div>
                    <div class="stat-label">Passed</div>
                </div>
            </div>

            <div class="stats-card">
                <div class="stat-box">
                    <div class="icon-box danger mx-auto">
                        <i class="bi bi-x-circle-fill"></i>
                    </div>
                    <div class="stat-number text-danger">{failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
            </div>

            <div class="stats-card">
                <div class="stat-box">
                    <div class="icon-box warning mx-auto">
                        <i class="bi bi-dash-circle-fill"></i>
                    </div>
                    <div class="stat-number text-warning">{skipped}</div>
                    <div class="stat-label">Skipped</div>
                </div>
            </div>
        </div>

        <!-- Progress Bar -->
        <div class="progress-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 class="mb-0"><i class="bi bi-graph-up"></i> Test Coverage</h3>
                <span class="badge bg-success badge-custom">{pass_rate:.1f}% Pass Rate</span>
            </div>
            <div class="progress">
                <div class="progress-bar bg-success" role="progressbar" style="width: {pass_rate}%">
                    {passed} Passed
                </div>
                <div class="progress-bar bg-danger" role="progressbar" style="width: {(failed/total_tests*100) if total_tests > 0 else 0}%">
                    {failed} Failed
                </div>
                <div class="progress-bar bg-warning" role="progressbar" style="width: {(skipped/total_tests*100) if total_tests > 0 else 0}%">
                    {skipped} Skipped
                </div>
            </div>
            <div class="mt-3 text-center">
                <span class="text-muted"><i class="bi bi-clock"></i> Total Duration: <strong>{duration:.2f}s</strong></span>
            </div>
        </div>

        <!-- Test Results -->
        <div class="test-list-card">
            <h3 class="mb-4"><i class="bi bi-file-earmark-text"></i> Test Results</h3>

            {generate_test_items(tests)}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p class="mb-2">Generated by <strong>Quetta Tea Bot Test Suite</strong></p>
            <p class="mb-0">
                <a href="https://github.com/abdullah-fr/QuettaTeaBot" target="_blank">
                    <i class="bi bi-github"></i> View on GitHub
                </a>
            </p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


def generate_test_items(tests):
    """Generate HTML for individual test items"""
    if not tests:
        return '<p class="text-muted">No test results available.</p>'

    html = ''
    for test in tests:
        status = test.get('status', 'unknown')
        name = test.get('name', 'Unknown Test')
        path = test.get('path', '')
        duration = test.get('duration', 0)

        # Determine badge and icon
        if status == 'passed':
            badge_class = 'bg-success'
            icon = 'bi-check-circle-fill'
            status_text = 'PASSED'
        elif status == 'failed':
            badge_class = 'bg-danger'
            icon = 'bi-x-circle-fill'
            status_text = 'FAILED'
        else:
            badge_class = 'bg-warning'
            icon = 'bi-dash-circle-fill'
            status_text = 'SKIPPED'

        html += f"""
            <div class="test-item {status}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="test-name">
                            <i class="bi {icon} text-{status}"></i> {name}
                        </div>
                        <div class="test-path">{path}</div>
                    </div>
                    <div class="text-end">
                        <span class="badge {badge_class} badge-custom">{status_text}</span>
                        <div class="test-duration mt-2">
                            <i class="bi bi-stopwatch"></i> {duration:.3f}s
                        </div>
                    </div>
                </div>
            </div>
        """

    return html


if __name__ == "__main__":
    # Example usage
    sample_results = {
        'total': 12,
        'passed': 12,
        'failed': 0,
        'skipped': 0,
        'duration': 0.35,
        'tests': [
            {
                'name': 'test_iftar_countdown_one_hour_remaining',
                'path': 'tests/features/test_iftar_countdown.py',
                'status': 'passed',
                'duration': 0.028
            },
            {
                'name': 'test_project_structure_exists',
                'path': 'tests/test_smoke.py::TestProjectSetup',
                'status': 'passed',
                'duration': 0.012
            },
        ]
    }

    generate_html_report(sample_results)
    print("Report generated successfully!")
