# MindMirror

### Your Decisions, Replayed. Your Thinking, Evolved.

MindMirror is a private, local-first AI decision-learning system that
helps a person learn from the gap between **what they believed before a
decision** and **what actually happened afterward**.

Instead of giving advice before a decision, MindMirror creates a record
of the decision, prediction, confidence, reasoning and later outcome. It
then replays those decisions and uses local AI to surface recurring
patterns in the user's reasoning.

> **Core idea:** Don't just make better decisions. Learn how you make
> decisions.

------------------------------------------------------------------------

## Why MindMirror?

Most decision tools focus on the decision itself: what should I choose?

MindMirror focuses on the learning loop after the decision:

**Think → Predict → Lock → Experience → Reflect**

The system turns past decisions into structured learning material.

For example, if someone repeatedly predicts stronger outcomes than
reality delivers, MindMirror can surface that pattern and ask a
practical question before a similar future decision.

It is designed as a reflective tool, not as a psychological diagnostic
system.

------------------------------------------------------------------------

## What MindMirror Does

### 1. Decision Capture

Before acting, the user records:

-   The decision
-   Their reasoning
-   Their prediction
-   Their confidence
-   An expected date for the outcome

This creates a time-stamped record of what the user believed **before
reality was known**.

### 2. Decision History

Completed and pending decisions can be reviewed in one place.

Each decision preserves the original prediction so it can later be
compared with the actual outcome.

### 3. Decision Replay

MindMirror brings the original decision back alongside the outcome.

This creates a simple but powerful comparison:

**What I expected → What actually happened → What I can learn**

### 4. Reasoning Mirror

The local AI analyzes recorded decisions and highlights patterns such
as:

-   recurring reasoning patterns
-   important assumptions
-   evidence explicitly mentioned in the reasoning
-   prediction patterns
-   reality checks
-   a practical question to consider next time

The analysis is intentionally grounded in the user's recorded
information rather than inventing additional facts.

### 5. Assumption Ledger

The Assumption Ledger organizes each decision into:

**Assumption → Evidence → Evidence Type → Prediction → Actual Outcome →
Reality Check → Lesson**

This makes it easier to see which assumptions held up and which did not.

The system distinguishes between information actually recorded by the
user and AI-generated interpretation.

### 6. Decision Fingerprint

The Decision Fingerprint looks across multiple completed decisions
instead of analyzing only one.

It can summarize:

-   prediction bias
-   confidence versus prediction accuracy
-   effectiveness of recorded evidence
-   recurring reasoning patterns
-   the practical adjustment most supported by the data
-   a question to ask before the next similar decision

The Fingerprint is intended as a reflection aid, not a clinical or
psychological assessment.

------------------------------------------------------------------------

## AI Architecture

MindMirror separates the application logic from the AI execution layer.

``` text
                    MindMirror
                         │
                         ▼
                AI Runtime Layer
                 ┌───────┴────────┐
                 │                │
          Development         Snapdragon
           / Fallback          Target
                 │                │
              Ollama       Qualcomm Runtime
                 │                │
           Local Model      Local Model /
                            NPU-capable path
```

The application communicates with a runtime abstraction rather than
directly depending on one inference backend.

### Current development runtime

The development environment uses:

-   Python
-   Streamlit
-   Ollama
-   Qwen3.5 2B
-   SQLite

The current development machine is used for software development and
testing. **Snapdragon NPU execution is not claimed by the current
development environment.**

### Snapdragon deployment direction

The runtime layer is designed so the application can use a
Qualcomm-supported local inference path on a Snapdragon-powered Windows
PC without changing the core decision-learning workflow.

The intended deployment can use Qualcomm's supported AI tooling and an
appropriate local model/runtime for the target Snapdragon device.

This separation is important because it allows the same MindMirror
experience to be developed and tested on a non-Snapdragon machine while
keeping the inference backend replaceable for Snapdragon deployment.

------------------------------------------------------------------------

## Privacy by Design

MindMirror is built around a local-first architecture.

Decision records are stored locally in SQLite and the AI inference path
is designed around local execution.

The project does not require a cloud AI API for its core reasoning
workflow.

This matters because decision journals can contain highly personal
business, academic or life context.

**Principle: your decisions should not need to leave your device just to
learn from them.**

> Note: local-first architecture does not automatically guarantee
> privacy in every deployment. Users should still review the runtime,
> model and operating-system environment used on their device.

------------------------------------------------------------------------

## Technology Stack

  Component                      Technology
  ------------------------------ -------------------------
  Interface                      Streamlit
  Language                       Python
  Local AI development runtime   Ollama
  Development model              Qwen3.5 2B
  Storage                        SQLite
  Runtime abstraction            `mindmirror_runtime.py`
  AI reasoning                   `ai_engine.py`
  Application                    `app.py`

------------------------------------------------------------------------

