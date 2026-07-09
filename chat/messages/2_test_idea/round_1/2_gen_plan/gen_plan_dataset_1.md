# gen_plan_dataset_1 — test_idea

> Phase: `invention_loop` · round 1 · `gen_plan`
> Run: `run_E1yko-FJ_C_D` — Near Duplicate Detection
>
> Full, verbatim transcript of this agent task — every system/user prompt, assistant response, thinking block, tool call and tool result — in the order they occurred. Nothing truncated.

## Task: `gen_plan_dataset_1` (terminal_claude_agent, claude-sonnet-4-6)

### [1] CONFIG · 2026-07-08 09:59:02 UTC

```
model: claude-sonnet-4-6 | effort: low | permission: bypassPermissions | cwd: /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_plan/gen_plan_dataset_1
```

### [2] SYSTEM-USER prompt · 2026-07-08 09:59:10 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A plan generator (Step 3.2: GEN_PLAN in the invention loop)

You received the hypothesis, an artifact direction to elaborate, and dependency artifacts relevant to the plan.
Your job: elaborate this direction into a detailed, actionable plan for the executor agent.

Specific, actionable plan → valuable artifact. Vague plan → wasted execution.
</your_role>
</ai_inventor_context>

<artifact_type_info>
You are expanding an artifact direction of type: DATASET

DATASET
Collect, prepare, and merge datasets for experiments and analysis.
Runtime: Python 3.12, UV, isolated workspace.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-hf-datasets (HuggingFace Hub — ML datasets, many UCI/OpenML/Kaggle mirrors), aii-owid-datasets (Our World in Data — global statistics), aii-json (schema validation). Also any Python source (sklearn.datasets, openml, direct URLs, APIs) — must verify within 300MB limit.
Capabilities: Search, acquire, transform, combine, and standardize data from any available source.
Deps: REQUIRED none | OPTIONAL RESEARCH for guidance on what data to collect
</artifact_type_info>

<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>

<skills>
Skills are self-contained capabilities with instructions, context, and tools.

- aii-web-tools: Web search (Serper), page/PDF fetch as markdown, regex grep over page/PDF text
- aii-semscholar-bib: Batch-fetch BibTeX from Semantic Scholar
- aii-openrouter-llms: Search and call 300+ LLMs via OpenRouter
- aii-hf-datasets: Search, preview, download HuggingFace datasets
- aii-owid-datasets: Search and load Our World in Data tables
- aii-lean: Compile/verify Lean 4 code, Mathlib search, tactic suggestions
- aii-image-gen: Generate/edit images via Gemini 3 Pro Image (Nano Banana Pro)
- aii-json: Validate JSON against schemas, generate mini/preview variants
- aii-paper-writing: Academic paper structure, bibliography, citations
- aii-paper-to-latex: Assemble LaTeX papers and compile to PDF
- aii-parallel-computing: GPU acceleration, CPU parallelism, async I/O
- aii-python: Python coding standards for experiment scripts
- aii-use-hardware: Detect CPU/RAM/GPU, memory-safe processing
- aii-long-running-tasks: Gradual scaling pattern for long-running tasks
- aii-colab: Google Colab runtime constraints for notebooks
- aii-file-size-limit: Check and split oversized output files
- aii-handbook-multi-llm-agents: Multi-LLM agent orchestration patterns
</skills>
</available_resources>

<time_budget>

The dataset executor has 6h total (including writing code, debugging, testing, and fixing errors).

</time_budget>

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<plan_guidelines>
You are expanding an artifact direction from the strategy into a detailed plan.
The artifact direction specifies what to do at a high level (type, objective, approach, dependencies).
Your job is to make it concrete and actionable as a detailed plan.
Use web research to look up technical details, verify feasibility, and find reference materials
that will make your plan more concrete and actionable for the executor.

