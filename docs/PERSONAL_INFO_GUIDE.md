# Personal Information File Guide

## What is PERSONAL_INFO.md?

`docs/PERSONAL_INFO.md` is a private file on your local machine that contains:
- Your contact information
- Resume bullet points (customizable)
- Cover letter templates
- LinkedIn post templates
- Interview preparation notes
- Job application checklists
- References

## Why is it separate?

✅ **Privacy**: Your personal information stays on your laptop
✅ **Security**: No risk of accidentally committing personal details to GitHub
✅ **Flexibility**: Customize for each job application without affecting the public portfolio
✅ **Professional**: Public portfolio remains clean and professional

## How to use it?

### 1. The file already exists on your laptop
Location: `docs/PERSONAL_INFO.md`

### 2. Customize it with your information
Open the file and replace placeholders:
- `[Your Full Name]` → Your actual name
- `[your.email@example.com]` → Your email
- `[Your Phone Number]` → Your phone
- etc.

### 3. Use it for job applications
- Copy resume bullet points
- Customize cover letter templates
- Use LinkedIn post template
- Reference interview talking points

### 4. It won't be committed to Git
The file is in `.gitignore`, so it stays private on your machine.

## What's in the file?

### Section 1: Contact Information
Your personal details (name, email, phone, LinkedIn, GitHub)

### Section 2: Resume Bullet Points
6 ready-to-use bullet points for your resume:
```
• Designed and implemented comprehensive test strategy with 73 automated tests...
• Built CI/CD pipeline using GitHub Actions...
• Performed load and stress testing with 50+ concurrent users...
• Implemented dependency injection pattern...
• Discovered and fixed 3 bugs through systematic testing...
• Created comprehensive test documentation...
```

### Section 3: LinkedIn Post Template
Ready-to-post announcement for LinkedIn with hashtags

### Section 4: Cover Letter Template
Professional cover letter you can customize for each job

### Section 5: Email Template for Recruiters
Quick email template when reaching out to recruiters

### Section 6: Interview Preparation Notes
Prepared answers for common interview questions:
- "Tell me about yourself"
- "Tell me about a challenging bug"
- "How do you approach performance testing?"

### Section 7: Job Application Checklist
Step-by-step checklist for each application

### Section 8: Skills to Highlight
Tailored skill lists for different role types:
- SDET roles
- QA Engineer roles
- QA Lead roles

### Section 9: Salary Expectations
Space to research and note salary ranges

### Section 10: References
Template for 3 professional references

### Section 11: Personal Notes
Space for your own notes

## Quick Start Guide

### For your first job application:

1. **Open the file**
   ```bash
   open docs/PERSONAL_INFO.md
   # or
   code docs/PERSONAL_INFO.md
   ```

2. **Fill in your contact information** (Section 1)

3. **Customize resume bullet points** (Section 2)
   - Adjust numbers if needed
   - Add specific technologies you used
   - Match to job description

4. **Copy to your resume**
   - Select the bullet points
   - Paste into your resume
   - Format as needed

5. **Prepare cover letter** (Section 4)
   - Replace `[Company Name]` with actual company
   - Replace `[Job Title]` with actual position
   - Customize skills mentioned

6. **Post on LinkedIn** (Section 3)
   - Copy the template
   - Add your GitHub link
   - Post it!

## Tips

### ✅ Do:
- Keep this file updated with your latest achievements
- Customize for each job application
- Use it as a reference during interviews
- Update the "Last Updated" date

### ❌ Don't:
- Don't commit this file to Git (it's already in .gitignore)
- Don't share it publicly
- Don't use the same cover letter for every job
- Don't forget to update contact information

## Verification

To verify the file is properly ignored by Git:

```bash
# Check if file exists locally
ls -la docs/PERSONAL_INFO.md

# Verify it's not tracked by Git
git status docs/PERSONAL_INFO.md
# Should show: "nothing to commit, working tree clean"

# Verify it's in .gitignore
grep PERSONAL_INFO .gitignore
# Should show: "docs/PERSONAL_INFO.md"
```

## Backup

Since this file is not in Git, make sure to back it up:

1. **Cloud Storage**: Copy to Google Drive, Dropbox, etc.
2. **USB Drive**: Keep a copy on external storage
3. **Email**: Email yourself a copy
4. **Multiple Devices**: Copy to other computers you use

## Questions?

If you need to recreate the file, the template is available in the commit history before it was added to .gitignore.

---

**Created**: March 1, 2026
**Purpose**: Keep personal information private while sharing portfolio publicly
