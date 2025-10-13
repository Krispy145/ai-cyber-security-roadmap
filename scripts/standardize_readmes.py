#!/usr/bin/env python3
"""
Standardize all repository README files using the secure-ai-api template structure.

This script:
1. Reads the manifest.json file to get repository information
2. Generates standardized README files for each repository
3. Uses the secure-ai-api README as the template structure
4. Populates content based on repository type and manifest data

Usage:
    python3 scripts/standardize_readmes.py [--dry-run] [--repo REPO_NAME]
    
Options:
    --dry-run    Show what would be changed without making changes
    --repo NAME  Only update a specific repository by name
"""

import json
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Repository name to workspace path mapping
REPO_PATHS = {
    "ml-foundations": "../ml-foundations",
    "phishing-classifier": "../phishing-classifier", 
    "secure-ai-api": "../secure-ai-api",
    "flutter-ai-chat-rag": "../flutter-ai-chat-rag",
    "flutter-iam-package": "../flutter-iam-package",
    "flutter-api-showcase": "../flutter-api-showcase",
    "react-phishing-dashboard": "../react-phishing-dashboard",
    "react-native-chat-rag": "../react-native-chat-rag",
    "react-native-api-showcase": "../react-native-api-showcase",
    "react-native-iam-package": "../react-native-iam-package",
    "ai-cyber-security-roadmap": "."  # This repo itself
}

def load_manifest() -> Dict:
    """Load and parse the manifest.json file."""
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        print("ERROR: manifest.json not found in current directory")
        sys.exit(1)
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse manifest.json: {e}")
        sys.exit(1)

def get_repo_milestones(manifest: Dict, repo_name: str) -> List[Dict]:
    """Get milestones for a specific repository."""
    milestones = manifest.get('milestones', [])
    return [m for m in milestones if m.get('repo') == repo_name]

def get_status_emoji(status: str) -> str:
    """Convert status to emoji representation."""
    status = (status or "").lower()
    if "active" in status or "done" in status:
        return "✅ Active"
    elif "scaffold" in status:
        return "🧩 Scaffolded"
    elif "planned" in status:
        return "⏳ Planned"
    elif "stub" in status:
        return "🔐 Stub"
    else:
        return status.title() or "—"

def format_date(date_str: str) -> str:
    """Format date string consistently."""
    if not date_str:
        return "—"
    try:
        if "/" in date_str:
            return datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return date_str

