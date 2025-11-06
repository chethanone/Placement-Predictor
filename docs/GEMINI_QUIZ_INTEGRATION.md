# Google Gemini AI Quiz Integration

## Overview

This application uses Google Gemini AI to automatically generate quiz questions from uploaded PDF and PowerPoint files.

## Configuration

### API Setup

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to your `.env` file:
   ```env
   GEMINI_API_KEY=your-api-key-here
   ```
3. Restart the Django server

## Features

### Question Generation
- Analyzes content from PDF and PowerPoint files
- Generates 25 questions per upload
- Supports multiple question types

### Question Types

| Type | Description |
|------|-------------|
| Multiple Choice | 4 options with 1 correct answer |
| True/False | Statement verification |
| Fill in the Blank | Complete missing words/phrases |
| Short Answer | Brief explanatory responses |

### File Support
- PDF files (text extraction via PyMuPDF and PyPDF2)
- PowerPoint files (PPT/PPTX via python-pptx)
- Maximum 8000 characters per request

## Implementation

The integration is implemented in `predictor/views.py` using the function `generate_questions_from_text()`.

### Required Dependencies

```txt
google-generativeai==0.8.5
PyMuPDF==1.26.5
python-pptx==1.0.2
PyPDF2==3.0.1
```

## Usage

### Student Workflow
1. Navigate to quiz upload page
2. Upload PDF or PowerPoint file
3. Wait 5-15 seconds for AI generation
4. Take the quiz with generated questions
5. Submit and view results

### API Limits
- Maximum content length: 8000 characters
- Questions per quiz: 25
- Automatic fallback to basic generation if API fails

## Security

- API key stored in environment variables
- Never commit `.env` file to version control
- Production deployments should use secret management services
