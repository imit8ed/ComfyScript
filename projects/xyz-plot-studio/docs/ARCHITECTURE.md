# Architecture Documentation

## System Overview

XYZ Plot Studio is a full-stack web application designed for systematic hyperparameter exploration in ComfyUI. It uses a microservices architecture with clear separation between the frontend, backend, and ComfyUI instance.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Port 3000)                 │ │
│  │  - Experiment Builder UI                                │ │
│  │  - Z-Axis Scrubber                                      │ │
│  │  - Real-time Progress Display                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  API Routes  │  │   Services   │  │    Models    │     │
│  │              │  │              │  │              │     │
│  │ - Enums      │  │ - Enum Svc   │  │ - Schemas    │     │
│  │ - Code Gen   │  │ - Workflow   │  │ - Database   │     │
│  │ - Experiments│  │ - Executor   │  │ - Types      │     │
│  │ - W&B        │  │ - W&B        │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  WebSocket   │  │   SQLite     │                        │
│  │  Manager     │  │  Database    │                        │
│  └──────────────┘  └──────────────┘                        │
└──────────────────────┬───────────────────────────────────────┘
                       │ ComfyScript API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ComfyUI Instance (Port 8188)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Models     │  │    Nodes     │  │   Samplers   │     │
│  │              │  │              │  │              │     │
│  │ - SD Models  │  │ - KSampler   │  │ - Schedulers │     │
│  │ - VAEs       │  │ - LoRA       │  │ - Methods    │     │
│  │ - LoRAs      │  │ - ControlNet │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               External Services (Optional)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Weights &   │  │    Redis     │                        │
│  │   Biases     │  │  (Celery)    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + TypeScript)

**Technology Stack:**
- React 18.2 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- Axios for HTTP requests

**Key Components:**
1. **ExperimentBuilder** - Main UI for creating experiments
2. **ParameterControl** - Reusable parameter definition widget
3. **ZAxisScrubber** - Interactive Z-axis navigation
4. **ResultsGrid** - Display generated images in grid
5. **CodeViewer** - View/edit generated ComfyScript

**State Management:**
```typescript
interface AppState {
  currentExperiment: Experiment | null
  experiments: Experiment[]
  enums: AvailableEnums | null
  isLoading: boolean
}
```

**API Communication:**
- REST API for CRUD operations
- WebSocket for real-time updates
- Automatic reconnection on disconnect

### Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI 0.104+
- SQLAlchemy for ORM
- Pydantic for validation
- asyncio for async operations
- pytest for testing

**Service Layer:**

1. **EnumService** (`app/services/enum_service.py`)
   - Initializes ComfyScript runtime
   - Extracts available enums (Samplers, Schedulers, etc.)
   - Caches enum values for performance

2. **WorkflowGenerator** (`app/services/workflow_generator.py`)
   - Generates ComfyScript code from parameter grid
   - Supports multiple workflow templates
   - Creates workflow JSON for API format

3. **ExperimentExecutor** (`app/services/experiment_service.py`)
   - Executes XYZ plot experiments
   - Manages workflow execution
   - Handles cancellation and error recovery

4. **WandbService** (`app/services/wandb_service.py`)
   - Integrates with Weights & Biases
   - Logs experiments, images, and metrics
   - Creates shareable run URLs

**Data Flow:**

```
Request → API Route → Service Layer → ComfyScript → ComfyUI
                         ↓
                    Database ← Response
```

**Database Schema:**

```sql
-- Experiments table
CREATE TABLE experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    parameter_grid_json JSON,
    workflow_config_json JSON,
    total_images INTEGER,
    images_generated INTEGER,
    created_at TIMESTAMP,
    ...
);

-- Images table
CREATE TABLE images (
    id TEXT PRIMARY KEY,
    experiment_id TEXT REFERENCES experiments(id),
    parameters_json JSON,
    image_path TEXT,
    seed INTEGER,
    generation_time REAL,
    ...
);
```

### ComfyScript Integration

**Initialization:**
```python
from comfy_script.runtime import load
load()  # Connects to ComfyUI server

from comfy_script.runtime.nodes import *
```

**Enum Extraction:**
```python
# Access enums from ComfyScript
from comfy_script.runtime import nodes

# Global enums
checkpoints = list(nodes.Checkpoints)

# Node-specific enums
samplers = list(nodes.KSampler.sampler_name)
schedulers = list(nodes.KSampler.scheduler)
```