def get_architecture_overview(repo_name: str, repo_type: str) -> str:
    """Get architecture overview based on repository type."""
    if "flutter" in repo_name:
        return """```
lib/
 ├─ core/           # DI, error handling, networking
 ├─ data/           # DTOs, entities, sources, repositories
 ├─ features/       # feature modules (providers, pages, widgets)
 └─ presentation/   # app shell, router, theme
```

**Patterns used:**

- **Repository pattern** → clean separation between UI and data
- **Riverpod/GetIt** → reactive state management and dependency injection
- **dart_mappable** → type-safe data modeling
- **Dio** → HTTP client with interceptors and error handling"""
    
    elif "react" in repo_name:
        if "native" in repo_name:
            return """```
src/
 ├─ screens/        # React Native screens
 ├─ shared/         # API client, notifications, utilities
 └─ store/          # Zustand state management
```

**Patterns used:**

- **Zustand** → lightweight state management
- **Axios** → HTTP client with interceptors
- **Expo** → cross-platform development
- **SecureStore** → secure token storage"""
        else:
            return """```
src/
 ├─ pages/          # React pages/components
 ├─ shared/         # API client, utilities, types
 └─ store/          # Zustand state management
```

**Patterns used:**

- **React + TypeScript** → type-safe component development
- **Vite** → fast build tool and dev server
- **Zustand** → lightweight state management
- **Axios** → HTTP client with interceptors"""
    
    elif "ml-foundations" in repo_name:
        return """```
notebooks/          # Jupyter notebooks for experiments
 ├─ 01-linear-regression.ipynb
 ├─ 02-multiple-linear-regression.ipynb
 └─ 03-logistic-regression.ipynb
cheat-sheets/       # Quick reference guides
data/              # Local datasets (gitignored)
```

**Patterns used:**

- **Jupyter notebooks** → interactive data science workflow
- **NumPy/Pandas** → data manipulation and analysis
- **Scikit-learn** → machine learning algorithms
- **Matplotlib** → data visualization"""
    
    elif "phishing-classifier" in repo_name:
        return """```
src/
 ├─ data/           # load.py, preprocess.py
 ├─ models/         # train.py, evaluate.py
 └─ pipeline.py     # main execution script
```

**Patterns used:**

- **load.py** handles data ingestion and validation
- **preprocess.py** performs feature engineering and scaling
- **train.py** implements model training with cross-validation
- **evaluate.py** provides comprehensive model evaluation
- **pipeline.py** orchestrates the entire ML workflow"""
    
    elif "secure-ai-api" in repo_name:
        return """```
app/
 ├─ api/v1/         # router.py, phishing.py, rag.py
 ├─ core/           # config.py, security, middleware
 └─ main.py         # FastAPI application entry point
```

**Patterns used:**

- `api/v1/` contains versioned API endpoints
- `core/` handles configuration and security middleware
- `main.py` initializes the FastAPI application
- Docker configuration for containerized deployment
- GitHub Actions for automated CI/CD"""
    
    else:
        return """```
src/                # Source code
tests/              # Test files
docs/               # Documentation
```

**Patterns used:**

- Clean, modular code organization
- Comprehensive testing strategy
- Documentation-driven development"""

def get_highlights(repo_name: str, repo_data: Dict) -> List[str]:
    """Get highlights based on repository type and data."""
    highlights = []
    
    if "flutter" in repo_name:
        highlights.extend([
            "**Cross-platform** → Android, iOS, Web support",
            "**State Management** → Riverpod/GetIt for reactive updates",
            "**Dependency Injection** → Clean architecture with GetIt",
            "**Type Safety** → dart_mappable for data modeling",
            "**Networking** → Dio with interceptors and error handling",
            "**CI/CD** → GitHub Actions + Shorebird OTA updates",
            "**Testing** → Unit, widget, and golden tests"
        ])
    elif "react" in repo_name:
        if "native" in repo_name:
            highlights.extend([
                "**Cross-platform** → iOS and Android support",
                "**Expo** → Rapid development and deployment",
                "**State Management** → Zustand for lightweight state",
                "**Secure Storage** → SecureStore for tokens",
                "**HTTP Client** → Axios with interceptors",
                "**TypeScript** → Type-safe development"
            ])
        else:
            highlights.extend([
                "**React + TypeScript** → Type-safe component development",
                "**Vite** → Fast build tool and dev server",
                "**State Management** → Zustand for lightweight state",
                "**HTTP Client** → Axios with interceptors",
                "**Modern Tooling** → ESLint, Prettier, TypeScript"
            ])
    elif "ml-foundations" in repo_name:
        highlights.extend([
            "**Hands-on Learning** → Interactive Jupyter notebooks",
            "**Core Algorithms** → Linear regression, logistic regression",
            "**Data Visualization** → Matplotlib and Seaborn plots",
            "**Real Datasets** → Practical examples with real data",
            "**Cheat Sheets** → Quick reference guides",
            "**Progressive Learning** → Step-by-step complexity"
        ])
    elif "phishing-classifier" in repo_name:
        highlights.extend([
            "**Dataset** → UCI Phishing Websites Dataset with 11,055 samples",
            "**Features** → 30 engineered features (URL length, domain age, suspicious patterns)",
            "**Models** → Multiple baseline algorithms (Logistic Regression, Random Forest, SVM)",
            "**Evaluation** → Comprehensive metrics (accuracy, precision, recall, F1-score)",
            "**Pipeline** → End-to-end ML workflow from EDA to model export",
            "**Export** → Pickle serialization for API integration"
        ])
    elif "secure-ai-api" in repo_name:
        highlights.extend([
            "**AI Endpoints** → Phishing detection and RAG (Retrieval-Augmented Generation)",
            "**Authentication** → OAuth2/JWT with secure token handling",
            "**Security** → Rate limiting, input validation, and CORS protection",
            "**Infrastructure** → Docker containerization and CI/CD pipelines",
            "**Monitoring** → Health checks, logging, and performance metrics",
            "**Documentation** → Auto-generated OpenAPI/Swagger docs"
        ])
    elif "ai-cyber-security-roadmap" in repo_name:
        highlights.extend([
            "**📊 Centralized Progress Tracking** → Single manifest.json file managing 11 repositories across ML, backend, Flutter, React, and React Native",
            "**🔄 Automated Synchronization** → Pre/post-commit hooks automatically update READMEs and sync changes across all repositories",
            "**📈 Real-time Progress Visualization** → Live progress percentages and milestone tracking with completion dates",
            "**🎯 Multi-Platform Portfolio** → Coordinated development across 5 technology stacks with consistent documentation",
            "**⚡ GitHub Integration** → Automated repository description and topic updates via GitHub API",
            "**📋 Comprehensive Milestone Management** → 50+ tracked milestones with status, due dates, and completion tracking",
            "**🔧 Developer Experience** → Makefile automation, validation scripts, and standardized README generation",
            "**📚 Educational Focus** → ML foundations progression from linear regression through advanced topics",
            "**🛡️ Security Preparation** → Integrated CompTIA Security+ certification roadmap",
            "**🎨 Visual Consistency** → Automated cover image and thumbnail management across all repositories"
        ])
    else:
        # Generic highlights based on topics
        topics = repo_data.get('topics', [])
        if 'machine-learning' in topics:
            highlights.append("**Machine Learning** → ML algorithms and data science")
        if 'flutter' in topics:
            highlights.append("**Flutter** → Cross-platform mobile development")
        if 'react' in topics:
            highlights.append("**React** → Modern web development")
        if 'api' in topics:
            highlights.append("**API Development** → RESTful API design")
        if 'security' in topics:
            highlights.append("**Security** → Authentication and authorization")
    
    return highlights