## Project Structure

``` text
MindMirror/
│
├── app.py                  # Streamlit application and UI
├── ai_engine.py            # AI analysis and structured reasoning
├── mindmirror_runtime.py   # Runtime abstraction / backend detection
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Local files and development artifacts
```

Development backups and local database files are intentionally excluded
from the public repository.

------------------------------------------------------------------------

## Running MindMirror Locally

### 1. Clone the repository

``` bash
git clone https://github.com/yuvrajs166315-cmd/MindMirror.git
cd MindMirror
```

### 2. Create a virtual environment

Windows PowerShell:

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` powershell
pip install -r requirements.txt
```

### 4. Install and start Ollama

Install Ollama for Windows and make sure the Ollama service is running.

Then download the development model:

``` powershell
ollama pull qwen3.5:2b
```

### 5. Start MindMirror

``` powershell
streamlit run app.py
```

The Streamlit application will open in the browser.

------------------------------------------------------------------------

## Example Learning Loop

A simplified MindMirror cycle looks like this:

``` text
User makes a decision
        │
        ▼
Records reasoning + prediction + confidence
        │
        ▼
Decision is stored locally
        │
        ▼
Reality produces an outcome
        │
        ▼
User records the actual outcome
        │
        ▼
MindMirror replays the decision
        │
        ▼
Local AI compares expectation with reality
        │
        ▼
Patterns + assumptions + lessons
        │
        ▼
Better questions for the next decision
```

------------------------------------------------------------------------

## Grounded AI

A key design principle is **grounded reflection**.

MindMirror should not manufacture evidence that the user never recorded.

For example, if a user writes:

> "I expect strong student demand."

MindMirror can identify that as an assumption.

It should **not** automatically claim that the user used market
research, historical sales data or competitor analysis unless those
things were actually included in the recorded reasoning.

This distinction is especially important for a decision-learning product
because fabricated explanations would undermine the very learning
process the system is trying to improve.

------------------------------------------------------------------------

## Structured AI Output

The AI engine uses structured JSON schemas for important analysis tasks.

This allows the application to receive predictable fields instead of
relying on free-form model output.

Examples include:

-   single-decision reasoning analysis
-   history analysis
-   assumption ledger generation
-   decision fingerprint analysis

This makes the AI layer easier to validate and the UI easier to
maintain.

------------------------------------------------------------------------

## What Makes MindMirror Different

MindMirror is not positioned simply as another chatbot that gives
recommendations.

Its core workflow is longitudinal:

**record → wait → observe → replay → compare → learn**

The differentiating product idea is the combination of:

-   decision journaling
-   explicit predictions
-   confidence capture
-   outcome replay
-   assumption tracking
-   longitudinal reasoning analysis
-   a Decision Fingerprint
-   local-first AI execution

The goal is to help users understand **how their predictions and
reasoning behave over time**, rather than simply receiving another
recommendation from an AI.

------------------------------------------------------------------------

## Snapdragon Optimization & Deployment

MindMirror is being developed with a runtime abstraction so the AI
backend can be adapted to Snapdragon-powered Windows PCs.

The deployment target is a local AI experience where inference can take
advantage of the Snapdragon platform's AI acceleration capabilities.

For a competition deployment, the following should be demonstrated on
the actual Snapdragon target device:

1.  The Snapdragon device model.
2.  The selected Qualcomm-supported inference runtime.
3.  The selected model.
4.  The accelerator/path used for inference.
5.  A successful local inference run.
6.  Offline behavior.
7.  Basic latency or performance measurements.

The repository deliberately separates **development/fallback runtime**
from **Snapdragon deployment runtime** so these claims can be verified
independently.

------------------------------------------------------------------------

## Development Status

Current implemented workflow:

-   [x] Decision capture
-   [x] Decision history
-   [x] Decision replay
-   [x] Reasoning Mirror
-   [x] Assumption Ledger
-   [x] AI Decision Fingerprint
-   [x] Local AI development runtime
-   [x] Runtime abstraction
-   [x] SQLite local storage
-   [x] Structured AI outputs
-   [x] Public GitHub repository

Next deployment milestone:

-   [ ] Validate the Qualcomm/Snapdragon runtime on the target HP
    Snapdragon PC
-   [ ] Verify actual accelerator/NPU execution
-   [ ] Measure local inference performance
-   [ ] Document Snapdragon deployment and benchmark evidence

------------------------------------------------------------------------

## Responsible Use

MindMirror is a reflective decision-support and learning tool.

Its AI-generated observations should be treated as prompts for
reflection, not as objective judgments about a person's intelligence,
personality or mental state.

The system should not be used as a substitute for professional advice in
high-stakes medical, legal or financial decisions.

------------------------------------------------------------------------

## License

This project is currently provided as a competition prototype. Licensing
terms can be added before public release.
