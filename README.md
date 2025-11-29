# Product Manual Support

An AI-powered tool that automatically generates comprehensive, professional user manuals from product images, videos, audio recordings, or text descriptions.

## 🎯 What It Does

This application transforms raw product information into polished, structured user manuals—saving hours of technical writing work.

### Input Options

You can provide product information in any of these formats:

- **📸 Images**: Upload photos of your product from different angles
- **🎥 Videos**: Record or upload video demonstrations of your product
- **🎤 Audio**: Record verbal descriptions or explanations
- **📄 Files**: Upload existing documentation or PDFs
- **✍️ Text**: Type a description or topic

**Mix and match**: Combine multiple input types for more comprehensive manuals (e.g., product photos + verbal explanation).

### Output

The system generates a **professionally structured user manual** with:

- **Introduction/Overview**: High-level product description
- **Top 5 Features**: The most important features, automatically prioritized
- **Detailed Descriptions**: Clear explanations of how each feature works
- **Visual Schematics**: AI-generated diagrams for each feature (IKEA-style simple sketches)
- **Markdown Formatting**: Clean, readable structure ready for publishing

**Example output structure:**
```markdown
## Introduction
Overview of the product and its purpose...

## Feature Name
Detailed description of the feature...
- How it works
- How to use it
![schematic](/images/feature-diagram.png)
```

## ⏱️ Why This Saves Time

### Traditional Manual Creation
Creating a product manual traditionally involves:
1. **Research & Analysis** (2-4 hours): Examining the product, testing features
2. **Content Writing** (4-8 hours): Writing descriptions, instructions, and explanations
3. **Visual Creation** (2-4 hours): Creating diagrams, screenshots, or illustrations
4. **Formatting & Editing** (1-2 hours): Structuring content, proofreading
5. **Revisions** (1-3 hours): Multiple rounds of feedback and updates

**Total: 10-21 hours per manual**

### With This Tool
1. **Capture Product Info** (5-10 minutes): Take photos/videos or describe the product
2. **Generate Manual** (2-3 minutes): AI processes and creates the manual
3. **Review & Refine** (15-30 minutes): Quick review and minor edits if needed

**Total: ~30-45 minutes per manual**

### Time Savings
- **90-95% reduction in manual creation time**
- **Consistent quality**: Professional structure every time
- **No design skills needed**: Automatic diagram generation
- **Scalable**: Create manuals for multiple products quickly

## 🚀 Getting Started

### Prerequisites
- Docker
- Gemini API key ([Get one here](https://ai.google.dev/))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd product-manual-support
```

2. Create a `.env` file with your API key:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

3. Build and run with Docker:
```bash
docker build -t manual-generator .
docker run -p 8000:8000 -e PORT=8000 --env-file .env manual-generator
```

4. Open your browser to `http://localhost:8000`

## 💡 Usage Tips

### For Best Results

1. **Multiple Angles**: Provide photos from different perspectives
2. **Clear Descriptions**: If using text/audio, be specific about features
3. **Combine Inputs**: Mix photos with verbal explanations for richer context
4. **Good Lighting**: Ensure images/videos are well-lit and clear

### Example Use Cases

- **E-commerce**: Generate manuals for products in your catalog
- **Hardware Products**: Document physical devices and their features
- **Software Tools**: Create user guides from screenshots and descriptions
- **Training Materials**: Build instructional content quickly
- **Customer Support**: Provide comprehensive guides to reduce support tickets

## 🏗️ Architecture

### Frontend
- **React** with Vite
- Multi-modal input capture (camera, microphone, file upload)
- Real-time markdown rendering
- Responsive two-column layout for manual display

### Backend
- **FastAPI** for API endpoints
- **Pydantic AI** agents for intelligent processing
- **Google Gemini** models for:
  - Content analysis and extraction
  - Manual generation
  - Schematic creation

### AI Pipeline

1. **Input Agent**: Analyzes uploaded media and extracts product information
2. **Master Agent**: Structures information into a professional manual format
3. **Image Generation**: Creates simple, clear schematics for each feature

## 📝 Technical Details

### API Endpoints

- `POST /generate-manual`: Main endpoint for manual generation
  - Accepts: `FormData` with `topic` (string) and `files` (array)
  - Returns: JSON with `manual` (markdown string)

### Models Used

- `gemini-3-pro-preview`: Text analysis and generation
- `gemini-3-pro-image-preview`: Schematic generation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with Google Gemini AI and Pydantic AI framework.