def get_what_it_demonstrates(repo_name: str, repo_data: Dict) -> List[str]:
    """Get what the repository demonstrates."""
    if "flutter" in repo_name:
        return [
            "Cross-platform mobile app development with Flutter",
            "Clean architecture patterns and state management",
            "API integration and data persistence",
            "Modern Flutter development practices and tooling"
        ]
    elif "react" in repo_name:
        if "native" in repo_name:
            return [
                "Cross-platform mobile development with React Native",
                "State management and API integration patterns",
                "Secure token storage and authentication flows",
                "Modern React Native development practices"
            ]
        else:
            return [
                "Modern React development with TypeScript",
                "State management and API integration patterns",
                "Component-based architecture and reusability",
                "Modern web development tooling and practices"
            ]
    elif "ml-foundations" in repo_name:
        return [
            "Machine learning fundamentals and algorithms",
            "Data science workflow and best practices",
            "Interactive learning with Jupyter notebooks",
            "Practical application of ML concepts"
        ]
    elif "phishing-classifier" in repo_name:
        return [
            "End-to-end machine learning project structure",
            "Feature engineering and data preprocessing techniques",
            "Model training, evaluation, and comparison",
            "Production-ready model export and serialization"
        ]
    elif "secure-ai-api" in repo_name:
        return [
            "Production-ready FastAPI application structure",
            "Secure API design with authentication and authorization",
            "AI/ML model integration and inference endpoints",
            "Containerization and deployment best practices"
        ]
    else:
        return [
            "Clean, maintainable code architecture",
            "Best practices for the specific technology stack",
            "Comprehensive testing and documentation",
            "Production-ready development patterns"
        ]