GOOD PLANS:
- Make each component SPECIFIC and actionable (not vague platitudes)
- Consider both success AND failure scenarios
- Build on the approach in the artifact direction
- Add concrete details the executor needs

BAD PLANS:
- Vague hand-waving ("do research on X")
- Ignoring the approach in the artifact direction
- Missing critical details the executor needs
</plan_guidelines>

<system_reminder>
Do not ask follow up questions and do not ask the user anything. Execute all steps independently.
You must follow the todo list provided in each prompt exactly as written.
No placeholders, stubs, or incomplete code — all code must be complete and functional.
</system_reminder>

<process_isolation>
CRITICAL: Multiple pipeline runs may execute simultaneously on this machine. `ps aux | grep method.py` matches ALL runs, not just yours.
- NEVER kill processes by name (`killall`, `pkill -f`, `ps aux | grep ... | xargs kill`). This kills OTHER runs' processes.
- NEVER monitor processes by name (`ps aux | grep method.py`). You will see other runs' processes and get confused.
- ALWAYS use PID-based process management:
  Run: `uv run method.py & PID=$!` or `timeout <seconds> uv run method.py & PID=$!`
  Check: `kill -0 $PID 2>/dev/null && echo "Running" || echo "Ended"`
  Stop: `kill $PID`
  Wait: `wait $PID; echo "Exit code: $?"`
  Monitor: `tail -f logs/run.log & TAIL_PID=$!` then `kill $TAIL_PID` when done
</process_isolation>

<hypothesis>
kind: hypothesis
title: Clustered Edit Positions Signal Near-Duplicates
hypothesis: >-
  When a near-duplicate text is created by locally modifying an original (as humans typically do: rewriting one paragraph,
  inserting a sentence, changing a local region), the edit operations in the word-level diff between the two texts are spatially
  clustered rather than uniformly distributed. The Index of Dispersion (IoD = variance / mean) of inter-edit-position gaps
  in the word-level diff will be significantly greater than 1 (the Poisson baseline) for genuine near-duplicates, and near
  1 for documents that share similar n-gram fingerprints only due to topical overlap or shared boilerplate. Combining this
  Edit Clustering Score (ECS) with standard Jaccard-based similarity will improve near-duplicate detection precision over
  Jaccard alone, particularly on hard negatives where two unrelated documents share vocabulary but differ structurally.
motivation: >-
  All mainstream near-duplicate detection methods (MinHash, SimHash, NCD, RETSim) measure the QUANTITY of textual overlap
  but ignore the SPATIAL PATTERN of differences. Two documents may share 80% of their 5-grams either because they are genuine
  near-duplicates (one original + localized edits) or because they share boilerplate, legal headers, topic-specific vocabulary,
  or domain jargon. Current methods cannot distinguish these cases without additional metadata. The spatial clustering of
  edits is a free signal that requires no external information: genuine human copy-and-modify behavior naturally produces
  clustered edits, while vocabulary coincidence produces uniformly scattered mismatches. This matters for LLM training data
  deduplication, plagiarism detection, and web crawl deduplication, where false positives (rejecting legitimately distinct
  documents) and false negatives (retaining near-copies) both carry costs.
assumptions:
- >-
  Human near-duplicate creation predominantly involves localized edits (rewriting one section, inserting a passage) rather
  than uniformly scattering word substitutions throughout the entire text.
- >-
  Documents sharing n-gram similarity by coincidence (boilerplate, topical vocabulary) will have their matching segments distributed
  across positions roughly uniformly, producing an IoD near 1.
- >-
  The word-level diff (longest common subsequence based) produces a well-defined sequence of edit positions whose inter-gap
  statistics are meaningful for documents of at least ~100 words.
- >-
  The Index of Dispersion is a sufficient statistic to detect clustering in this 1D point process at the document lengths
  typical of news articles or Wikipedia sections.
