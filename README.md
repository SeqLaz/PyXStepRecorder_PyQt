# 📸 PyXStepRecorder Desktop Application

This repository contains the **PyQt6 Desktop Graphical User Interface (GUI)** for [PyXStepRecorder](https://github.com/SeqLaz/PyXStepRecorder). It provides an intuitive layout allowing users to visually configure output directories, handle lossless quality adjustments, and toggle recording actions smoothly with integrated background logging pipelines.

---

## 🏗️ Workspace Architecture

The core logic package sits inside the `PyXStepRecorder` directory, while the desktop panel application resides in `PyXStepRecorder_PyQt`.

```text
. (Workspace Root)
├── .gitignore
├── .gitmodules
├── .pre-commit-config.yaml
├── PyXStepRecorder/          # Core CLI/Package Engine (Git Submodule)
└── PyXStepRecorder_PyQt/     # Desktop Interface Client (main.py, layouts)

```

---

## 🛠️ Prerequisites

* **Python 3.9+**
* An active installation of either standard **pip** or **uv**.

---

## 🚀 Getting Started

### 1. Clone the Repository (with Submodules)

Because this project relies on a submodule, you must clone the repository recursively to fetch both the app code and the core engine:

```bash
git clone --recursive https://github.com/SeqLaz/PyXStepRecorder_PyQt.git
cd PyXStepRecorder_PyQt

```

*If you already cloned the repository without the recursive flag, fetch the missing engine components by running:*

```bash
git submodule update --init --recursive

```

### 2. Environment Provisioning & Installation

Set up a unified virtual environment at the root of the workspace to bind both development modules together seamlessly.

#### Option A: Using `uv` (Recommended / Ultra-Fast)

```bash
# Create and activate the virtual environment
uv venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1

# Install app dependencies and development hooks
uv pip install PyQt6 pre-commit ruff

# Mount the core recorder engine in local editable mode
uv pip install -e ./PyXStepRecorder

```

#### Option B: Using Standard `pip`

```bash
# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1

# Install app dependencies and development hooks
pip install PyQt6 pre-commit ruff

# Mount the core recorder engine in local editable mode
pip install -e ./PyXStepRecorder

```

---

## 💻 Local Launch & Development

Once dependencies are linked inside your virtual environment, change directories to the application folder and launch the interface script:

```bash
cd PyXStepRecorder_PyQt
python main.py

```

### 🛡️ Code Quality & Pre-commit Hooks

This workspace uses `ruff` for ultra-fast linting and code formatting, automated locally via `pre-commit`.

To activate the automated code validation hooks right inside your local Git workflow, run the following command from the **root directory**:

```bash
pre-commit install

```

You can test or manually run formatting validation across all project files at any time by executing:

```bash
pre-commit run --all-files

```

---

## 📦 Bundling as a Standalone Program (PyInstaller)

If you need to compile this script into a completely standalone single-file binary for distribution, ensure `pyinstaller` is inside your environment and compile using your respective OS layout flags:

#### 🪟 Windows Compilation

```bash
pyinstaller --onefile --windowed --add-data "main_window.ui;." --collect-data py_xsr main.py

```

#### 🐧 Linux Compilation

```bash
pyinstaller --onefile --windowed --add-data "main_window.ui:." --collect-data py_xsr main.py

```

The finished executable file will drop inside the newly generated `dist/` directory.

---

## 📄 License

This workspace is distributed under the MIT License. See `LICENSE` inside individual repositories for further information.
