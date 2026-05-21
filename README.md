# KARMA — Knowledge Augmented embodied agents with long- and short-term Recall Memory for AI

重构后的 KARMA 采用与 [MoETTA](../MoETTA) 类似的仓库布局：**统一 CLI 入口**、**dataclass 配置**、**分层 `src/` 源码**、**可选 W&B 可观测性**，便于理解、实验与调试。

## 架构概览

```
用户任务 / 基准任务
        │
        ▼
   main.py (tyro CLI)
        │
        ▼
  src/pipeline.py
        │
        ├─► src/memory/retrieval.py   短期记忆 + RAG 示例检索
        ├─► src/llm/planner.py        LLM 任务分解 → task_functions.py
        └─► src/env/executor.py         AI2-THOR 仿真执行 + 记忆更新
```

| 目录 | 职责 |
|------|------|
| `main.py` | 唯一 Python 入口，支持 CLI 覆盖配置 |
| `config/` | dataclass 配置与预设（`base` / `headless` / `benchmark` / `smoke`） |
| `src/pipeline.py` | 实验流水线编排 |
| `src/llm/` | 百炼 DashScope 客户端与规划器 |
| `src/memory/` | 场景映射、短期/长期记忆、语义检索 |
| `src/env/` | AI2-THOR 执行引擎、GUI、生成任务代码 |
| `src/benchmark/` | 无 GUI 基准任务（`long_task_1` ~ `long_task_6`） |
| `scripts/` | 环境安装、冒烟测试、批量实验 shell |
| `prompts/` | LLM 提示词模板（运行时读写） |
| `memory/` | 记忆持久化 JSON / 图像 |
| `logs/` | 运行中间状态 |
| `artifacts/` | 实验日志、基准输出、W&B 离线缓存 |

## 快速开始

### 1. 环境

```bash
cd KARMA
bash scripts/setup_env.sh
source .venv/bin/activate
export KARMA_ROOT=$PWD
cp .env.example .env   # 填入 DASHSCOPE_API_KEY
source .env
```

### 2. 外部依赖（需自行准备）

详见 [SETUP_USER.md](SETUP_USER.md)：

- **DashScope API Key** — LLM 规划与视觉分析
- **AI2-THOR CloudRendering** — headless 仿真 (~797 MB)
- **all-mpnet-base-v2** — 短期记忆语义检索 (~420 MB)

```bash
bash scripts/download_assets_mirror.sh ai2thor
bash scripts/download_assets_mirror.sh mpnet
```

### 3. 冒烟测试

```bash
# 跳过下载/API 调用
KARMA_SKIP_DOWNLOADS=1 python main.py smoke

# 完整检测
python scripts/smoke_test.py
```

## 使用方式

### 交互式 GUI

```bash
python main.py base --task.use_gui
# 或兼容旧入口
python scripts/GUI_karma.py
```

### 单任务（CLI）

```bash
python main.py base \
  --task.instruction "wash an apple and put it on the countertop" \
  --env.name wash_apple_demo
```

### 仅规划（不启动仿真）

```bash
python main.py headless \
  --task.instruction "slice a tomato and place it on the plate"
```

### 基准评估

```bash
bash scripts/run_benchmark.sh long_task_3

# 或直接 CLI
python main.py benchmark \
  --benchmark.task_name long_task_3 \
  --benchmark.output_path artifacts/long_task_3_output.json
```

输出指标：`explore_count`（探索次数）、`total_time`（总耗时）。

### 启用 W&B 可观测性

在 `.env` 中配置 `WANDB_API_KEY`，然后：

```bash
python main.py base \
  --env.wandb_mode online \
  --env.group my-exp \
  --env.name run_001 \
  --task.instruction "wash an apple"
```

日志同时写入 `artifacts/logs/`（loguru）与 W&B。

## 配置系统

与 MoETTA 相同，使用 **tyro + dataclass**：

```bash
python main.py base --simulation.scene FloorPlan1 --llm.chat_model qwen3.5-omni-flash
python main.py benchmark --benchmark.task_name long_task_1
```

可用预设：

| 预设 | 说明 |
|------|------|
| `base` | 默认完整流水线 |
| `headless` | 仅记忆检索 + LLM 规划 |
| `benchmark` | 运行内置基准任务 |
| `smoke` | 运行冒烟测试 |

## 与原版脚本的兼容

`scripts/` 下保留薄封装，旧命令仍可用：

| 旧命令 | 新推荐 |
|--------|--------|
| `python scripts/GUI_karma.py` | `python main.py base --task.use_gui` |
| `python scripts/llm_as_planner.py` | `python main.py headless` |
| `python scripts/smoke_test.py` | `python main.py smoke` |

## 数据流

1. **任务输入** → 写入 `prompts/instruction.txt`、`logs/task_description.json`
2. **记忆检索** → SentenceTransformer 匹配 `memory/memory3.json`，RAG 检索 `experience/experience.json`
3. **LLM 规划** → 生成 Python 函数写入 `src/env/task_functions.py`
4. **仿真执行** → AI2-THOR 原语队列执行，PutObject 后更新短期记忆与视觉分析

## Citation

```bibtex
@article{wang2024karma,
  title={Karma: Augmenting embodied ai agents with long-and-short term memory systems},
  author={Wang, Zixuan and Yu, Bo and Zhao, Junzhe and Sun, Wenhao and Hou, Sai and Liang, Shuai and Hu, Xing and Han, Yinhe and Gan, Yiming},
  journal={arXiv preprint arXiv:2409.14908},
  year={2024}
}
```