investigation_approach: >-
  1. BUILD DATASET: Create three categories of text pairs from Wikipedia articles: (a) near-duplicates — take an article,
  randomly select a contiguous 20-40% span, replace it with content from a different article (local modification); (b) hard
  negatives — take two different articles from the same Wikipedia category (shared vocabulary and Jaccard overlap but structurally
  independent); (c) random pairs — articles from different categories. 2. COMPUTE FEATURES: For each pair, compute (i) Jaccard
  similarity over 5-grams (standard MinHash baseline); (ii) Edit Clustering Score (ECS): run a word-level LCS diff, extract
  the positions of edit tokens (insertions/deletions in the aligned sequence), compute the index of dispersion (variance/mean)
  of inter-edit gaps. 3. EVALUATE: Train a logistic classifier on each feature set (Jaccard only; ECS only; Jaccard+ECS) using
  5-fold cross-validation. Report ROC-AUC and precision@80%-recall. The hypothesis is confirmed if Jaccard+ECS significantly
  outperforms Jaccard alone, specifically by reducing false positives on hard negatives.
success_criteria: >-
  CONFIRM: ROC-AUC of Jaccard+ECS exceeds Jaccard-only by >=0.03 on the hard-negative subset; ECS alone achieves AUC > 0.65
  on discriminating near-duplicates from hard negatives; the median IoD for near-duplicate pairs is at least 2x higher than
  for hard-negative pairs (Mann-Whitney p < 0.01). DISCONFIRM: ECS adds no signal (AUC improvement < 0.01); IoD distributions
  for near-duplicates and hard-negatives are indistinguishable; or the assumption of localized human edits is violated in
  the dataset (edits are already uniform).
related_works:
- >-
  MinHash / LSH (Broder 1997, Manku 2007 SimHash): Estimates Jaccard similarity over k-shingles using random hash projections.
  These methods measure overlap quantity only — they have no mechanism to use spatial edit patterns. The proposed ECS is orthogonal
  and complements rather than replaces them.
- >-
  Normalized Compression Distance (NCD, Cilibrasi & Vitanyi 2005): Uses compression ratio of joint vs. individual compression
  as a similarity proxy. This measures information-theoretic overlap but also ignores spatial structure of differences.
- >-
  RETSim (Zhang et al. 2023, arXiv:2311.17264): A neural embedding model trained for near-duplicate detection with high throughput.
  It is a learned similarity metric and does not expose or exploit the spatial pattern of differences. ECS is training-free
  and interpretable.
- >-
  Adaptive Near-Duplicate Detection (Yih et al. 2004, ACM SIGIR): Uses learnable string similarity measures; focused on learning
  similarity metrics, not the geometric structure of diffs.
- >-
  Cluster-Based Plagiarism Detection (Zou et al. 2010, CLEF PAN): Uses TF-IDF clustering to detect copied text regions. The
  closest in spirit — it groups matching passages — but uses frequency vectors, not point-process statistics on diff positions,
  and targets cross-document passage reuse rather than pairwise near-duplicate classification.
inspiration: >-
  The key cross-domain transfer is from **spatial ecology and geography**: the Index of Dispersion and Ripley's K function
  are standard tools for classifying point patterns in 2D space as clustered (aggregated), random (Poisson), or regular (overdispersed).
  Ecologists use IoD to distinguish animal herding behavior (clustered occurrences) from randomly distributed species. Transplanting
  this to the 1D point process of edit positions in a text diff is the novel move: edit positions are the 'events', text length
  is the 'space', and the IoD distinguishes clustered human modifications (near-duplicates) from Poisson-like coincidental
  matches (hard negatives). This framing — treating the diff as a point process and testing its spatial statistics — does
  not appear in any text similarity or near-duplicate detection literature found during research.
terms:
- term: Edit Clustering Score (ECS)
  definition: >-
    The Index of Dispersion (variance divided by mean) of the sequence of gap lengths between consecutive edit operations
    in a word-level diff. Values much greater than 1 indicate clustered edits; values near 1 indicate uniformly random (Poisson-like)
    edits.
