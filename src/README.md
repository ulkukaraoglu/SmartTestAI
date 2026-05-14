# SmartTestAI Web UI

Upload code files through a simple web interface and analyze them with **Snyk Code** and **DeepSource**.

## Features

- **File upload**: Drag and drop or click to select files
- **Dual scan**: Runs both Snyk Code and DeepSource automatically
- **Detailed results**: Side-by-side metrics
- **Advanced metrics**: Precision, recall, and F1 when ground truth is available
- **Live status**: Scan progress and results on the same page

## Setup

### Start the backend (Web UI is served from the same app)

```bash
cd backend
pip install flask flask-cors
python app.py
```

When the backend is running:

- **Web UI**: `http://localhost:5001`
- **API**: same origin, e.g. `http://localhost:5001/projects`

Open **`http://localhost:5001`** in your browser. You do not need a separate static file server.

## Usage

1. **Upload files** on the home page (drag and drop or click).
2. Click **Start scan**.
3. Review results for each tool.
4. Click **Show details** for advanced metrics in the modal.

## Supported file types

- Python: `.py`
- JavaScript: `.js`
- Java: `.java`
- C/C++: `.cpp`, `.c`
- Go: `.go`
- Rust: `.rs`
- Text: `.txt`
- Archives: `.zip`

## API endpoints used by the UI

- `POST /upload` — file upload
- `POST /scan/code` — Snyk Code scan
- `POST /scan/deepsource` — DeepSource scan

## Troubleshooting

### CORS errors

1. Ensure `flask-cors` is installed on the backend.
2. Ensure the backend listens on `http://localhost:5001`.
3. Open the UI via that URL (not as a raw `file://` page if your browser blocks requests).

### Cannot reach the backend

- Check `http://localhost:5001/projects`.
- The UI uses `window.location.origin` as `API_BASE_URL` in `app.js`.

### Upload failures

- Check file size (rough guideline: under ~10MB depending on server limits).
- Confirm the file extension is allowed.
- Check backend logs.

## Development

The UI consists of:

- `index.html` — structure
- `style.css` — layout and styling
- `app.js` — behavior and API calls

Edit these files to change the interface.
