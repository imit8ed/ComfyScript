# XYZ Plot Studio

**Systematic Hyperparameter Exploration for ComfyUI**

A powerful, self-contained web application that enables systematic exploration of hyperparameter spaces in ComfyUI using ComfyScript. Think "W&B for ComfyUI" - making experimentation reproducible, visual, and collaborative.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)

---

## 🎯 **Features**

### Core Capabilities
- **3D Parameter Sweeps**: Define X, Y, and Z axes with numeric or categorical parameters
- **Enum-Powered UI**: Auto-populated dropdowns from ComfyScript enums (Samplers, Schedulers, Models)
- **Real-time Generation**: Watch your XYZ plot generate with live progress updates
- **Interactive Z-Axis Scrubber**: Navigate through Z-axis values with keyboard shortcuts
- **W&B Integration**: Automatically log experiments to Weights & Biases
- **ComfyScript Code Generation**: View and edit generated ComfyScript code
- **Comprehensive Testing**: 50+ backend tests ensuring reliability

### Key Features
✅ **Smart Parameter Controls** - Range sliders for numeric params, multi-select for enums
✅ **Template System** - Quick-start with txt2img, img2img, hires fix workflows
✅ **Progress Tracking** - WebSocket real-time updates during generation
✅ **Batch Execution** - Queue multiple experiments
✅ **Export Options** - Save as image grid, PDF report, or JSON
✅ **Docker Deployment** - One-command setup with docker-compose

---

## 🚀 **Quick Start**

### Prerequisites
- Docker and Docker Compose
- NVIDIA GPU with CUDA support (for ComfyUI)
- 8GB+ VRAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xyz-plot-studio
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ComfyUI: http://localhost:8188

That's it! The application will automatically:
- Start the backend FastAPI server
- Start the frontend React app
- Launch ComfyUI with GPU support
- Initialize Redis for task queuing

---

## 📖 **Usage**

### Creating Your First XYZ Plot

1. **Open the Experiment Builder** at http://localhost:3000

2. **Define Your Parameter Grid**:
   - **X-Axis**: CFG Scale (4.0 → 12.0, step 2.0)
   - **Y-Axis**: Steps (15 → 30, step 5)
   - **Z-Axis**: Sampler (euler, dpmpp_2m, uni_pc)

3. **Configure Workflow**:
   - Select your checkpoint
   - Enter your prompt and negative prompt
   - Set image dimensions (512x512)
   - Choose a seed

4. **Review and Launch**:
   - Check total combinations (e.g., 5 × 4 × 3 = 60 images)
   - Click "Create and Start Experiment"

5. **Monitor Progress**:
   - Watch real-time generation in the experiment view
   - Use the Z-axis scrubber to navigate results
   - Export when complete

### Example: Finding Optimal CFG and Steps

```python
# This is automatically generated for you!
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

with Workflow():
    model, clip, vae = CheckpointLoaderSimple('v1-5-pruned-emaonly.safetensors')

    for sampler in ['euler', 'dpmpp_2m', 'uni_pc']:
        for steps in [15, 20, 25, 30]:
            for cfg in [4.0, 6.0, 8.0, 10.0, 12.0]:
                latent = EmptyLatentImage(512, 512, 1)
                latent = KSampler(model, seed=42, steps=steps, cfg=cfg,
                                 sampler_name=sampler, ...)
                image = VAEDecode(latent, vae)
                SaveImage(image, f'{cfg}_{steps}_{sampler}')
```

---

## 🏗️ **Architecture**

### Stack Overview

**Backend:**
- FastAPI (Python 3.9+)
- ComfyScript for workflow execution
- SQLAlchemy for persistence
- Celery + Redis for async tasks
- W&B for experiment tracking

**Frontend:**
- React 18 with TypeScript
- Vite for fast dev/build
- Tailwind CSS for styling
- Zustand for state management
- WebSockets for real-time updates

**Infrastructure:**
- Docker + Docker Compose
- Nginx reverse proxy
- PostgreSQL (optional, SQLite default)

### Directory Structure

```
xyz-plot-studio/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── core/          # Configuration
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── main.py        # App entry point
│   ├── tests/             # Pytest tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docs/                  # Documentation
├── docker-compose.yml
└── README.md
```

---

## 🧪 **Testing**

### Backend Tests

Run the comprehensive test suite:

```bash
cd backend
pytest tests/ -v --cov=app
```

**Test Coverage:**
- ✅ Models and schemas (validation, serialization)
- ✅ Services (enum extraction, workflow generation, execution)
- ✅ API endpoints (CRUD, error handling, WebSocket)
- ✅ Integration tests (full workflow execution)