- term: Index of Dispersion (IoD)
  definition: >-
    A classical statistic from spatial point process analysis: IoD = variance(gaps) / mean(gaps). For a Poisson (random) process,
    IoD = 1. IoD > 1 indicates clustering (overdispersion); IoD < 1 indicates regularity (underdispersion).
- term: Word-level diff
  definition: >-
    A sequence alignment between two texts at the word token level using the longest common subsequence (LCS) algorithm, producing
    a list of matched and mismatched (inserted/deleted) tokens at specific positions.
- term: Hard negative
  definition: >-
    A pair of documents with high n-gram Jaccard similarity but which are NOT near-duplicates — e.g., two articles on the
    same topic sharing domain vocabulary and boilerplate but written independently.
- term: Near-duplicate
  definition: >-
    A text derived from another by localized human editing: inserting, deleting, or rewriting a contiguous region while leaving
    most of the original text intact.
summary: >-
  We hypothesize that the spatial clustering of edit positions in a word-level diff — quantified by the Index of Dispersion
  borrowed from spatial ecology — distinguishes genuine near-duplicates (clustered edits from local human modifications) from
  documents with coincidental n-gram overlap (uniformly scattered mismatches), providing an orthogonal signal that improves
  near-duplicate detection precision when combined with standard Jaccard similarity.
</hypothesis>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. Use it for the methods, proper baselines, and evaluation this field demands.

- **aii-handbook-multi-llm-agents** — Guide for implementing Multi-LLM Agent Systems research using Mirascope orchestration, HuggingFace datasets/evaluation, and proven multi-agent patterns.
</available_domain_handbooks>

<artifact_direction>
Make this direction concrete and actionable. Keep the same type and respect dependencies.

id: dataset_iter1_dir1
type: dataset
objective: >-
  Build a labeled benchmark of text pairs with three categories: near-duplicates (local splice edits), hard negatives (same-category
  Wikipedia articles), and random pairs. Each pair gets a label and metadata for fold assignment.
approach: >-
  Use the Wikipedia API (wikipedia Python package or requests to en.wikipedia.org/w/api.php) to fetch article text. Near-duplicates:
  take an article, replace a contiguous 20-40% word span with content from a random unrelated article, yielding a controlled
  local edit. Hard negatives: two different articles from the same Wikipedia category (fetched via category members API).
  Random pairs: articles from different categories. Target 300 pairs per category (900 total), storing {text_a, text_b, label,
  category, pair_id, fold} in data_out.json. Validate that hard-negative Jaccard scores overlap with near-duplicate Jaccard
  scores to confirm the hard-negative challenge.
depends_on: []
</artifact_direction>



<instructions>
YOUR ROLE: Write a detailed PLAN for the artifact. A separate executor agent runs the actual artifact later.

You are a PLANNER, not an executor. Your output is a plan that tells the executor what to do and how.
Do NOT execute the artifact itself — a separate agent handles that. Your job is to plan it so well that the executor can follow your plan step by step.

You CAN and SHOULD: search the web, read papers, and explore library docs to make your plan concrete.
You CANNOT run shell commands or scripts — code execution is disabled. Research via web tools only.

Do NOT do the executor's job: don't download datasets, don't implement code, don't run experiments, don't write proofs, don't compute evaluations.

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

DATASET executor scope:
  Output: data_out.json with rows of {input, output, metadata_fold, ...} — raw data only, no derived computations
  DOES: Download/generate datasets, analyze candidates to pick the best ones, standardize to JSON schema (features, labels, folds, metadata), validate schema, split into full/mini/preview
  DOES NOT: Run experiments, train models, compute derived statistics (PID/MI/correlations/synergy matrices) as final output
  If you need to COMPUTE something from data (synergy matrices, MI scores, timing benchmarks), use an EXPERIMENT artifact instead
