# 📊 Test Reporting Guide

## Overview

The Quetta Tea Bot project includes a beautiful, Bootstrap-styled HTML test report that automatically generates after every test run.

---

## 🎨 Features

### Visual Design
- **Bootstrap 5** - Modern, responsive design
- **Gradient backgrounds** - Eye-catching purple gradient theme
- **Card-based layout** - Clean, organized information display
- **Icons** - Bootstrap Icons for visual clarity
- **Animations** - Smooth hover effects and transitions

### Report Sections

#### 1. Header
- Project name with icon
- Current date and time
- Gradient background matching bot theme

#### 2. Summary Statistics (4 Cards)
- **Total Tests** - Blue icon with total count
- **Passed Tests** - Green checkmark with pass count
- **Failed Tests** - Red X with failure count
- **Skipped Tests** - Yellow dash with skip count

Each card features:
- Large, bold numbers
- Colored icon boxes with gradients
- Hover animations (lift effect)

#### 3. Progress Bar
- Visual representation of test results
- Color-coded segments:
  - Green: Passed tests
  - Red: Failed tests
  - Yellow: Skipped tests
- Pass rate percentage badge
- Total duration display

#### 4. Test Results List
- Individual test items with:
  - Test name and path
  - Status badge (PASSED/FAILED/SKIPPED)
  - Execution duration
  - Color-coded left border
  - Hover effects

#### 5. Footer
- Project attribution
- GitHub link
- Clean, centered design

---

## 🚀 Usage

### Automatic Generation

The report is automatically generated every time you run tests:

```bash
pytest tests/ -v
```

Output:
```
✨ Custom HTML report generated: reports/test_report.html
```

### Using the Report Generator Script

```bash
python generate_report.py
```

This script:
1. Runs all tests
2. Generates the HTML report
3. Displays the file path
4. Shows the browser URL

### Opening the Report

**Option 1: Direct file open**
```bash
open reports/test_report.html  # macOS
xdg-open reports/test_report.html  # Linux
start reports/test_report.html  # Windows
```

**Option 2: Browser URL**
```
file:///path/to/your/project/reports/test_report.html
```

---

## 📁 File Structure

```
QuettaTeaBot/
├── tests/
│   ├── conftest.py                    # Pytest configuration & hooks
│   └── utils/
│       └── report_generator.py        # Custom report generator
├── reports/
│   └── test_report.html              # Generated report (auto-created)
└── generate_report.py                 # Standalone report script
```

---

## 🔧 Technical Details

### Report Generator (`tests/utils/report_generator.py`)

**Key Functions:**
- `generate_html_report(test_results, output_path)` - Main generator
- `generate_test_items(tests)` - Creates test item HTML

**Input Format:**
```python
test_results = {
    'total': 12,
    'passed': 12,
    'failed': 0,
    'skipped': 0,
    'duration': 0.35,
    'tests': [
        {
            'name': 'test_name',
            'path': 'tests/path/to/test.py',
            'status': 'passed',  # or 'failed', 'skipped'
            'duration': 0.028
        },
        # ... more tests
    ]
}
```

### Pytest Integration (`tests/conftest.py`)

**Hooks Used:**
- `pytest_sessionstart()` - Start timer
- `pytest_runtest_logreport()` - Collect test results
- `pytest_sessionfinish()` - Generate report

**Fixtures:**
- `project_root` - Returns project root directory

---

## 🎨 Customization

### Colors

Edit `tests/utils/report_generator.py` CSS variables:

```css
:root {
    --primary-color: #6366f1;    /* Primary blue */
    --success-color: #10b981;    /* Success green */
    --danger-color: #ef4444;     /* Danger red */
    --warning-color: #f59e0b;    /* Warning yellow */
    --info-color: #3b82f6;       /* Info blue */
}
```

### Gradient Background

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

Change the hex colors to customize the gradient.

### Card Styling

Modify `.stats-card` and `.test-list-card` classes for different card appearances.

---

## 📊 Example Report Statistics

**Current Project Stats:**
- Total Tests: 12
- Passed: 12
- Failed: 0
- Skipped: 0
- Pass Rate: 100%
- Duration: ~0.35s

---

## 🔄 CI/CD Integration

The report is automatically generated in CI/CD pipelines:

```yaml
- name: Run pytest
  run: |
    pytest tests/ -v --tb=short
  # Report is auto-generated via conftest.py
```

**Note**: The `reports/` folder is in `.gitignore` to avoid committing auto-generated files.

---

## 📱 Responsive Design

The report is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablets (iPad, Android tablets)
- Mobile devices (iPhone, Android phones)

**Mobile Optimizations:**
- Smaller font sizes
- Stacked layout for statistics
- Touch-friendly buttons and links

---

## 🐛 Troubleshooting

### Report Not Generated

**Issue**: No report file after running tests

**Solutions:**
1. Check if `reports/` directory exists (auto-created)
2. Verify `tests/conftest.py` is present
3. Check for import errors in `tests/utils/report_generator.py`
4. Run with verbose output: `pytest tests/ -v -s`

### Styling Issues

**Issue**: Report looks broken or unstyled

**Solutions:**
1. Check internet connection (Bootstrap CDN required)
2. Open browser console for errors
3. Verify HTML file is complete (not truncated)

### Import Errors

**Issue**: `ModuleNotFoundError` when generating report

**Solutions:**
1. Ensure you're running from project root
2. Check Python path: `export PYTHONPATH=$PWD`
3. Verify all test files are in `tests/` directory

---

## 🎯 Best Practices

1. **Run tests before commits** - Always generate fresh report
2. **Review failed tests** - Check report for detailed failure info
3. **Track pass rate** - Monitor test health over time
4. **Share reports** - Send HTML file to team members
5. **Archive reports** - Save reports for historical comparison

---

## 🔮 Future Enhancements

Potential improvements:
- [ ] Test history tracking (compare runs)
- [ ] Coverage percentage display
- [ ] Failure screenshots (for UI tests)
- [ ] Performance graphs
- [ ] Export to PDF
- [ ] Email report option
- [ ] Slack/Discord integration

---

## 📚 Resources

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Hooks](https://docs.pytest.org/en/stable/reference/reference.html#hooks)

---

**Last Updated**: March 1, 2026
**Version**: 1.0.0
**Status**: ✅ Production Ready