**50+ tests** covering:
- Parameter grid validation
- ComfyScript code generation
- Experiment execution
- W&B integration
- Error handling

### Frontend Tests

```bash
cd frontend
npm run test
```

---

## 🔧 **Development**

### Backend Development

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Frontend Development

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

---

## 🎨 **Key Components**

### Z-Axis Scrubber

The interactive Z-axis scrubber is a highlight feature:

```typescript
<ZAxisScrubber
  zValues={['euler', 'dpmpp_2m', 'uni_pc']}
  currentIndex={0}
  onChange={(index) => setCurrentZ(index)}
  parameterName="Sampler"
/>
```

**Features:**
- Keyboard navigation (`[` and `]` keys)
- Smooth slider transitions
- Value labels and current value display
- Responsive design

### Parameter Control

Flexible parameter definition:

```typescript
<ParameterControl
  label="CFG Scale"
  parameterName="cfg"
  type={ParameterType.NUMERIC}
  onChange={(definition) => setXAxis(definition)}
/>
```

**Supports:**
- Numeric ranges (min, max, step)
- Categorical selection (multi-select)
- Enum values (auto-populated from ComfyScript)

---

## 🌐 **API Documentation**

Full API documentation available at: http://localhost:8000/docs

### Key Endpoints

```
GET  /api/v1/health              # Health check
GET  /api/v1/enums               # Get all available enums
POST /api/v1/experiments         # Create experiment
GET  /api/v1/experiments/{id}    # Get experiment status
POST /api/v1/experiments/{id}/execute  # Start execution
WS   /ws/experiments/{id}        # WebSocket updates
POST /api/v1/wandb/sync          # Sync to W&B
POST /api/v1/code/generate       # Generate ComfyScript code
```

---

## 🚀 **Deployment**

### Production Deployment

1. **Update environment variables**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with production values
   ```

2. **Build and deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure reverse proxy** (Nginx/Traefik) for HTTPS

### Environment Variables

**Backend** (`.env`):
```env
COMFYUI_URL=http://comfyui:8188
DATABASE_URL=postgresql://user:pass@db/xyz_studio
WANDB_API_KEY=your_wandb_key
SECRET_KEY=your_secret_key
CORS_ORIGINS=https://yourdomain.com
```

---

## 📊 **W&B Integration**

Enable experiment tracking with Weights & Biases:

1. **Set W&B API key**:
   ```bash
   export WANDB_API_KEY=your_key_here
   ```

2. **Enable in experiment creation**:
   ```typescript
   {
     enable_wandb: true,
     wandb_tags: ['txt2img', 'cfg-sweep']
   }
   ```

3. **View results**:
   - Automatic run creation
   - All images logged as artifacts
   - Parameter grid as table
   - Metrics and charts

---

## 🤝 **Contributing**

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines

- **Backend**: Follow PEP 8, type hints required
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Tests**: Required for all new features
- **Documentation**: Update README and API docs

---

## 📝 **Roadmap**

### Phase 1 (Current - MVP)
- ✅ Basic XYZ parameter grid
- ✅ txt2img workflow template
- ✅ Real-time execution
- ✅ Z-axis scrubber
- ✅ W&B integration
- ✅ Docker deployment

### Phase 2 (Next)
- [ ] Multiple workflow templates (img2img, hires fix)
- [ ] Advanced metrics (aesthetic score, CLIP similarity)
- [ ] Video/GIF export
- [ ] Prompt matrix (4D plots)
- [ ] Multi-model comparison
- [ ] Community template sharing

### Phase 3 (Future)
- [ ] Statistical analysis and optimization
- [ ] A/B testing with significance tests
- [ ] Cost tracking and quotas
- [ ] Team collaboration features
- [ ] API access for programmatic use

---

## 🐛 **Troubleshooting**

### Common Issues

**ComfyUI not connecting:**
```bash
# Check ComfyUI is running
curl http://localhost:8188

# Check backend logs
docker-compose logs backend
```

**Frontend not loading:**
```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

**GPU not available:**
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## 📄 **License**

MIT License - see LICENSE file for details

---

## 🙏 **Acknowledgments**

- **ComfyScript** - Chaoses-Ib for the amazing Python frontend for ComfyUI
- **ComfyUI** - comfyanonymous for the revolutionary node-based interface
- **Community** - All the ComfyUI enthusiasts and contributors

---

## 📧 **Support**

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Discord**: [Join our server](#)

---

**Built with ❤️ for the ComfyUI community**

*From guesswork to science - systematic exploration made easy.*