</artifact_executor_scope>

<artifact_planning_rules>
DATASET:
- Plan for REAL third-party datasets (HuggingFace, Kaggle, direct-download URLs) — downloadable within time and size constraints
- Describe dataset criteria (domain, size, format) — executors find exact sources, but you can suggest candidates or search directions
- ALWAYS prefer real datasets over synthetic. Synthetic is a LAST RESORT only when no suitable real data exists
</artifact_planning_rules>

<compute_profiles>
Choose the compute profile this artifact needs for execution.
Available profiles for dataset artifacts:
  - gpu: 1x NVIDIA RTX A4500, 20GB VRAM, 7 vCPUs, 29GB RAM — ML training, CUDA, large models (fallback: GPUs cheap→expensive: 2000 Ada → A4000 → 4000 Ada → L4 → 4090 → 5090)
  - cpu_heavy: 4 vCPUs, 32GB RAM — large datasets, memory-intensive processing (fallback: CPUs cheap→expensive, then GPU hosts cheap→expensive (all ≥32GB RAM))

Set runpod_compute_profile to one of these exact tier names.
</compute_profiles>
GOOD PLANS: specific, actionable, consider failure scenarios, build on the suggested approach.
BAD PLANS: vague hand-waving, ignoring the suggested approach, missing critical executor details.
</instructions><user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "description": "Plan for a DATASET artifact.",
  "properties": {
    "title": {
      "description": "Plan title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters).",
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Brief summary",
      "title": "Summary",
      "type": "string"
    },
    "runpod_compute_profile": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "cpu_light",
      "description": "Compute tier for execution \u2014 pick from the available profiles list (e.g., 'gpu', 'cpu_heavy', 'cpu_light'). Only used in RunPod mode.",
      "title": "Runpod Compute Profile"
    },
    "ideal_dataset_criteria": {
      "description": "What makes an ideal dataset for this purpose - size, format, content requirements",
      "title": "Ideal Dataset Criteria",
      "type": "string"
    },
    "dataset_search_plan": {
      "description": "Step-by-step plan for finding/creating this dataset - sources to check, fallback options",
      "title": "Dataset Search Plan",
      "type": "string"
    },
    "target_num_datasets": {
      "description": "How many individual datasets should be delivered. Count each dataset separately, not collections \u2014 a benchmark suite of N datasets counts as N. This controls how broadly the executor searches, so setting it too low will under-collect.",
      "title": "Target Num Datasets",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "ideal_dataset_criteria",
    "dataset_search_plan",
    "target_num_datasets"
  ],
  "title": "DatasetPlan",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `./.terminal_claude_agent_struct_out.json`.
````

### [3] HUMAN-USER prompt · 2026-07-08 09:59:10 UTC

```
Propose a simple, novel, testable ML method for near-duplicate text detection and validate it with a tiny experiment.
```

### [4] TOOL CALL — Write · 2026-07-08 09:59:48 UTC

