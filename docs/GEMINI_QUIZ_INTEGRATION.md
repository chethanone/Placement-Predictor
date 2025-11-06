# Google Gemini AI Quiz Generation Integration

## Overview
Successfully integrated Google Gemini AI to automatically generate 25 diverse quiz questions from uploaded PDF/PPT files.

## API Configuration
- **API Key**: Set in environment variables (`.env` file)
- **Model**: gemini-2.0-flash (Latest fast model)
- **Location**: `predictor/views.py` (lines 13-16)

**To set up:**
1. Get your API key from: https://makersuite.google.com/app/apikey
2. Add to `.env` file: `GEMINI_API_KEY=your-api-key-here`

## Features

### 1. **AI-Powered Question Generation**
- Analyzes content from PDF/PPT files
- Generates **exactly 25 questions** per upload
- Uses advanced natural language understanding

### 2. **Diverse Question Types**
The system generates 5 different types of questions:

| Type | Count | Description |
|------|-------|-------------|
| **Multiple Choice (MCQ)** | 10+ | 4 options with 1 correct answer |
| **Fill in the Blanks** | 5+ | Complete missing words/phrases |
| **True/False** | 3+ | Statement verification |
| **Short Answer** | 5+ | Brief explanatory responses |
| **Definition/Explanation** | 2+ | Detailed concept explanations |

### 3. **Smart Content Processing**
- Extracts text from **PDF** files (PyMuPDF + PyPDF2)
- Extracts text from **PPT/PPTX** files (python-pptx)
- Handles up to 8000 characters of content per request
- Automatic fallback if AI generation fails

## Technical Implementation

### Updated Models (`predictor/models.py`)
```python
class QuizQuestion(models.Model):
QUESTION_TYPES = [
('mcq', 'Multiple Choice'),
('tf', 'True/False'),
('fill_blank', 'Fill in the Blank'),
('short_answer', 'Short Answer'),
('true_false', 'True/False'),
('text', 'Text'),
]

question_type = models.CharField(max_length=20, ...)
correct_answer = models.TextField() # Supports longer answers
student_answer = models.TextField()
options = models.TextField() # JSON field for flexible options
```

### AI Generation Function (`predictor/views.py`)
```python
def generate_questions_from_text(text, max_questions=25):
"""Generate 25 diverse quiz questions using Google Gemini AI."""
- Uses Gemini 1.5 Flash model
- Structured prompt for consistent output
- JSON response parsing
- Automatic fallback to basic generation
```

## Question Format Examples

### Multiple Choice Question
```json
{
"question_number": 1,
"question_text": "What is the primary purpose of a compiler?",
"question_type": "mcq",
"options": [
"To execute code line by line",
"To convert source code to machine code",
"To debug programs",
"To format code"
],
"correct_answer": "To convert source code to machine code",
"explanation": "Compilers translate high-level code to machine code"
}
```

### Fill in the Blank
```json
{
"question_number": 2,
"question_text": "_____ is a high-level programming language.",
"question_type": "fill_blank",
"correct_answer": "Python",
"explanation": "Python is one of many high-level languages"
}
```

### True/False
```json
{
"question_number": 3,
"question_text": "Python is a compiled language.",
"question_type": "true_false",
"correct_answer": "False",
"explanation": "Python is an interpreted language"
}
```

## Workflow

1. **Upload**: Student uploads PDF/PPT file with syllabus content
2. **Extract**: System extracts text using PyMuPDF/python-pptx
3. **AI Generate**: Gemini AI analyzes content and creates 25 questions
4. **Store**: Questions saved to database with metadata
5. **Display**: Student takes quiz with diverse question types
6. **Evaluate**: Automatic grading and score calculation

## Error Handling

- **Primary**: Google Gemini AI generation
- **Fallback**: Basic rule-based question generation
- **File Processing**: Multiple libraries with failover
- **Validation**: Ensures exactly 25 questions generated

## Dependencies

```
google-generativeai==0.8.5
PyMuPDF==1.26.5
python-pptx==1.0.2
PyPDF2==3.0.1
```

## Usage

### For Students
1. Navigate to: http://127.0.0.1:8000/student/quiz/
2. Upload PDF/PPT file containing study material
3. Wait for AI to generate questions (5-15 seconds)
4. Take the quiz with 25 diverse questions
5. Submit and view results

### For Developers
```python
# In views.py
from predictor.views import generate_questions_from_text

# Extract text from file
text = process_uploaded_file(file_path)

# Generate questions
questions = generate_questions_from_text(text, max_questions=25)

# Each question contains:
# - question_text
# - correct_answer
# - question_type
# - options (for MCQ)
```

## Benefits

**Automated**: No manual question creation needed
**Diverse**: 5 different question types
**Intelligent**: AI understands context and concepts
**Scalable**: Handles any subject/topic
**Consistent**: Always generates 25 questions
**Random**: Each generation creates unique questions
**Educational**: Tests understanding, not just memorization

## Security Notes

- API key is hardcoded (for demo purposes)
- **Production**: Move to environment variables
- **Recommendation**: Use `.env` file with `python-dotenv`

```python
# Recommended for production:
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
```

## Database Migration

Migration applied: `0002_quizquestion_options_and_more.py`

Changes:
- Added `options` field (TextField)
- Changed `correct_answer` to TextField
- Changed `student_answer` to TextField
- Extended `question_type` choices
- Increased `question_type` max_length to 20

## Testing

To test the integration:

1. **Start Server**:
```bash
.\.venv\Scripts\python.exe manage.py runserver
```

2. **Access Quiz Upload**:
- URL: http://127.0.0.1:8000/student/quiz/
- Upload a PDF or PPT file
- Wait for questions to generate

3. **Verify**:
- Check for 25 questions
- Verify diverse question types
- Confirm correct answers are stored

## Example Output

When you upload a PDF about "Python Programming":

- **MCQ Questions**: About syntax, concepts, features
- **Fill Blanks**: Key terminology and definitions
- **True/False**: Common misconceptions
- **Short Answer**: Explain concepts in your words
- **Definitions**: Define technical terms

All questions are contextually relevant to the uploaded content!

---

**Status**: **FULLY INTEGRATED & WORKING**

**Last Updated**: November 3, 2025