def get_getting_started(repo_name: str, repo_data: Dict) -> str:
    """Get getting started instructions based on repository type."""
    if "flutter" in repo_name:
        return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
flutter pub get
```

**Run (Dev):**
```bash
flutter run --flavor dev
```

**Run (Prod):**
```bash
flutter run --flavor prod
```

**Codegen:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```""".format(repo_name=repo_name)
    
    elif "react" in repo_name:
        if "native" in repo_name:
            return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
npm install
```

**Run:**
```bash
npm start
```

**iOS:**
```bash
npx expo run:ios
```

**Android:**
```bash
npx expo run:android
```""".format(repo_name=repo_name)
        else:
            return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
npm install
```

**Run:**
```bash
npm run dev
```

**Build:**
```bash
npm run build
```""".format(repo_name=repo_name)
    
    elif "ml-foundations" in repo_name:
        return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook
```""".format(repo_name=repo_name)
    
    elif "phishing-classifier" in repo_name:
        return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
pip install -r requirements.txt
```

**Run the full pipeline:**
```bash
python src/pipeline.py
```

**Train specific models:**
```bash
python src/models/train.py --model logistic_regression
python src/models/train.py --model random_forest
```""".format(repo_name=repo_name)
    
    elif "secure-ai-api" in repo_name:
        return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
pip install -r requirements.txt
```

**Run locally:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Run with Docker:**
```bash
docker-compose up --build
```

**API Documentation:**
Visit `http://localhost:8000/docs` for interactive API documentation.""".format(repo_name=repo_name)
    
    else:
        return """```bash
git clone https://github.com/Krispy145/{repo_name}.git
cd {repo_name}
# Follow specific setup instructions in the repository
```""".format(repo_name=repo_name)

def get_testing_instructions(repo_name: str) -> str:
    """Get testing instructions based on repository type."""
    if "flutter" in repo_name:
        return """```bash
flutter test --coverage
```

- Unit → repositories, services
- Widget → UI components and interactions
- Golden → visual regression tests"""
    
    elif "react" in repo_name:
        if "native" in repo_name:
            return """```bash
npm test
```

- Unit → components and utilities
- Integration → API interactions
- E2E → user flows"""
        else:
            return """```bash
npm test
```

- Unit → components and utilities
- Integration → API interactions
- E2E → user flows"""
    
    elif "ml-foundations" in repo_name:
        return """```bash
# Run notebook tests
jupyter nbconvert --execute --to notebook notebooks/*.ipynb
```

- Notebook execution → verify all cells run successfully
- Data validation → check data loading and processing
- Visualization → ensure plots render correctly"""
    
    elif "phishing-classifier" in repo_name:
        return """```bash
python -m pytest tests/
```

- Unit tests → Data loading and preprocessing functions
- Integration tests → Full pipeline execution
- Model tests → Training and evaluation workflows"""
    
    elif "secure-ai-api" in repo_name:
        return """```bash
pytest tests/ --cov=app --cov-report=html
```

- Unit tests → API endpoints and business logic
- Integration tests → Database and external service interactions
- Security tests → Authentication and authorization flows
- Performance tests → Load testing and rate limiting"""
    
    else:
        return """```bash
# Run appropriate test command for the technology stack
```

- Unit tests → Individual component testing
- Integration tests → End-to-end functionality
- Security tests → Authentication and authorization"""