```
File: /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_plan/gen_plan_dataset_1/.terminal_claude_agent_struct_out.json

{
  "title": "Wikipedia Text Pair Benchmark (Near-Dup vs Hard Neg)",
  "summary": "Build 900 labeled text pairs from Wikipedia: 300 near-duplicates (splice edit), 300 hard negatives (same-category different articles), 300 random pairs. Output data_out.json with text_a, text_b, label, fold, and metadata.",
  "runpod_compute_profile": "cpu_heavy",
  "ideal_dataset_criteria": "900 text pairs total (300 per class). Each document should be 150-600 words after cleaning (Wikipedia section or short article). Near-duplicates must have Jaccard similarity in the range 0.3-0.8 (confirming the splice edit created real overlap). Hard negatives must also have Jaccard in 0.2-0.6 (same-topic vocabulary overlap but not near-copies) — this is the key challenge class. Random pairs should have Jaccard < 0.15. Pairs must include: text_a (str), text_b (str), label (str: 'near_duplicate'|'hard_negative'|'random'), pair_id (str), fold (int 0-4 for 5-fold CV), jaccard_5gram (float), word_count_a (int), word_count_b (int), category (str, the Wikipedia category used). All texts in English, minimum 100 words each.",
  "dataset_search_plan": "NO pre-existing dataset matches this exact task — the executor must build it synthetically from Wikipedia. Here is the step-by-step construction plan:\n\n## Step 1: Category discovery\nFetch a diverse set of Wikipedia categories via the API endpoint:\n  https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Featured_articles&cmlimit=500&format=json\nAlso use broad topic categories: 'Category:Geography', 'Category:History', 'Category:Science', 'Category:Technology', 'Category:Sports', 'Category:Politics', 'Category:Arts'. Aim for 30-50 categories with at least 10 members each.\n\n## Step 2: Article fetching\nUse the `wikipedia` PyPI package (pip install wikipedia-api) or direct requests to:\n  https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=false&titles=TITLE&format=json&explaintext=true\nFor each article, extract plain text, split into words, keep only articles with 200-800 words. Build a pool of ~500 articles organized by category.\n\n## Step 3: Near-duplicate construction (300 pairs)\nFor each pair:\n  a. Pick source article A (200+ words)\n  b. Pick a donor article B from a DIFFERENT category (to avoid topic bleed)\n  c. Compute splice_start = random position in [10%, 70%] of A's word count\n  d. splice_length = random in [20%, 40%] of A's word count\n  e. Replace words [splice_start : splice_start+splice_length] in A with the first splice_length words of B\n  f. text_a = original A, text_b = spliced version\n  g. Compute 5-gram Jaccard; REJECT and retry if Jaccard < 0.25 or > 0.85\n\n## Step 4: Hard negative construction (300 pairs)\nFor each pair:\n  a. Pick two DIFFERENT articles from the SAME Wikipedia category\n  b. They must not share more than 3 sentences (avoid accidental near-duplicates)\n  c. Compute 5-gram Jaccard; TARGET range 0.15-0.50\n  d. If Jaccard < 0.1, try another same-category pair; if still too low after 5 tries, accept it anyway\n  e. text_a = article 1, text_b = article 2\n\n## Step 5: Random pair construction (300 pairs)\nFor each pair:\n  a. Pick two articles from DIFFERENT categories\n  b. Compute 5-gram Jaccard; expect < 0.15\n  c. text_a = article 1, text_b = article 2\n\n## Step 6: Validation checks\n  - Verify Jaccard distribution: near_dup median > hard_neg median (expected ~0.6 vs ~0.25)\n  - Verify hard_neg and near_dup Jaccard ranges OVERLAP (this is the whole point — they must overlap to be a challenge)\n  - Verify no text_a or text_b appears in more than 2 pairs (avoid data leakage)\n  - Verify all texts >= 100 words\n  - Print a summary table: per-class Jaccard stats (min, median, max)\n\n## Step 7: Fold assignment\n  Assign fold 0-4 to each pair sequentially within each class (round-robin), so each fold has 60 per class = 180 total.\n\n## Step 8: Output\n  Write data_out.json as a JSON array of objects:\n  {\n    'pair_id': 'nd_001',\n    'text_a': '...',\n    'text_b': '...',\n    'label': 'near_duplicate',\n    'fold': 0,\n    'jaccard_5gram': 0.52,\n    'word_count_a': 312,\n    'word_count_b': 298,\n    'category': 'Geography',\n    'splice_start_pct': 0.35,   // near_dup only, else null\n    'splice_length_pct': 0.28   // near_dup only, else null\n  }\n  Also write data_out_mini.json (30 pairs, 10 per class) and data_out_preview.json (first 3 per class, truncated text to 200 chars).\n\n## Failure fallbacks\n  - If Wikipedia API rate-limits: add time.sleep(0.5) between requests; use the `wikipedia` package's built-in retry\n  - If a category has <5 articles: skip it, move to next\n  - If hard-negative Jaccard targets are not met after 50 attempts: relax to 0.05-0.6 and document in output metadata\n  - If total article pool < 300 after filtering: reduce word-count minimum to 80 words\n\n## Implementation notes\n  - Use `wikipedia` package: `pip install wikipedia` — simpler than raw API\n  - 5-gram Jaccard: tokenize by whitespace, extract all 5-word ngrams as frozensets, compute |A∩B|/|A∪B|\n  - Parallelize article fetching with ThreadPoolExecutor(max_workers=5) but respect rate limits\n  - Cache fetched articles to avoid re-downloading on retry\n  - Total expected runtime: 20-40 minutes (900 Wikipedia fetches at ~0.5s each with threading)\n  - No LLM calls needed — this is pure dataset construction ($0 spend)",
  "target_num_datasets": 1
}
```

