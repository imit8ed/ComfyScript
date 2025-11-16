# User Guide - XYZ Plot Studio

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating Experiments](#creating-experiments)
4. [Understanding Results](#understanding-results)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

XYZ Plot Studio helps you systematically explore hyperparameter spaces in ComfyUI. Instead of manually testing different settings, you can define parameter ranges and let the system generate all combinations automatically.

**Common Use Cases:**
- Finding optimal CFG and Steps for your prompt
- Comparing different samplers and schedulers
- Testing LoRA weights and strengths
- Model comparison across checkpoints
- Prompt engineering with parameter sweeps

---

## Getting Started

### First Time Setup

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **Access the web interface**:
   Open http://localhost:3000 in your browser

3. **Verify connection**:
   The app should show available samplers, schedulers, and checkpoints

### Understanding the Interface

The main interface consists of:
- **Header**: App title and navigation
- **Experiment Builder**: Where you create new experiments
- **Parameter Controls**: X, Y, and Z axis configuration
- **Workflow Settings**: Prompt, checkpoint, and generation settings
- **Summary Panel**: Shows total combinations and estimated time

---

## Creating Experiments

### Step 1: Define Your Research Question

Before creating an experiment, decide what you want to learn:

**Example Questions:**
- "What's the best CFG scale for portraits?"
- "How do different samplers affect image quality?"
- "What step count gives the best detail vs. speed?"

### Step 2: Choose Your Parameters

**X-Axis** (First parameter):
- Typically the most important variable
- Example: CFG Scale (4.0 to 12.0)

**Y-Axis** (Second parameter):
- Complementary parameter
- Example: Steps (15 to 40)

**Z-Axis** (Third parameter):
- Usually categorical (samplers, schedulers)
- Example: Sampler (euler, dpmpp_2m, uni_pc)

### Step 3: Configure Parameter Ranges

#### Numeric Parameters (CFG, Steps, Denoise)

1. Set **Min Value**: Starting point (e.g., 4.0)
2. Set **Max Value**: Ending point (e.g., 12.0)
3. Set **Step**: Increment (e.g., 2.0)
   - Smaller steps = more detail, more images
   - Larger steps = faster, fewer images

**Example**: CFG from 4.0 to 12.0 in steps of 2.0
- Values: [4.0, 6.0, 8.0, 10.0, 12.0] = 5 images

#### Categorical Parameters (Samplers, Schedulers)

1. Click **Select All** or choose individual values
2. Selected values will be tested

**Example**: Samplers
- ☑ euler
- ☑ dpmpp_2m
- ☑ uni_pc
= 3 samplers

### Step 4: Configure Workflow

**Required Settings:**
- **Checkpoint**: Choose your model (e.g., "v1-5-pruned-emaonly")
- **Prompt**: Your positive prompt
- **Negative Prompt**: What to avoid
- **Dimensions**: Image width and height

**Optional Settings:**
- **Seed**: Set for reproducibility (-1 for random)
- **Batch Size**: Usually keep at 1
- **VAE**: Optional custom VAE

**Example Workflow:**
```
Checkpoint: v1-5-pruned-emaonly.safetensors
Prompt: "A beautiful sunset over mountains, highly detailed, 4k"
Negative: "low quality, blurry, distorted"
Width: 512
Height: 512
Seed: 42
```

### Step 5: Review and Launch

1. **Check Total Combinations**:
   - X values × Y values × Z values = Total images
   - Example: 5 × 4 × 3 = 60 images

2. **Estimate Time**:
   - Roughly 20-30 seconds per image
   - 60 images ≈ 20-30 minutes

3. **Click "Create and Start Experiment"**

---

## Understanding Results

### Real-Time Progress

While your experiment runs:
1. **Progress Bar**: Shows completion percentage
2. **Images Generated**: Count of finished images
3. **Live Preview**: See images as they're created
4. **Estimated Time Remaining**: Based on current speed

### Using the Z-Axis Scrubber

The Z-Axis Scrubber lets you navigate through different Z values:

**Keyboard Shortcuts:**
- `[` - Previous Z value
- `]` - Next Z value
- Arrow Left/Right also work

**Mouse Control:**
- Drag the slider to jump to any Z value
- Click prev/next buttons

**What You See:**
- Current Z value is highlighted
- Grid shows all X×Y combinations for that Z
- Value labels show each Z option

### Analyzing Results

**Look for patterns:**
1. **Sweet Spots**: Parameter combinations that work well
2. **Trends**: How one parameter affects output
3. **Outliers**: Unexpected good or bad results

**Example Analysis:**
```
Z = euler:
  - CFG 6-8 looks best
  - Higher steps don't help much after 25

Z = dpmpp_2m:
  - Can use lower CFG (4-6)
  - Benefits from more steps (30+)

Conclusion: Use dpmpp_2m with CFG=5, Steps=30
```

### Exporting Results

**Available Exports:**
1. **Image Grid**: All results in one image
2. **Individual Images**: Download specific ones
3. **JSON Data**: Parameter values and metadata
4. **W&B Link**: Share experiment with team

---

## Advanced Features

### Template-Based Experiments

**Pre-configured Templates:**
- **txt2img Standard**: Basic image generation
- **img2img Refine**: Image-to-image with strength sweep
- **Hires Fix**: Two-pass generation with upscaling
- **LoRA Comparison**: Test multiple LoRAs

Select template → Customize parameters → Launch

### Multi-Seed Experiments

For statistical robustness:
1. Enable "Multi-Seed Mode"
2. Set number of seeds (e.g., 5)
3. Each combination generates N images with different seeds

**Use Case**: Measure consistency of results

### W&B Integration

Track experiments professionally:

1. **Set W&B API Key**:
   ```bash
   export WANDB_API_KEY=your_key
   ```

2. **Enable in Experiment**:
   - Check "Enable W&B Logging"
   - Add tags (e.g., "portrait", "cfg-sweep")

3. **View Results**:
   - Automatic run creation
   - All images logged as artifacts
   - Shareable dashboard

### Code Generation

View the generated ComfyScript:

1. Click "View Generated Code"
2. Review the Python code
3. Edit if needed (Advanced)
4. Copy for manual execution

**Example Use**: Learn how parameter sweeps work

### Queuing Multiple Experiments

Run multiple experiments sequentially:

1. Create first experiment → Don't execute yet
2. Create second experiment
3. Both will queue and run in order

**Manage Queue**:
- View all queued experiments
- Reorder priority
- Cancel individual experiments

---

## Troubleshooting

### Common Issues

#### "ComfyUI not connected"

**Causes:**
- ComfyUI server not running
- Wrong URL configuration

**Solutions:**
```bash
# Check if ComfyUI is running
curl http://localhost:8188

# Restart ComfyUI
docker-compose restart comfyui

# Check backend logs
docker-compose logs backend
```

#### "No samplers/schedulers found"

**Cause**: Enum extraction failed

**Solution:**
```bash
# Restart backend to re-initialize
docker-compose restart backend

# Check ComfyUI is accessible
curl http://localhost:8188/system_stats
```

#### "Experiment stuck at 0%"

**Causes:**
- Checkpoint not found
- Out of VRAM
- ComfyUI error

**Solutions:**
1. Check checkpoint name matches exactly
2. Reduce batch size or image dimensions
3. Check ComfyUI logs:
   ```bash
   docker-compose logs comfyui
   ```

#### "Too many images error"

**Cause**: Total combinations exceed limit (500)

**Solution**:
- Reduce number of parameter values
- Use larger steps for numeric ranges
- Create multiple smaller experiments

### Performance Issues

#### Slow Generation

**Optimize:**
1. Reduce image dimensions (512→480)
2. Lower step counts
3. Use faster samplers (euler vs dpmpp_3m)
4. Ensure GPU is being used

#### Out of Memory

**Solutions:**
1. Reduce batch size to 1
2. Lower image dimensions
3. Close other GPU applications
4. Use model with smaller VRAM requirements

### Getting Help

**Resources:**
1. Check the [Architecture Docs](ARCHITECTURE.md)
2. Review [API Documentation](http://localhost:8000/docs)
3. Search GitHub Issues
4. Ask on Discord

**When Reporting Issues:**
- Include experiment configuration
- Share error messages
- Attach backend logs
- Note ComfyUI version

---

## Best Practices

### Efficient Experimentation

1. **Start Small**: Test with 2-3 values first
2. **Iterate**: Refine ranges based on initial results
3. **Document**: Use descriptive experiment names
4. **Organize**: Tag experiments for easy searching

### Parameter Selection

**Good Parameter Combinations:**
- CFG × Steps × Sampler (very informative)
- Denoise × Steps (for img2img)
- LoRA Strength × CFG (for LoRA tuning)

**Avoid:**
- Three numeric parameters (hard to visualize)
- Very fine-grained steps (too many images)
- Unrelated parameters

### Reproducibility

For reproducible experiments:
1. Set explicit seed (not -1)
2. Note ComfyUI version
3. Save experiment JSON
4. Export to W&B

---

## Tips and Tricks

### Finding Sweet Spots Faster

1. **Coarse → Fine**:
   - First: Large steps (CFG: 4, 8, 12)
   - Then: Small steps around best (6.5, 7.0, 7.5)

2. **Reference Images**:
   - Include a "baseline" in every experiment
   - Compare against known good settings

3. **Parameter Coupling**:
   - Some parameters interact (CFG + Sampler)
   - Test these together on X and Y axes

### Keyboard Shortcuts

- `[` / `]` - Navigate Z-axis
- `Ctrl+Enter` - Start experiment (in builder)
- `Esc` - Cancel current action

### Experiment Naming

Good names help organization:
```
✅ "Portrait_CFG-vs-Steps_euler_v1.5"
✅ "Landscape_Sampler-Comparison_2024-01"
❌ "test1"
❌ "experiment"
```

### Batch Operations

Generate multiple related experiments:
1. Create base configuration
2. Duplicate and modify Z-axis
3. Queue all
4. Compare results across experiments

---

## Examples

### Example 1: Finding Optimal Portrait Settings

**Goal**: Best CFG and Steps for portraits

**Configuration:**
- X: CFG (5.0 to 9.0, step 1.0) = 5 values
- Y: Steps (20 to 35, step 5) = 4 values
- Z: Sampler (euler, dpmpp_2m) = 2 values
- Total: 5 × 4 × 2 = 40 images

**Prompt**: "portrait of a woman, professional photography, detailed"

**Result**: CFG=7.0, Steps=25, Sampler=dpmpp_2m

### Example 2: Sampler Comparison

**Goal**: Compare all samplers

**Configuration:**
- X: CFG (7.0 only) = 1 value
- Y: Steps (20, 30, 40) = 3 values
- Z: Sampler (all available) = 15 values
- Total: 1 × 3 × 15 = 45 images

**Prompt**: "a futuristic city, detailed, 8k"

**Result**: Visual comparison of all samplers at different step counts

### Example 3: LoRA Strength Tuning

**Goal**: Find optimal LoRA strength

**Configuration:**
- X: LoRA Strength (0.2 to 1.0, step 0.2) = 5 values
- Y: CFG (6.0 to 10.0, step 1.0) = 5 values
- Z: Steps (20, 30) = 2 values
- Total: 5 × 5 × 2 = 50 images

**Result**: LoRA Strength=0.6, CFG=7.5, Steps=30

---

**Happy Experimenting!** 🚀