def generate_readme_content(repo_data: Dict, manifest: Dict) -> str:
    """Generate standardized README content for a repository."""
    repo_name = repo_data.get('name', '')
    description = repo_data.get('short_description', '')
    status = repo_data.get('status', '')
    target = repo_data.get('target', '')
    topics = repo_data.get('topics', [])
    
    # Get milestones for this repo
    milestones = get_repo_milestones(manifest, repo_name)
    
    # Generate content sections
    highlights = get_highlights(repo_name, repo_data)
    what_demonstrates = get_what_it_demonstrates(repo_name, repo_data)
    architecture = get_architecture_overview(repo_name, '')
    getting_started = get_getting_started(repo_name, repo_data)
    testing = get_testing_instructions(repo_name)
    
    # Generate roadmap table
    roadmap_table = ""
    if milestones:
        roadmap_table = "| Milestone                    | Category              | Target Date | Status     |\n"
        roadmap_table += "| ---------------------------- | --------------------- | ----------- | ---------- |\n"
        for milestone in milestones:
            title = milestone.get('title', '')
            category = milestone.get('category', '')
            due = format_date(milestone.get('due', ''))
            status_icon = "✅ Done" if milestone.get('status') == 'done' else "⏳ In Progress" if milestone.get('status') == 'in_progress' else "⏳ Planned"
            roadmap_table += f"| {title} | {category} | {due} | {status_icon} |\n"
    
    # Generate README content
    readme = f"""# {repo_name.replace('-', ' ').replace('_', ' ').title()}

{description}

---

## 📈 Status

- **Status:** {status.lower()} ({get_status_emoji(status).split()[1] if ' ' in get_status_emoji(status) else get_status_emoji(status)})
- **Focus:** {description}
- **Last updated:** {format_date(manifest.get('updated', ''))}
- **Target completion:** {format_date(target)}

---

## 🔑 Highlights

{chr(10).join(f"- {highlight}" for highlight in highlights)}

---

## 🏗 Architecture Overview

{architecture}

---

## 📱 What It Demonstrates

{chr(10).join(f"- {item}" for item in what_demonstrates)}

---

## 🚀 Getting Started

{getting_started}

---

## 🧪 Testing

{testing}

---

## 🔒 Security & Next Steps

- Follow security best practices for the technology stack
- Implement proper authentication and authorization
- Add comprehensive error handling and validation
- Set up monitoring and logging

---

## 🗓 Roadmap

{roadmap_table}

---

## 📄 License

MIT © Krispy145"""
    
    return readme

def update_repo_readme(repo_name: str, repo_data: Dict, manifest: Dict, dry_run: bool = False) -> bool:
    """Update README for a specific repository."""
    if repo_name not in REPO_PATHS:
        print(f"WARNING: No path mapping for repository '{repo_name}', skipping")
        return False
    
    repo_path = Path(REPO_PATHS[repo_name])
    readme_path = repo_path / "README.md"
    
    if not repo_path.exists():
        print(f"WARNING: Repository path not found: {repo_path}")
        return False
    
    # Generate new README content
    new_content = generate_readme_content(repo_data, manifest)
    
    if dry_run:
        print(f"WOULD UPDATE {readme_path}:")
        print(f"  Content length: {len(new_content)} characters")
        return True
    
    try:
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Updated {readme_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {readme_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Standardize repository READMEs')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--repo', type=str, 
                       help='Only update a specific repository by name')
    
    args = parser.parse_args()
    
    # Load manifest
    manifest = load_manifest()
    repositories = manifest.get('repositories', [])
    
    if not repositories:
        print("ERROR: No repositories found in manifest")
        sys.exit(1)
    
    # Filter repositories if specific repo requested
    if args.repo:
        repositories = [r for r in repositories if r.get('name') == args.repo]
        if not repositories:
            print(f"ERROR: Repository '{args.repo}' not found in manifest")
            sys.exit(1)
    
    # Process each repository
    updated_count = 0
    total_count = len(repositories)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Standardizing READMEs for {total_count} repositories...")
    print()
    
    for repo in repositories:
        repo_name = repo.get('name')
        if not repo_name:
            print(f"WARNING: Repository missing name, skipping")
            continue
        
        was_updated = update_repo_readme(repo_name, repo, manifest, args.dry_run)
        if was_updated:
            updated_count += 1
    
    print()
    if args.dry_run:
        print(f"DRY RUN COMPLETE: Would update {updated_count}/{total_count} repositories")
    else:
        print(f"✅ COMPLETE: Updated {updated_count}/{total_count} repositories")

if __name__ == "__main__":
    main()