**Workflow Execution:**
```python
with Workflow():
    model, clip, vae = CheckpointLoaderSimple(checkpoint)

    for z_value in z_values:
        for y_value in y_values:
            for x_value in x_values:
                # Build workflow dynamically
                latent = KSampler(model, cfg=x_value, steps=y_value, ...)
                image = VAEDecode(latent, vae)
                SaveImage(image, filename)
```

## Security Considerations

### Authentication
- Optional JWT-based authentication
- API rate limiting (100 req/min per IP)
- CORS configuration for allowed origins

### Input Validation
- Pydantic models for all request/response
- Parameter grid size limits (max 500 images)
- File upload size limits
- SQL injection prevention via ORM

### Sandboxing
- ComfyScript code generation is template-based (no arbitrary execution)
- Docker container isolation
- Limited file system access

## Performance Optimization

### Backend
1. **Caching**:
   - Enum values cached after first load
   - Redis for distributed caching (future)

2. **Async Operations**:
   - All I/O operations are async
   - Background task execution for experiments
   - Non-blocking WebSocket connections

3. **Database**:
   - Indexes on frequently queried fields
   - Connection pooling
   - Batch inserts for images

### Frontend
1. **Code Splitting**:
   - Route-based code splitting
   - Lazy loading of components

2. **Image Optimization**:
   - Lazy loading with virtual scrolling
   - Thumbnail generation (256px)
   - Progressive image loading

3. **State Management**:
   - Zustand for minimal re-renders
   - React Query for server state caching

## Scalability

### Horizontal Scaling

**Backend:**
- Stateless API servers (can run multiple instances)
- Load balancing via Nginx/HAProxy
- Shared database and Redis

**Task Queue:**
- Celery workers for experiment execution
- Multiple workers for parallel generation
- Result backend via Redis

**ComfyUI:**
- Multiple ComfyUI instances for load distribution
- Round-robin or least-busy scheduling

### Vertical Scaling

**GPU:**
- Batch processing to maximize GPU utilization
- Multiple experiments in parallel (if VRAM allows)

**Memory:**
- Stream large results instead of loading all at once
- Paginated API responses

## Monitoring and Observability

### Logging
```python
# Structured logging
logger.info("Experiment started", extra={
    "experiment_id": exp_id,
    "total_images": total_images
})
```

### Metrics
- Request latency (p50, p95, p99)
- Experiment success rate
- Generation time per image
- Error rates by endpoint

### Health Checks
```
GET /api/v1/health
{
  "status": "healthy",
  "comfyui_connected": true,
  "redis_connected": true
}
```

## Error Handling

### Strategy
1. **Graceful Degradation**:
   - Frontend works without backend (shows error states)
   - Backend works without ComfyUI (limited functionality)

2. **Retry Logic**:
   - Automatic retry for transient failures
   - Exponential backoff for rate limits

3. **User Feedback**:
   - Clear error messages
   - Actionable suggestions
   - Error reporting to backend

### Example Error Flow
```
User Action → Frontend Validation → Backend Validation → Service Layer
                  ↓ Error               ↓ 400 Error        ↓ 500 Error
              Show Inline           Show Toast          Log + Alert
```

## Testing Strategy

### Unit Tests
- Service layer logic
- Parameter validation
- Code generation

### Integration Tests
- API endpoints
- Database operations
- ComfyScript interaction

### End-to-End Tests
- Full experiment workflow
- WebSocket communication
- Error scenarios

**Coverage Target:** 80%+

## Deployment

### Docker Compose (Development)
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]

  frontend:
    build: ./frontend
    ports: ["3000:80"]

  comfyui:
    image: comfyui:latest
    ports: ["8188:8188"]
```

### Kubernetes (Production)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xyz-backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: xyz-studio-backend:latest
```

## Future Improvements

1. **Performance**:
   - GraphQL for flexible querying
   - Server-side rendering for SEO
   - CDN for static assets

2. **Features**:
   - Multi-user support with auth
   - Experiment templates marketplace
   - Advanced analytics dashboard

3. **Infrastructure**:
   - Kubernetes for orchestration
   - Prometheus + Grafana for monitoring
   - Automated backups and disaster recovery