### [5] TOOL RESULT — Write · 2026-07-08 09:59:48 UTC

```
{"type": "create", "filePath": "/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_plan/gen_plan_dataset_1/.terminal_claude_agent_struct_out.json", "content": "{\n  \"title\": \"Wikipedia Text Pair Benchmark (Near-Dup vs Hard Neg)\",\n  \"summary\": \"Build 900 labeled text pairs from Wikipedia: 300 near-duplicates (splice edit), 300 hard negatives (same-category different articles), 300 random pairs. Output data_out.json with text_a, text_b, label, fold, and metadata.\",\n  \"runpod_compute_profile\": \"cpu_heavy\",\n  \"ideal_dataset_criteria\": \"900 text pairs total (300 per class). Each document should be 150-600 words after cleaning (Wikipedia section or short article). Near-duplicates must have Jaccard similarity in the range 0.3-0.8 (confirming the splice edit created real overlap). Hard negatives must also have Jaccard in 0.2-0.6 (same-topic vocabulary overlap but not near-copies) — this is the key challenge class. Random pairs should have Jaccard < 0.15. Pairs must include: text_a (str), text_b (str), label (str: 'near_duplicate'|'hard_negative'|'random'), pair_id (str), fold (int 0-4 for 5-fold CV), jaccard_5gram (float), word_count_a (int), word_count_b (int), category (str, the Wikipedia category used). All texts in English, minimum 100 words each.\",\n  \"dataset_search_plan\": \"NO pre-existing dataset matches this exact task — the executor must build it synthetically from Wikipedia. Here is the step-by-step construction plan:\\n\\n## Step 1: Category discovery\\nFetch a diverse set of Wikipedia categories via the API endpoint:\\n  https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Featured_articles&cmlimit=500&format=json\\nAlso use broad topic categories: 'Category:Geography', 'Category:History', 'Category:Science', 'Category:Technology', 'Category:Sports', 'Category:Politics', 'Category:Arts'. Aim for 30-50 categories with at least 10 members each.\\n\\n## Step 2: Article fetching\\nUse the `wikipedia` PyPI package (pip install wikipedia-api) or direct requests to:\\n  https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=false&titles=TITLE&format=json&explaintext=true\\nFor each article, extract plain text, split into words, keep only articles with 200-800 words. Build a pool of ~500 articles organized by category.\\n\\n## Step 3: Near-duplicate construction (300 pairs)\\nFor each pair:\\n  a. Pick source article A (200+ words)\\n  b. Pick a donor article B from a DIFFERENT category (to avoid topic bleed)\\n  c. Compute splice_start = random position in [10%, 70%] of A's word count\\n  d. splice_length = random in [20%, 40%] of A's word count\\n  e. Replace words [splice_start : splice_start+splice_length] in A with the first splice_length words of B\\n  f. text_a = original A, text_b = spliced version\\n  g. Compute 5-gram Jaccard; REJECT and retry if Jaccard < 0.25 or > 0.85\\n\\n## Step 4: Hard negative construction (300 pairs)\\nFor each pair:\\n  a. Pick two DIFFERENT articles from the SAME Wikipedia category\\n  b. They must not share more than 3 sentences (avoid accidental near-duplicates)\\n  c. Compute 5-gram Jaccard; TARGET range 0.15-0.50\\n  d. If Jaccard < 0.1, try another same-category pair; if still too low after 5 tries, accept it anyway\\n  e. text_a = article 1, text_b = article 2\\n\\n## Step 5: Random pair construction (300 pairs)\\nFor each pair:\\n  a. Pick two articles from DIFFERENT categories\\n  b. Compute 5-gram Jaccard; expect < 0.15\\n  c. text_a = article 1, text_b = article 2\\n\\n## Step 6: Validation checks\\n  - Verify Jaccard distribution: near_dup median > hard_neg median (expected ~0.6 vs ~0.25)\\n  - Verify hard_neg and near_dup Jaccard ranges OVERLAP (this is the whole point — they must overlap to be a challenge)\\n  - Verify no text_a or text_b appears in more than 2 pairs (avoid data leakage)\\n  - Verify all texts >= 100 words\\n  - Print a summary table: per-class Jaccard stats (min, median, max)\\n\\n## Step 7: Fold assignment\\n  Assign fold 0-4 to each pair sequentially within each class (round-robin), so each fold has 60 per class = 180 total.\\n\\n## Step 8: Output\\n  Write data_out.json as a JSON array of objects:\\n  {\\n    'pair_id': 'nd_001',\\n    'text_a': '...',\\n    'text_b': '...',\\n    'label': 'near_duplicate',\\n    'fold': 0,\\n    'jaccard_5gram': 0.52,\\n    'word_count_a': 312,\\n    'word_count_b': 298,\\n    'category': 'Geography',\\n    'splice_start_pct': 0.35,   // near_dup only, else null\\n    'splice_length_pct': 0.28   // near_dup only, else null\\n  }\\n  Also write data_out_mini.json (30 pairs, 10 per class) and data_out_preview.json (first 3 per class, truncated text to 200 chars).\\n\\n## Failure fallbacks\\n  - If Wikipedia API rate-limits: add time.sleep(0.5) between requests; use the `wikipedia` package's built-in retry\\n  - If a category has <5 articles: skip it, move to next\\n  - If hard-negative Jaccard targets are not met after 50 attempts: relax to 0.05-0.6 and document in output metadata\\n  - If total article pool < 300 after filtering: reduce word-count minimum to 80 words\\n\\n## Implementation notes\\n  - Use `wikipedia` package: `pip install wikipedia` — simpler than raw API\\n  - 5-gram Jaccard: tokenize by whitespace, extract all 5-word ngrams as frozensets, compute |A∩B|/|A∪B|\\n  - Parallelize article fetching with ThreadPoolExecutor(max_workers=5) but respect rate limits\\n  - Cache fetched articles to avoid re-downloading on retry\\n  - Total expected runtime: 20-40 minutes (900 Wikipedia fetches at ~0.5s each with threading)\\n  - No LLM calls needed — this is pure dataset construction ($0 spend)\",\n  \"target_num_datasets\": 1\n}\n", "structuredPatch": [], "originalFile": null, "userModified": false}
```

### [6] ASSISTANT · 2026-07-08 09:59:51 UTC

```
Plan written to `.terminal_claude_agent_struct_out.json`. The plan builds 900 labeled Wikipedia text pairs (300 near-duplicates via splice edits, 300 same-category hard negatives, 300 random pairs) using the Wikipedia API with ThreadPoolExecutor for parallel fetching, 5-gram Jaccard validation to confirm class overlap, 5-fold assignments, and outputs data_out.json + mini/preview variants at $0 cost.
```
