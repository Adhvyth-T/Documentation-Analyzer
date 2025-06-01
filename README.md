# AI-Powered Documentation Improvement Agent

An intelligent documentation analyzer that evaluates MoEngage documentation articles and provides actionable improvement suggestions using advanced AI techniques and modern web technologies.

## 🚀 Features

- **Comprehensive Analysis**: Evaluates documentation across 4 key criteria:
  - **Readability** for non-technical marketers
  - **Structure & Flow** assessment
  - **Completeness** of information and examples
  - **Style Guidelines** compliance (Microsoft Style Guide principles)

- **Advanced Web Scraping**: Uses Playwright for robust extraction of JavaScript-rendered content
- **AI-Powered Insights**: Leverages Large Language Models via OpenRouter API for intelligent analysis
- **Vector-Based Processing**: Employs FAISS and embeddings for context-aware content analysis
- **Multiple Output Formats**: Generates both JSON and HTML reports with timestamps

## 🏗️ Architecture

```
URL Input → Playwright Scraping → Text Chunking → Vector Store → AI Analysis → Structured Reports
```

### Key Components:
- **Content Extraction**: Playwright with headless Chrome for dynamic content
- **Document Processing**: LangChain with RecursiveCharacterTextSplitter
- **Vector Search**: FAISS with HuggingFace embeddings for relevant chunk selection
- **AI Analysis**: OpenRouter API integration with flexible model support
- **Report Generation**: Multi-format output with professional styling

## 📋 Requirements

- Python 3.8+
- OpenRouter API key
- Chrome/Chromium browser (for Playwright)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd documentation-analyzer
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers:**
```bash
playwright install chromium
```

4. **Set up environment variables:**
Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
DEFAULT_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
```

## 🚀 Usage

### Basic Usage

```python
from main import DocumentationAnalyzer

# Initialize analyzer
analyzer = DocumentationAnalyzer()

# Analyze a MoEngage documentation URL
url = "https://help.moengage.com/hc/en-us/articles/360035738832-Explore-the-Number-of-Notifications-Received-by-Users"
report = analyzer.analyze(url)

print(f"Analysis Status: {report['status']}")
```

### Running the Example

```bash
python main.py
```

This will display a Tkinter window that accepts a documentation URL as text and analyze a sample MoEngage documentation article and generate reports in the `output/` directory.
Upon completion, a success window is displayed.
## 📊 Output Examples

### JSON Report Structure
```json
{
    "status": "success",
    "url": "https://help.moengage.com/hc/en-us/articles/...",
    "analysis_type": "all",
    "results": {
        "readability": [...],
        "structure": [...],
        "completeness": [...],
        "style": [...]
    }
}
```

### Generated Files
- `output/report_YYYYMMDD_HHMMSS.json` - Machine-readable analysis results
- `output/report_YYYYMMDD_HHMMSS.html` - Human-friendly formatted report

## 🔧 Technical Challenges Solved

### 1. Dynamic Content Extraction
**Challenge**: MoEngage documentation uses JavaScript rendering, making standard HTTP requests insufficient.

**Solution**: Implemented Playwright with proper wait states for network idle and complete content loading.

### 2. Large Document Processing
**Challenge**: Documentation articles exceed LLM context limits.

**Solution**: Developed intelligent chunking with FAISS vector search to analyze only relevant sections for each criterion.

### 3. Inconsistent LLM Responses
**Challenge**: AI responses vary in format and may include markdown formatting.

**Solution**: Created robust JSON extraction that handles code blocks and malformed responses gracefully.

### 4. Multi-Criteria Analysis Coordination
**Challenge**: Efficiently performing different analysis types on the same document.

**Solution**: Designed a mapping system coordinating analysis functions with targeted vector queries.

## 🏛️ Design Choices & Approach

### Web Scraping Strategy
- **Playwright over Selenium**: Better performance and modern async/await support
- **Headless browsing**: Handles JavaScript-heavy documentation sites effectively
- **UTF-8 encoding**: Ensures proper handling of special characters

### AI Integration Approach
- **OpenRouter API**: Access to multiple LLM providers and models
- **Context-aware prompting**: Tailored prompts for each analysis criterion
- **Structured output parsing**: Robust JSON extraction from varied AI responses

### Analysis Methodology
- **Hybrid readability assessment**: Combines Flesch-Kincaid scoring with qualitative AI analysis
- **Vector similarity search**: Identifies relevant content sections for targeted analysis
- **Microsoft Style Guide focus**: Emphasizes clarity, conciseness, and action-oriented language

## 📁 Project Structure

```
documentation-analyzer/
├──Analyzer/
      ├── main.py              # Main application and DocumentationAnalyzer class
      └──utils.py             # Core utility functions and analysis logic
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── output/             # Generated reports directory
├── README.md           # This file
└──.env.example
```

## 🔄 Task Implementation Status

### ✅ Task 1: Documentation Analyzer Agent - **COMPLETED**
- Fully functional agent analyzing MoEngage documentation URLs
- Implements all 4 required analysis criteria
- Generates structured, actionable improvement suggestions
- Provides comprehensive reporting in multiple formats

### ❌ Task 2: Documentation Revision Agent - **NOT IMPLEMENTED**
- The bonus task for automatic document revision was not attempted
- This was an optional enhancement task

## 🔍 Example Analysis Output

Here are sample analyses from two different MoEngage documentation articles:

### Sample 1: Notification Analytics Article
- **Readability Issues**: Identified 3 sentences exceeding recommended length for marketers
- **Structure Improvements**: Suggested adding numbered steps for complex procedures
- **Completeness Gaps**: Recommended adding visual examples for dashboard navigation
- **Style Issues**: Found 2 instances of passive voice needing conversion

### Sample 2: Campaign Setup Guide  
- **Readability Score**: Flesch-Kincaid grade 8.2 (appropriate for target audience)
- **Structure Strength**: Well-organized with clear headings and bullet points
- **Example Quality**: Good use of screenshots but missing code examples
- **Style Compliance**: Mostly action-oriented with minor jargon simplification needed

## 🛡️ Error Handling

The system includes comprehensive error handling for:
- Invalid or unreachable URLs
- API rate limits and network timeouts
- Malformed content extraction
- JSON parsing failures
- File system operations

## 🔮 Future Enhancements

- Implementation of Task 2 (automatic document revision)
- Support for batch processing multiple URLs
- Integration with additional style guides
- Real-time analysis via web interface
- Advanced caching for improved performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenRouter for AI model access
- Playwright team for excellent web automation tools
- LangChain community for document processing capabilities
- MoEngage for providing comprehensive documentation to analyze
