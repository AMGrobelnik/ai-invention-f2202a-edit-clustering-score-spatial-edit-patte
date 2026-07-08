# gen_art_experiment_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_art`
> Run: `run_E1yko-FJ_C_D` — Edit Clustering Score: Spatial Edit Patterns for Near-Duplicate Text Detection
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_art_experiment_1` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-07-08 10:35:26 UTC

```
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: An artifact executor (Step 3.3: GEN_ART in the invention loop)

Executing a plan to produce a concrete artifact.
GEN_PAPER_TEXT will use your artifact in the next paper draft.

Rigorous artifact with clear results → strong paper. Sloppy artifact → misdirected research.
</your_role>
</ai_inventor_context>

<research_methodology>
Design experiments like a researcher, not a programmer running a script.

- Every method needs a meaningful baseline — the current standard approach, not a strawman.
- Control your variables. When comparing methods, hold everything else constant.
- Results need variance, not just point estimates. A single run proves nothing.
- Implement the proposed method and baseline side-by-side in the same pipeline to eliminate implementation-level confounds.
</research_methodology>

<task>
Implement the research methodology as a production-ready experimental system.
Adapt your implementation approach based on the hypothesis and domain requirements.
</task>

<critical_requirements>
- Fully implement the methodology described in hypothesis
- Use appropriate frameworks based on research domain
- Load and process data from the specified data_filepath
- Complete working systems
- Handle all edge cases, errors, and exceptions properly
- Always implement baseline comparison method
</critical_requirements>

<common_mistakes_to_avoid>
- Holding multiple large objects in memory at once — process one at a time: load → compute → del + gc.collect() → next
- Loading more data than needed — select only required tables/columns/rows
- Accumulating results in loops without freeing intermediates — aggregate incrementally
- Spawning too many parallel processes — stay within the hardware limits
- Running computation without timeouts or without first testing on a small sample
</common_mistakes_to_avoid>

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

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/`:
GOOD: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/file.py`, `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_experiment_1_idx2
type: experiment
title: ECS vs Jaccard on Wiki + Boilerplate Benchmarks
summary: >-
  Run Edit Clustering Score (inverted IoD) and Jaccard classifiers on both the original Wikipedia 900-pair benchmark and a
  new boilerplate-hard-negative benchmark. Key question: does inverted_ECS complement 2-gram Jaccard when Jaccard is degraded
  by boilerplate inflation? Pure CPU, $0 cost.
runpod_compute_profile: cpu_heavy
implementation_pseudocode: "## Step 1: Load dependency dataset\n\nDEP_DIR = '/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_dataset_1'\n\
  wiki_rows = json.load(open(f'{DEP_DIR}/full_data_out.json'))  # list of {input, output, pair_id, fold, ...}\n# Each row:\
  \ input = json string with {text_a, text_b}, output = label ('near_duplicate'|'hard_negative'|'random')\n\n## Step 2: Build\
  \ boilerplate-hard-negative benchmark (900 pairs, balanced)\n\n# Download Wikipedia articles using the Wikipedia API (requests,\
  \ no auth needed)\n# Strategy for boilerplate-hard-negative construction:\n#   - Near-duplicate (300 pairs): same as before\
  \ — take article A, splice 20-40% with donor from different category\n#   - Boilerplate-hard-negative (300 pairs): two DIFFERENT\
  \ articles from same category BUT\n#     prepend IDENTICAL boilerplate header (150-250 words: legal disclaimer text + date/attribution\
  \ block)\n#     so 5-gram Jaccard lands in [0.25, 0.55] due to shared boilerplate\n#   - Random (300 pairs): two articles\
  \ from different categories, no boilerplate\n#\n# Wikipedia categories to use (same 8 as iter1): science, history, arts,\
  \ sports, technology, nature, society, architecture\n# Fetch 30 articles per category via Wikipedia API:\n#   url = f'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat}&cmlimit=50&format=json'\n\
  #   then for each article: extract first 150-600 words of clean text\n#\n# Boilerplate text (fixed string, ~180 words):\n\
  #   'This article is provided under the Creative Commons Attribution-ShareAlike License. \n#    All content is for informational\
  \ purposes only. Last updated: January 2024. \n#    Reproduction permitted with attribution. The views expressed do not\
  \ represent \n#    any organization. See terms at creativecommons.org/licenses/by-sa/3.0/ ...'\n#   (repeat/extend to ~180\
  \ words)\n#\n# For boilerplate-hard-neg pair: text_a = boilerplate + article_X, text_b = boilerplate + article_Y\n#   where\
  \ X != Y, same category, verify resulting 5-gram Jaccard in [0.2, 0.6]\n# For near-duplicate pair: text_a = article_X, text_b\
  \ = splice(article_X, donor_Y)\n#   splice: replace words[start:end] with words from donor_Y, start/end = random 20-40%\
  \ contiguous block\n# For random pair: text_a = article from cat_i, text_b = article from cat_j (i != j)\n#\n# Assign fold\
  \ 0-4 round-robin per class\n# Save as boilerplate_data.json in same schema as full_data_out.json\n\n## Step 3: Feature\
  \ extraction function\n\nimport difflib, re, math, numpy as np\n\ndef tokenize(text):\n    return re.findall(r'\\b\\w+\\\
  b', text.lower())\n\ndef jaccard_ngram(a_tokens, b_tokens, n):\n    a_shingles = set(zip(*[a_tokens[i:] for i in range(n)]))\n\
  \    b_shingles = set(zip(*[b_tokens[i:] for i in range(n)]))\n    if not a_shingles and not b_shingles: return 0.0\n  \
  \  return len(a_shingles & b_shingles) / len(a_shingles | b_shingles)\n\ndef compute_ecs(a_tokens, b_tokens):\n    \"\"\"\
  \n    Returns dict with ECS metrics.\n    Uses difflib.SequenceMatcher to get opcodes.\n    Edit positions: for each non-equal\
  \ opcode, record the midpoint position\n    in the combined sequence. Compute inter-edit-gap lengths.\n    ECS = IoD = var(gaps)\
  \ / mean(gaps). Low IoD = clustered = near-duplicate signal.\n    inverted_ECS = 1 / (1 + ECS).\n    longest_run_frac =\
  \ longest contiguous equal block / total tokens.\n    edit_count_norm = n_edit_ops / (len(a)+len(b)).\n    \"\"\"\n    matcher\
  \ = difflib.SequenceMatcher(None, a_tokens, b_tokens, autojunk=False)\n    opcodes = matcher.get_opcodes()\n    \n    #\
  \ edit positions: use a_start of each non-equal block, normalized to [0,1]\n    total_len = max(len(a_tokens), 1)\n    edit_positions\
  \ = [op[1] / total_len for op in opcodes if op[0] != 'equal']\n    \n    # inter-edit gaps (in token units, not normalized)\n\
  \    edit_pos_raw = [op[1] for op in opcodes if op[0] != 'equal']\n    gaps = [edit_pos_raw[i+1] - edit_pos_raw[i] for i\
  \ in range(len(edit_pos_raw)-1)]\n    \n    if len(gaps) < 2:\n        iod = 0.0  # single edit block = maximally clustered\n\
  \    else:\n        mu = np.mean(gaps)\n        var = np.var(gaps)\n        iod = var / mu if mu > 0 else 0.0\n    \n  \
  \  inv_ecs = 1.0 / (1.0 + iod)\n    \n    # longest equal run\n    equal_lengths = [op[4]-op[3] for op in opcodes if op[0]\
  \ == 'equal']\n    longest_run = max(equal_lengths) if equal_lengths else 0\n    longest_run_frac = longest_run / total_len\n\
  \    \n    n_edit_ops = sum(1 for op in opcodes if op[0] != 'equal')\n    edit_count_norm = n_edit_ops / (len(a_tokens)\
  \ + len(b_tokens) + 1)\n    \n    return {\n        'ecs': iod,\n        'inv_ecs': inv_ecs,\n        'longest_run_frac':\
  \ longest_run_frac,\n        'edit_count_norm': edit_count_norm,\n        'n_edit_positions': len(edit_pos_raw)\n    }\n\
  \ndef extract_features(row):\n    inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']\n  \
  \  ta, tb = inp['text_a'], inp['text_b']\n    ta_tok, tb_tok = tokenize(ta), tokenize(tb)\n    j5 = jaccard_ngram(ta_tok,\
  \ tb_tok, 5)\n    j2 = jaccard_ngram(ta_tok, tb_tok, 2)\n    ecs_feats = compute_ecs(ta_tok, tb_tok)\n    return {\n   \
  \     'jaccard_5gram': j5,\n        'jaccard_2gram': j2,\n        **ecs_feats,\n        'label': row['output'],\n      \
  \  'fold': row.get('fold', 0)\n    }\n\n## Step 4: Extract features for both datasets\n\nwiki_features = [extract_features(r)\
  \ for r in wiki_rows]\nboilerplate_features = [extract_features(r) for r in boilerplate_rows]\n\n## Step 5: Classifier evaluation\
  \ (5-fold CV)\n\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\n\
  from sklearn.metrics import roc_auc_score\nfrom sklearn.preprocessing import StandardScaler\nimport scipy.stats as stats\n\
  \ndef run_cv(features_list, feature_sets, label_map):\n    \"\"\"\n    feature_sets: dict of name -> list of feature column\
  \ names\n    label_map: which labels to use as binary (1=positive, 0=negative)\n    Returns dict of {feature_set_name: {auc_mean,\
  \ auc_std, fold_aucs}}\n    \"\"\"\n    df = pd.DataFrame(features_list)\n    df['y'] = df['label'].map(label_map)\n   \
  \ df = df.dropna(subset=['y'])\n    \n    results = {}\n    for fs_name, cols in feature_sets.items():\n        fold_aucs\
  \ = []\n        for fold in range(5):\n            train = df[df['fold'] != fold]\n            test = df[df['fold'] == fold]\n\
  \            if len(test['y'].unique()) < 2: continue\n            \n            X_train = train[cols].fillna(0).values\n\
  \            X_test = test[cols].fillna(0).values\n            y_train = train['y'].values\n            y_test = test['y'].values\n\
  \            \n            scaler = StandardScaler()\n            X_train = scaler.fit_transform(X_train)\n            X_test\
  \ = scaler.transform(X_test)\n            \n            clf = LogisticRegression(max_iter=1000, C=1.0)\n            clf.fit(X_train,\
  \ y_train)\n            probs = clf.predict_proba(X_test)[:, 1]\n            auc = roc_auc_score(y_test, probs)\n      \
  \      fold_aucs.append(auc)\n        \n        results[fs_name] = {\n            'auc_mean': np.mean(fold_aucs),\n    \
  \        'auc_std': np.std(fold_aucs),\n            'fold_aucs': fold_aucs\n        }\n    return results\n\n# Define feature\
  \ sets\nfeature_sets = {\n    'jaccard5_only': ['jaccard_5gram'],\n    'jaccard2_only': ['jaccard_2gram'],\n    'inv_ecs_only':\
  \ ['inv_ecs'],\n    'jaccard5_inv_ecs': ['jaccard_5gram', 'inv_ecs'],\n    'jaccard2_inv_ecs': ['jaccard_2gram', 'inv_ecs'],\n\
  \    'all_features': ['jaccard_5gram', 'jaccard_2gram', 'inv_ecs', 'longest_run_frac', 'edit_count_norm']\n}\n\n# Evaluation\
  \ 1: near_duplicate vs hard_negative (main discriminative task)\nlabel_map_hard = {'near_duplicate': 1, 'hard_negative':\
  \ 0}  # exclude random\n\nwiki_results = run_cv(wiki_features, feature_sets, label_map_hard)\nboilerplate_results = run_cv(boilerplate_features,\
  \ feature_sets, label_map_hard)\n\n# Evaluation 2: near_duplicate vs ALL negatives (overall task)\nlabel_map_all = {'near_duplicate':\
  \ 1, 'hard_negative': 0, 'random': 0}\nwiki_results_all = run_cv(wiki_features, feature_sets, label_map_all)\nboilerplate_results_all\
  \ = run_cv(boilerplate_features, feature_sets, label_map_all)\n\n## Step 6: Bootstrap CI for delta_AUC on boilerplate benchmark\n\
  \ndef bootstrap_delta_auc(features_list, col_a, col_b, label_map, B=2000):\n    \"\"\"Bootstrap CI for AUC(col_b) - AUC(col_a)\
  \ on full pooled data.\"\"\"\n    df = pd.DataFrame(features_list)\n    df['y'] = df['label'].map(label_map)\n    df = df.dropna(subset=['y'])\n\
  \    if len(df['y'].unique()) < 2: return None\n    \n    deltas = []\n    for _ in range(B):\n        sample = df.sample(n=len(df),\
  \ replace=True)\n        Xa = sample[col_a].fillna(0).values.reshape(-1,1)\n        Xb = sample[col_b if isinstance(col_b,\
  \ list) else [col_b]].fillna(0).values\n        y = sample['y'].values\n        if len(np.unique(y)) < 2: continue\n   \
  \     \n        sc = StandardScaler()\n        clf_a = LogisticRegression(max_iter=500).fit(sc.fit_transform(Xa), y)\n \
  \       clf_b = LogisticRegression(max_iter=500).fit(sc.fit_transform(Xb), y)\n        \n        auc_a = roc_auc_score(y,\
  \ clf_a.predict_proba(sc.transform(Xa))[:, 1])\n        auc_b = roc_auc_score(y, clf_b.predict_proba(sc.transform(Xb))[:,\
  \ 1])\n        deltas.append(auc_b - auc_a)\n    \n    deltas = np.array(deltas)\n    return {'mean': float(np.mean(deltas)),\
  \ 'ci_lo': float(np.percentile(deltas, 2.5)), 'ci_hi': float(np.percentile(deltas, 97.5))}\n\n# KEY comparison: jaccard2+inv_ecs\
  \ vs jaccard2 alone on boilerplate benchmark\ndelta_boilerplate = bootstrap_delta_auc(\n    boilerplate_features,\n    col_a=['jaccard_2gram'],\n\
  \    col_b=['jaccard_2gram', 'inv_ecs'],\n    label_map=label_map_hard, B=2000\n)\n\n## Step 7: Mann-Whitney U on IoD distributions\n\
  \ndef mann_whitney_iod(features_list):\n    df = pd.DataFrame(features_list)\n    nd = df[df['label']=='near_duplicate']['ecs'].dropna()\n\
  \    hn = df[df['label']=='hard_negative']['ecs'].dropna()\n    u, p = stats.mannwhitneyu(nd, hn, alternative='less')  #\
  \ near-dup IoD < hard-neg IoD\n    return {\n        'median_iod_near_dup': float(nd.median()),\n        'median_iod_hard_neg':\
  \ float(hn.median()),\n        'mann_whitney_p': float(p),\n        'n_near_dup': len(nd), 'n_hard_neg': len(hn)\n    }\n\
  \nwiki_mw = mann_whitney_iod(wiki_features)\nboilerplate_mw = mann_whitney_iod(boilerplate_features)\n\n## Step 8: Assemble\
  \ method_out.json\n\noutput = {\n    'wiki_benchmark': {\n        'cv_results_hard_subset': wiki_results,\n        'cv_results_all_labels':\
  \ wiki_results_all,\n        'mann_whitney_iod': wiki_mw\n    },\n    'boilerplate_benchmark': {\n        'cv_results_hard_subset':\
  \ boilerplate_results,\n        'cv_results_all_labels': boilerplate_results_all,\n        'mann_whitney_iod': boilerplate_mw,\n\
  \        'delta_auc_jaccard2_plus_inv_ecs_vs_jaccard2': delta_boilerplate\n    },\n    'key_findings': {\n        'inv_ecs_auc_wiki_hard':\
  \ wiki_results['inv_ecs_only']['auc_mean'],\n        'inv_ecs_auc_boilerplate_hard': boilerplate_results['inv_ecs_only']['auc_mean'],\n\
  \        'delta_auc_boilerplate_ci_lo': delta_boilerplate['ci_lo'],\n        'hypothesis_confirmed': boilerplate_results['jaccard2_inv_ecs']['auc_mean']\
  \ - boilerplate_results['jaccard2_only']['auc_mean'] >= 0.03\n    }\n}\n\njson.dump(output, open('method_out.json', 'w'),\
  \ indent=2)\nprint('Done. Key AUC delta:', delta_boilerplate)"
fallback_plan: |-
  If Wikipedia API is rate-limited or slow during boilerplate benchmark construction:
  - Use the EXISTING wiki benchmark's articles: re-pair same-category articles and prepend a fixed boilerplate string of ~180 words (no new downloads needed). The iter1 dataset stores category per pair, so articles of the same category can be re-paired.
  - If that yields fewer than 300 boilerplate-hard-neg pairs, reduce to 150 per class (450 total) and note the smaller sample in output.

  If IoD is undefined for pairs with 0 or 1 edit positions (very short texts or near-identical pairs):
  - Assign ECS=0 (maximally clustered, single block) and inv_ecs=1.0. Document this imputation.

  If 5-fold CV folds are missing from the dependency data (fold key absent):
  - Assign folds round-robin by pair_id modulo 5.

  If sklearn or scipy not available:
  - Implement AUC manually via trapezoid rule on sorted predictions; Mann-Whitney via rank-sum formula. All are pure numpy.
testing_plan: |-
  MINI TEST (first 60 rows of wiki benchmark, ~10 seconds):
  1. Load first 60 rows from full_data_out.json (20 per class).
  2. Run extract_features on all 60 — verify no crashes, all 6 features produced, no NaN in jaccard_5gram.
  3. Check median IoD: near_duplicate rows should have lower IoD than hard_negative rows (print medians).
  4. Run a single train/test split (fold 0 as test), fit LogisticRegression on ['jaccard_5gram'] vs ['inv_ecs'], verify both produce a valid AUC (not NaN, in [0,1]).
  5. Print 3 sample feature rows to visually sanity-check values are in expected ranges: jaccard_5gram in [0,1], inv_ecs in (0,1], longest_run_frac in (0,1].

  CONFIRMATION SIGNALS before full run:
  - At least one feature set produces AUC > 0.7 on the mini test (otherwise feature extraction is broken)
  - IoD median for near_dup < IoD median for hard_neg on mini test (validates directional hypothesis)
  - Boilerplate pairs (after construction) have 5-gram Jaccard in [0.15, 0.65] — print histogram

  FULL RUN: only proceed after mini test passes. Full run estimated <5 minutes on CPU.
</artifact_plan>

<dependencies>
Read the files in these dependency workspaces to understand what's available, then copy any you need into your working directory.

--- Dependency 1 ---
id: art_of-sMCpCSjl5
type: dataset
title: Wikipedia Text Pair Benchmark Dataset
summary: >-
  This artifact provides the Wikipedia Text Pair Benchmark, a synthetic dataset of 900 labeled text pairs built from Wikipedia
  articles via the Wikipedia API. The dataset contains three balanced classes (300 each): (1) near_duplicate pairs where text_b
  is a splice-edited version of text_a with 20-40% of words replaced by content from a donor article from a different category,
  producing 5-gram Jaccard similarity of 0.42-0.70 (median 0.54); (2) hard_negative pairs of two different articles from the
  same Wikipedia category, capturing thematic overlap without textual duplication (5-gram Jaccard near 0, emphasizing the
  semantic difficulty); and (3) random pairs of articles from different categories serving as easy negatives (5-gram Jaccard
  ~0). All texts are 80-800 words in English, drawn from 220 Wikipedia articles across 8 categories: science, history, arts,
  sports, technology, nature, society, and architecture. Each pair includes: text_a, text_b, label, pair_id, fold (0-4 for
  5-fold cross-validation), jaccard_5gram, word_count_a, word_count_b, category, and splice_start_pct/splice_length_pct (near_duplicate
  only). The dataset is formatted in the exp_sel_data_out schema with input as a JSON string containing text_a and text_b,
  and output as the class label. Key insight: 5-gram Jaccard cleanly separates near-duplicates from the other two classes,
  making it a useful baseline feature, while the hard_negative class tests whether models can detect category-level topical
  similarity vs. near-textual-copy. Dataset is $0 cost (no LLM calls), built entirely from the Wikipedia API.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json

Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</dependencies>

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

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. Use it for framework choices, implementation patterns, agent orchestration.

- **aii-handbook-multi-llm-agents** — Guide for implementing Multi-LLM Agent Systems research using Mirascope orchestration, HuggingFace datasets/evaluation, and proven multi-agent patterns.
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-python, aii-long-running-tasks, aii-json, aii-file-size-limit, aii-use-hardware, aii-parallel-computing.
TODO 2. Read preview files from dependencies to understand data structure. Use ALL datasets provided — do not skip or select a subset. Read domain handbook if applicable (see <available_domain_handbooks>). Test basic functionality with 'uv run'.
TODO 3. Fully implement our method AND baseline (comparison) as described in artifact plan in './method.py'. Use exp_gen_sol_out.json schema in aii-json skill for output format validation. Include everything specified in the artifact plan, but you may also implement additional relevant methods or analysis beyond what's listed. Be very attentive to meticulously and exhaustively fix any errors in your code.
</todos>
```

### [2] HUMAN-USER prompt · 2026-07-08 10:35:26 UTC

```
Propose a simple, novel, testable ML method for near-duplicate text detection and validate it with a tiny experiment.
```

### [3] SKILL-INPUT — aii-python · 2026-07-08 10:35:48 UTC

The agent loaded the **aii-python** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-python
description: Python coding standards for experiment and evaluation scripts. Covers environment setup, logging, error handling, and code structure.
---

## Environment Setup

- Python 3.12+
- **NEVER use `pip` or `.venv/bin/pip`** — they are not installed. Use `uv` for ALL package operations:
  ```bash
  uv venv .venv --python=3.12
  source .venv/bin/activate  # or: .venv/bin/python script.py
  uv pip install pandas loguru  # NOT: pip install
  ```
- Create `.toml` file with dependencies, create uv `.venv` and activate it
- NO inline dependencies (no `# /// script` headers)

## Logging

Use `loguru` for all logging. Add a file sink alongside stdout.

```python
from loguru import logger
import sys

logger.remove()  # Remove default handler
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")
```

Rules:
- Log every major step (data loading, processing start/end, results)
- If applicable, log every LLM API call input and output
- Truncate long outputs in logs (add truncation logic for potentially large strings)
- Use `logger.error()` in except blocks (traceback auto-captured)

## Error Handling

- Wrap major operations in try/except blocks
- Use `@logger.catch(reraise=True)` decorator on main functions — without `reraise=True`, the script exits 0 even on uncaught exceptions, hiding failures from downstream consumers
- Use explicit exception types, not bare `except:`
- Never silently swallow exceptions — always log them

```python
@logger.catch(reraise=True)
def main():
    try:
        data = load_data(path)
    except FileNotFoundError:
        logger.error("Data file not found")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in data file")
        raise
```

## Code Structure

- Use `pathlib.Path` for file operations: `Path("data/input.json").read_text()` not `open(...).read()`
- Use type hints for function signatures
- Use keyword arguments for functions with more than 4 parameters
- No hardcoded paths — derive from script location or accept as arguments

## Script Pattern

Standard pattern for experiment/evaluation scripts:

```python
#!/usr/bin/env python3
"""Brief description of what this script does."""

from loguru import logger
from pathlib import Path
import json
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def main():
    # Load data
    data_path = Path("full_data_out.json")
    logger.info(f"Loading data from {data_path}")
    data = json.loads(data_path.read_text())
    logger.info(f"Loaded {len(data['examples'])} examples")

    # Process
    results = []
    for i, example in enumerate(data["examples"]):
        try:
            result = process(example)
            results.append(result)
        except Exception:
            logger.error(f"Failed on example {i}")
            continue

    # Save output
    output = {"examples": results}
    Path("method_out.json").write_text(json.dumps(output, indent=2))
    logger.info(f"Saved {len(results)} results")

if __name__ == "__main__":
    main()
```
````

### [4] SKILL-INPUT — aii-long-running-tasks · 2026-07-08 10:35:48 UTC

The agent loaded the **aii-long-running-tasks** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-long-running-tasks
description: Gradual scaling pattern for long-running autonomous tasks. Use when running experiments, evaluations, or any code that processes data at increasing scale with runtime checks.
---

## Core Principles

1. **Time budget first**: Read your time/runtime constraints before running anything. Set every Bash timeout to fit within the budget.
2. **Start small, scale up**: Run on minimal input first, fix errors, then increase scale.
3. **Extrapolate before scaling**: Use recorded runtimes to predict whether the next step fits in the budget. Don't guess — calculate.
4. **Background execution**: For anything that takes >1 min, run in background (`run_in_background=true`) and do useful work while waiting.
5. **Stop early if needed**: Quality results on less data beats a timeout or crash. It's always acceptable to stop at a smaller scale.

---

## Gradual Scaling Sequence

Run code at increasing data sizes, checking runtime at each step.

Substitute your actual file names:
- `{mini_file}` — mini JSON (3 examples) from dependency workspace
- `{full_file}` — full dataset from dependency workspace
- `{script}` — your processing script (e.g., `./method.py`, `./eval.py`)
- `{schema}` — JSON schema to validate output against

**STEP 1 — MINI DATA:** Run `{script}` on `{mini_file}`. Do NOT truncate logs. Fix all errors. Validate output against `{schema}`. Verify you are NOT using mock scripts, mock data, or mock APIs.

**STEP 2 — 10 EXAMPLES:** Modify `{script}` to load only the first 10 examples from `{full_file}`. Run and fix errors. Validate schema. Record the runtime.

**STEP 3 — 50 EXAMPLES:** Load first 50 examples from `{full_file}`. Run and fix errors. Record runtime. **EXTRAPOLATE**: Using runtimes from steps 2-3, estimate time per example. Calculate how many examples fit in your remaining time budget. If 50 already used most of the budget, stop here.

**STEP 4 — 100 EXAMPLES (if budget allows):** Load first 100 examples. Run and fix errors. Record runtime. Re-extrapolate with the new data point.

**STEP 5 — 200 EXAMPLES (if budget allows):** Load first 200 examples from `{full_file}`. Run and fix errors. Record runtime.

**STEP 6 — MAXIMIZE:** Using all recorded runtimes, extrapolate time-per-example (it may not be perfectly linear — account for overhead). Calculate the maximum number of examples that fits within your remaining time budget with a 10% safety margin. Load that many (or all if they fit). Run and validate.

## Final Testing Phase

After completing the scaling sequence, redo the entire sequence **one more time** up to your final example count:

mini → 10 → 50 → 100 → 200 → max

At each scale: look for issues, fix problems, validate output, ensure it completes within time limits.

---

## Background Execution

For any step that takes >1 min, run as a **background task**:

1. Launch with Bash `run_in_background=true`
2. While it runs, use the time productively:
   - Sanity-check previous outputs
   - Verify file integrity (correct field names, non-empty values)
   - Review code for edge cases at larger scale
   - Prepare the next step
3. Check back on the background task to get results
4. If it failed, fix errors and re-run

---

## Resource Limits

Set hard RAM and CPU time limits so code fails fast instead of crashing the system. Read limits from `<hardware>` and leave headroom for the OS (e.g., if 16GB total, cap at 14GB).

Python example using stdlib `resource` module:
```python
import resource
resource.setrlimit(resource.RLIMIT_AS, (14 * 1024**3, 14 * 1024**3))  # 14GB RAM
resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))  # 1 hour CPU time
```
Exceeding RAM raises `MemoryError`. Exceeding CPU time sends `SIGKILL`.

## Monitoring

At each step, record runtime AND check resource usage (`free -h` for RAM, `top -bn1 | head -5` for CPU). If memory usage is climbing toward the limit or CPU is pegged, stop and investigate before scaling further.
````

### [5] SKILL-INPUT — aii-json · 2026-07-08 10:35:48 UTC

The agent loaded the **aii-json** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-json
description: JSON validation and formatting toolkit. Validate JSON files against schemas for experiment pipelines, and generate full/mini/preview versions of JSON datasets. Use for validating pipeline outputs, checking schema compliance, or creating size-optimized JSON variants.
---

## Contents

- Validating JSON (schema validation against experiment schemas)
- Formatting JSON (generate full/mini/preview versions)

**IMPORTANT - Parallel execution:** GNU `parallel` subshells do NOT inherit `source activate`. Use `export` for variables and **single-quoted** command templates so parallel's subshells can resolve them:
```
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

---

## Validating JSON

Validate JSON files against predefined schemas for experiment-based hypothesis selection, data collection, solution generation, and evaluation.

### Quick Start

1. Read the schema spec you need to adhere to (e.g., `schemas/exp_eval_sol_out.json`)
2. Create your output file following that schema structure
3. Validate:

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /path/to/eval_out.json
```

### Script: aii_json_validate_schema.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /tmp/eval_out.json
```

**Parallel execution (multiple validations):**

IMPORTANT: When validating multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_validate_schema.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --format {1} --file {2}' ::: 'exp_sel_data_out' 'exp_gen_sol_out' 'exp_eval_sol_out' :::+ '/tmp/full_data_out.json' '/tmp/method_out.json' '/tmp/eval_out.json'
```

**Example output (success):**
```
Validating: aii_json_validate_schema.py
Format: exp_eval_sol_out

✓ Validation PASSED
```

**Example output (failure):**
```
Validating: aii_json_validate_schema.py
Format: exp_sel_data_out

✗ Validation FAILED

Errors:
  Path: datasets → 0 → examples → 0
  Error: 'output' is a required property
  Validator: required
```

**Parameters:**

`--format` (required)
- Format type to validate against
- Determines which schema to use

`--file` (required)
- Path to JSON file to validate
- Must be valid JSON
- **Always pass an absolute path.** Relative paths resolve from the
  ability server's CWD (typically ``/ai-inventor/aii_server``), not from
  your agent workspace, so ``data_out/x.json`` will silently look in the
  wrong directory and fail with "Could not load JSON file". The validate
  endpoint also accepts a ``workspace_dir`` arg if you need to keep a
  relative path — pass your workspace path there.

**Tips:**
- Fix errors in your JSON and rerun validation until it passes

### Schema Files

Schemas are stored in `.claude/skills/aii-json/schemas/`:

**Hypothesis Selection & Evaluation:**
- `sel_hypo_out.json` - Hypothesis Selection output (all hypotheses with selected flags)
- `feasibility_eval_all.json` - All hypotheses with feasibility scores
- `feasibility_eval_top.json` - Top 5 most feasible hypotheses
- `novelty_research_one.json` - Single hypothesis novelty research arguments with citations
- `novelty_eval_all.json` - All hypotheses with novelty scores
- `novelty_eval_top.json` - Single best selected hypothesis

**Experiment Pipeline:**
- `exp_sel_data_out.json` - Experiment Data Selection format
- `exp_gen_sol_out.json` - Experiment Solution Generation format
- `exp_eval_sol_out.json` - Experiment Solution Evaluation format

---

## Formatting JSON

Generate three size-optimized versions of a JSON file for efficient development and preview:
- **full**: Identical to original (all data)
- **mini**: First 3 items only (for quick testing)
- **preview**: Mini + all strings truncated to 200 chars (for quick inspection)

### Quick Start

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

### Script: aii_json_format_mini_preview.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

**Parallel execution (multiple files):**

IMPORTANT: When formatting multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_format_mini_preview.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --input {}' ::: 'full_data_out.json' 'method_out.json' 'eval_out.json'
```

**Example output:**
```
Generated 3 versions:
  Full (50 items): /path/to/full_method_out.json
  Mini (3 items): /path/to/mini_method_out.json
  Preview (3 items, truncated): /path/to/preview_method_out.json
```

**Parameters:**

`--input` (required)
- Path to input JSON file
- Must have a top-level array
- Example: `method_out.json`, `full_data_out.json`

`--output-dir` (optional)
- Output directory for generated files
- Default: same directory as input file
- Files are prefixed with `full_`, `mini_`, `preview_`

**Output Files:**

All three files use the same base name with different prefixes:
- `full_{basename}.json` - Complete dataset (identical to original)
- `mini_{basename}.json` - First 3 array items only
- `preview_{basename}.json` - First 3 items with strings truncated to 200 chars

**Tips:**
- Input JSON must have a top-level array structure
- String truncation is recursive (applies to nested objects and arrays)
- Use preview files for quick inspection without reading large datasets
- Use mini files for developing/testing code before running on full dataset

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [6] SKILL-INPUT — aii-file-size-limit · 2026-07-08 10:35:56 UTC

The agent loaded the **aii-file-size-limit** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

```
---
name: aii-file-size-limit
description: File size check procedure for splitting oversized output files. Use after generating JSON output files to check and split files exceeding the provided size limit.
---

## File Size Check

After generating output files, run `ls -lh` to check sizes. If ANY file exceeds the provided file size limit:

1. Create directory with same base name (e.g., `data_out/` for `full_data_out.json`)
2. Split into parts under the limit named: `full_data_out_1.json`, `full_data_out_2.json`, etc.
3. Place parts in directory (e.g., `data_out/full_data_out_1.json`, `data_out/full_data_out_2.json`)
4. Delete the original oversized file
5. Update the script to read from split files: `for f in sorted(glob.glob('data_out/full_data_out_*.json')): data.extend(json.load(open(f)))`
6. For each split part, generate its own mini/preview versions with the json skill's format script
```

### [7] SKILL-INPUT — aii-use-hardware · 2026-07-08 10:35:56 UTC

The agent loaded the **aii-use-hardware** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-use-hardware
description: Detect hardware and use it responsibly. Covers CPU/RAM/GPU detection, memory-safe data processing, and resource-aware computation.
---

**Step 1** — Run `bash scripts/get_hardware.sh` (relative to this skill's directory).

Read the `=== CGROUP ===` section carefully. If `Type: cgroup v1` or `cgroup v2`:
- You are in a **container with hard resource limits**. Exceeding them = OOM kill, no recovery.
- **Never** use `psutil.virtual_memory().total`, `free -h`, `/proc/meminfo`, `os.cpu_count()`, or `nproc` for resource limits — these report **host** values, not your container's allocation.
- **Always** read limits from the cgroup paths shown in the output, or use the Python helpers below.
- For **runtime memory monitoring**, read current usage from cgroup too:
  - v2: `/sys/fs/cgroup/memory.current`
  - v1: `/sys/fs/cgroup/memory/memory.usage_in_bytes`

**Step 2** — Use Step 1 results to pick package variants **before** installing.

Defaults often target the most powerful environment — PyPI's `torch` ships with CUDA libs even on CPU-only hosts. Wrong variant = wasted disk, slow setup, possible import-time failures.

If `=== GPU ===` shows `No GPU`, install torch's CPU build (skips ~4.5GB of CUDA libs):
```bash
uv pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
```
Same idea for any library whose wheel selection depends on detected hardware (GPU/CPU-only builds, architecture-specific wheels).

After install, sanity-check imports right away (`python -c "import torch"`). Disk-pressure or interrupted installs leave half-built wheels (e.g. `libtorch_global_deps.so` missing) — catch these before the experiment runs.

**Step 3** — Set Python constants from the Step 1 results:
```python
import os, math, torch, psutil
from pathlib import Path

def _detect_cpus() -> int:
    """Detect actual CPU allocation (containers/pods/bare metal)."""
    try:  # cgroups v2 quota
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError): pass
    try:  # cgroups v1 quota
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError): pass
    try:  # CPU affinity (cpuset — used by RunPod, Docker --cpuset-cpus)
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError): pass
    return os.cpu_count() or 1

def _container_ram_gb() -> float | None:
    """Read RAM limit from cgroup (containers/pods)."""
    for p in ["/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"]:
        try:
            v = Path(p).read_text().strip()
            if v != "max" and int(v) < 1_000_000_000_000:
                return int(v) / 1e9
        except (FileNotFoundError, ValueError): pass
    return None

NUM_CPUS = _detect_cpus()
HAS_GPU = torch.cuda.is_available()
VRAM_GB = torch.cuda.get_device_properties(0).total_mem / 1e9 if HAS_GPU else 0
DEVICE = torch.device("cuda" if HAS_GPU else "cpu")
TOTAL_RAM_GB = _container_ram_gb() or psutil.virtual_memory().total / 1e9
AVAILABLE_RAM_GB = min(psutil.virtual_memory().available / 1e9, TOTAL_RAM_GB)
```

## Step 4 — Set Memory Limits

OOM kills the entire container. **Every script MUST set RAM and VRAM limits at startup.**

Decide the budget based on what the script actually needs. Estimate data size × 2-5x for in-memory overhead, then add ~50% breathing room for temporaries. You may use up to 90% of available RAM/VRAM, but **scale gradually** — start small (e.g. 30-50%), verify it works, then increase toward the limit. Never exceed 90% to keep a buffer for the OS, system processes, and the agent runtime itself. Going over crashes the container/machine with no recovery.

```python
import resource, psutil

_avail = psutil.virtual_memory().available
RAM_BUDGET = ???  # YOU decide: estimate what this script needs (in bytes)
assert RAM_BUDGET < _avail, f"Budget {RAM_BUDGET/1e9:.1f}GB > available {_avail/1e9:.1f}GB"
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))  # 3x: virtual > RSS; raises MemoryError on exceed

if HAS_GPU:
    _free, _total = torch.cuda.mem_get_info(0)
    VRAM_BUDGET = ???  # YOU decide: estimate GPU memory needs
    torch.cuda.set_per_process_memory_fraction(min(VRAM_BUDGET / _total, 0.95))  # raises OutOfMemoryError on exceed
```

## Memory-Safe Data Processing

- **One at a time**: load one large object → process → `del obj; gc.collect()` → next
- **Load only what you need**: select specific tables/columns/rows, not entire databases
- **Test small first**: run on a sample before scaling to full data to estimate memory/time
- **Free intermediates in loops**: don't accumulate large results — aggregate incrementally
- **Size before loading**: check file/dataset size before loading; if it's >30% of `RAM_BUDGET`, chunk it

## Common Mistakes (from real crashes)

- **Skipping this skill entirely** — loading data with no RAM detection, no limits, no budget. Container OOM-killed, all agents lost.
- **Using `psutil.virtual_memory().total` instead of `_container_ram_gb()`** — reports host RAM (e.g. 66 GB) when container limit is 28 GB. You MUST use the cgroup-aware functions above.
- **Loading all tables from a multi-table database at once** — one agent loaded 14 RelBench tables simultaneously, spiked past container limit.
- **Setting no memory limits** — without `resource.setrlimit` (RAM) and `set_per_process_memory_fraction` (VRAM), a runaway script OOM-kills the container instead of raising a catchable error.
- **Using `os.cpu_count()` directly** — returns host CPUs (e.g. 192) instead of container limit (e.g. 4) on RunPod/Docker. Always use `_detect_cpus()` above which checks cgroup quota → CPU affinity → `os.cpu_count()` in order.

## Hardware Use

- Keep these results in mind for ALL subsequent tasks — don't assume more than detected
- GPU if available and parallelizable, multiprocessing if multiple CPUs
- Push available resources to their full potential — don't leave hardware idle
````

### [8] SKILL-INPUT — aii-parallel-computing · 2026-07-08 10:35:56 UTC

The agent loaded the **aii-parallel-computing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-parallel-computing
description: "CRITICAL PERFORMANCE SKILL. Maximize hardware utilization for compute-intensive tasks. Covers GPU acceleration, CPU parallelism, and async I/O. The difference between hours of failure and minutes of success. Use whenever writing ANY script that processes data, makes API calls, or does computation."
---

**ALWAYS parallelize. Sequential processing is unacceptable for any non-trivial workload.** A sequential script doing 1000 API calls takes hours and fails halfway. An async version finishes in minutes with proper error handling. ALWAYS ask: "Can this run in parallel?" — the answer is almost always yes.

Read aii-use-hardware skill first → get `NUM_CPUS`, `HAS_GPU`, `VRAM_GB`, `device`. Set `NUM_WORKERS` proportional to available CPU capacity — check `psutil.cpu_percent(interval=1)` and scale accordingly (e.g. 30% used → use ~70% of cores).

## Decision Tree (follow strictly)

- **I/O-bound** (API calls, downloads, web, file reads) → `asyncio` + `aiohttp` with `Semaphore(NUM_WORKERS * 4)`. NEVER do sequential HTTP requests in a loop.
- **CPU-bound, vectorizable** → GPU available: PyTorch on device / No GPU: NumPy vectorized ops. NEVER loop over array elements in Python.
- **CPU-bound, independent items** → `ProcessPoolExecutor(max_workers=NUM_WORKERS)`. NEVER process items one-by-one when they're independent.
- **Sequential** → only acceptable when items have data dependencies (each depends on the previous result).

## GPU Rules

- Use up to 90% of available VRAM — scale gradually (start small, increase after each successful run, keep 10% buffer)
- Move to device → compute → move back: `torch.tensor(data, device=device)` → `.cpu().numpy()`
- OOM fallback: catch `torch.cuda.OutOfMemoryError` → `empty_cache()` → halve batch size → retry on GPU. Keep reducing until it fits. Stay on GPU.
- Batch large data: chunk it, `del batch` between iterations to free VRAM

## Parallelism Rules

- **CPU-bound**: `ProcessPoolExecutor` + `as_completed`, pre-allocate result list indexed by submission order
- **I/O-bound**: `asyncio` + `aiohttp`, `Semaphore(NUM_WORKERS * 4)`, single shared `ClientSession`, `asyncio.gather(*tasks, return_exceptions=True)`
- Always add `tenacity` retries for transient failures, always set timeouts on HTTP requests
- **CRITICAL — `ProcessPoolExecutor` start method**: Default `fork` deadlocks with loguru (and any threading library). ALWAYS pass `mp_context=multiprocessing.get_context("spawn")` when constructing `ProcessPoolExecutor` in any script that uses loguru, threading, or async I/O. Example:
  ```python
  import multiprocessing as mp
  from concurrent.futures import ProcessPoolExecutor
  with ProcessPoolExecutor(max_workers=N, mp_context=mp.get_context("spawn")) as pool:
      ...
  ```
````

### [9] SYSTEM-USER prompt · 2026-07-08 10:45:49 UTC

````
<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/`:
GOOD: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/file.py`, `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_experiment_1_idx2
type: experiment
title: ECS vs Jaccard on Wiki + Boilerplate Benchmarks
summary: >-
  Run Edit Clustering Score (inverted IoD) and Jaccard classifiers on both the original Wikipedia 900-pair benchmark and a
  new boilerplate-hard-negative benchmark. Key question: does inverted_ECS complement 2-gram Jaccard when Jaccard is degraded
  by boilerplate inflation? Pure CPU, $0 cost.
runpod_compute_profile: cpu_heavy
implementation_pseudocode: "## Step 1: Load dependency dataset\n\nDEP_DIR = '/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_dataset_1'\n\
  wiki_rows = json.load(open(f'{DEP_DIR}/full_data_out.json'))  # list of {input, output, pair_id, fold, ...}\n# Each row:\
  \ input = json string with {text_a, text_b}, output = label ('near_duplicate'|'hard_negative'|'random')\n\n## Step 2: Build\
  \ boilerplate-hard-negative benchmark (900 pairs, balanced)\n\n# Download Wikipedia articles using the Wikipedia API (requests,\
  \ no auth needed)\n# Strategy for boilerplate-hard-negative construction:\n#   - Near-duplicate (300 pairs): same as before\
  \ — take article A, splice 20-40% with donor from different category\n#   - Boilerplate-hard-negative (300 pairs): two DIFFERENT\
  \ articles from same category BUT\n#     prepend IDENTICAL boilerplate header (150-250 words: legal disclaimer text + date/attribution\
  \ block)\n#     so 5-gram Jaccard lands in [0.25, 0.55] due to shared boilerplate\n#   - Random (300 pairs): two articles\
  \ from different categories, no boilerplate\n#\n# Wikipedia categories to use (same 8 as iter1): science, history, arts,\
  \ sports, technology, nature, society, architecture\n# Fetch 30 articles per category via Wikipedia API:\n#   url = f'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat}&cmlimit=50&format=json'\n\
  #   then for each article: extract first 150-600 words of clean text\n#\n# Boilerplate text (fixed string, ~180 words):\n\
  #   'This article is provided under the Creative Commons Attribution-ShareAlike License. \n#    All content is for informational\
  \ purposes only. Last updated: January 2024. \n#    Reproduction permitted with attribution. The views expressed do not\
  \ represent \n#    any organization. See terms at creativecommons.org/licenses/by-sa/3.0/ ...'\n#   (repeat/extend to ~180\
  \ words)\n#\n# For boilerplate-hard-neg pair: text_a = boilerplate + article_X, text_b = boilerplate + article_Y\n#   where\
  \ X != Y, same category, verify resulting 5-gram Jaccard in [0.2, 0.6]\n# For near-duplicate pair: text_a = article_X, text_b\
  \ = splice(article_X, donor_Y)\n#   splice: replace words[start:end] with words from donor_Y, start/end = random 20-40%\
  \ contiguous block\n# For random pair: text_a = article from cat_i, text_b = article from cat_j (i != j)\n#\n# Assign fold\
  \ 0-4 round-robin per class\n# Save as boilerplate_data.json in same schema as full_data_out.json\n\n## Step 3: Feature\
  \ extraction function\n\nimport difflib, re, math, numpy as np\n\ndef tokenize(text):\n    return re.findall(r'\\b\\w+\\\
  b', text.lower())\n\ndef jaccard_ngram(a_tokens, b_tokens, n):\n    a_shingles = set(zip(*[a_tokens[i:] for i in range(n)]))\n\
  \    b_shingles = set(zip(*[b_tokens[i:] for i in range(n)]))\n    if not a_shingles and not b_shingles: return 0.0\n  \
  \  return len(a_shingles & b_shingles) / len(a_shingles | b_shingles)\n\ndef compute_ecs(a_tokens, b_tokens):\n    \"\"\"\
  \n    Returns dict with ECS metrics.\n    Uses difflib.SequenceMatcher to get opcodes.\n    Edit positions: for each non-equal\
  \ opcode, record the midpoint position\n    in the combined sequence. Compute inter-edit-gap lengths.\n    ECS = IoD = var(gaps)\
  \ / mean(gaps). Low IoD = clustered = near-duplicate signal.\n    inverted_ECS = 1 / (1 + ECS).\n    longest_run_frac =\
  \ longest contiguous equal block / total tokens.\n    edit_count_norm = n_edit_ops / (len(a)+len(b)).\n    \"\"\"\n    matcher\
  \ = difflib.SequenceMatcher(None, a_tokens, b_tokens, autojunk=False)\n    opcodes = matcher.get_opcodes()\n    \n    #\
  \ edit positions: use a_start of each non-equal block, normalized to [0,1]\n    total_len = max(len(a_tokens), 1)\n    edit_positions\
  \ = [op[1] / total_len for op in opcodes if op[0] != 'equal']\n    \n    # inter-edit gaps (in token units, not normalized)\n\
  \    edit_pos_raw = [op[1] for op in opcodes if op[0] != 'equal']\n    gaps = [edit_pos_raw[i+1] - edit_pos_raw[i] for i\
  \ in range(len(edit_pos_raw)-1)]\n    \n    if len(gaps) < 2:\n        iod = 0.0  # single edit block = maximally clustered\n\
  \    else:\n        mu = np.mean(gaps)\n        var = np.var(gaps)\n        iod = var / mu if mu > 0 else 0.0\n    \n  \
  \  inv_ecs = 1.0 / (1.0 + iod)\n    \n    # longest equal run\n    equal_lengths = [op[4]-op[3] for op in opcodes if op[0]\
  \ == 'equal']\n    longest_run = max(equal_lengths) if equal_lengths else 0\n    longest_run_frac = longest_run / total_len\n\
  \    \n    n_edit_ops = sum(1 for op in opcodes if op[0] != 'equal')\n    edit_count_norm = n_edit_ops / (len(a_tokens)\
  \ + len(b_tokens) + 1)\n    \n    return {\n        'ecs': iod,\n        'inv_ecs': inv_ecs,\n        'longest_run_frac':\
  \ longest_run_frac,\n        'edit_count_norm': edit_count_norm,\n        'n_edit_positions': len(edit_pos_raw)\n    }\n\
  \ndef extract_features(row):\n    inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']\n  \
  \  ta, tb = inp['text_a'], inp['text_b']\n    ta_tok, tb_tok = tokenize(ta), tokenize(tb)\n    j5 = jaccard_ngram(ta_tok,\
  \ tb_tok, 5)\n    j2 = jaccard_ngram(ta_tok, tb_tok, 2)\n    ecs_feats = compute_ecs(ta_tok, tb_tok)\n    return {\n   \
  \     'jaccard_5gram': j5,\n        'jaccard_2gram': j2,\n        **ecs_feats,\n        'label': row['output'],\n      \
  \  'fold': row.get('fold', 0)\n    }\n\n## Step 4: Extract features for both datasets\n\nwiki_features = [extract_features(r)\
  \ for r in wiki_rows]\nboilerplate_features = [extract_features(r) for r in boilerplate_rows]\n\n## Step 5: Classifier evaluation\
  \ (5-fold CV)\n\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\n\
  from sklearn.metrics import roc_auc_score\nfrom sklearn.preprocessing import StandardScaler\nimport scipy.stats as stats\n\
  \ndef run_cv(features_list, feature_sets, label_map):\n    \"\"\"\n    feature_sets: dict of name -> list of feature column\
  \ names\n    label_map: which labels to use as binary (1=positive, 0=negative)\n    Returns dict of {feature_set_name: {auc_mean,\
  \ auc_std, fold_aucs}}\n    \"\"\"\n    df = pd.DataFrame(features_list)\n    df['y'] = df['label'].map(label_map)\n   \
  \ df = df.dropna(subset=['y'])\n    \n    results = {}\n    for fs_name, cols in feature_sets.items():\n        fold_aucs\
  \ = []\n        for fold in range(5):\n            train = df[df['fold'] != fold]\n            test = df[df['fold'] == fold]\n\
  \            if len(test['y'].unique()) < 2: continue\n            \n            X_train = train[cols].fillna(0).values\n\
  \            X_test = test[cols].fillna(0).values\n            y_train = train['y'].values\n            y_test = test['y'].values\n\
  \            \n            scaler = StandardScaler()\n            X_train = scaler.fit_transform(X_train)\n            X_test\
  \ = scaler.transform(X_test)\n            \n            clf = LogisticRegression(max_iter=1000, C=1.0)\n            clf.fit(X_train,\
  \ y_train)\n            probs = clf.predict_proba(X_test)[:, 1]\n            auc = roc_auc_score(y_test, probs)\n      \
  \      fold_aucs.append(auc)\n        \n        results[fs_name] = {\n            'auc_mean': np.mean(fold_aucs),\n    \
  \        'auc_std': np.std(fold_aucs),\n            'fold_aucs': fold_aucs\n        }\n    return results\n\n# Define feature\
  \ sets\nfeature_sets = {\n    'jaccard5_only': ['jaccard_5gram'],\n    'jaccard2_only': ['jaccard_2gram'],\n    'inv_ecs_only':\
  \ ['inv_ecs'],\n    'jaccard5_inv_ecs': ['jaccard_5gram', 'inv_ecs'],\n    'jaccard2_inv_ecs': ['jaccard_2gram', 'inv_ecs'],\n\
  \    'all_features': ['jaccard_5gram', 'jaccard_2gram', 'inv_ecs', 'longest_run_frac', 'edit_count_norm']\n}\n\n# Evaluation\
  \ 1: near_duplicate vs hard_negative (main discriminative task)\nlabel_map_hard = {'near_duplicate': 1, 'hard_negative':\
  \ 0}  # exclude random\n\nwiki_results = run_cv(wiki_features, feature_sets, label_map_hard)\nboilerplate_results = run_cv(boilerplate_features,\
  \ feature_sets, label_map_hard)\n\n# Evaluation 2: near_duplicate vs ALL negatives (overall task)\nlabel_map_all = {'near_duplicate':\
  \ 1, 'hard_negative': 0, 'random': 0}\nwiki_results_all = run_cv(wiki_features, feature_sets, label_map_all)\nboilerplate_results_all\
  \ = run_cv(boilerplate_features, feature_sets, label_map_all)\n\n## Step 6: Bootstrap CI for delta_AUC on boilerplate benchmark\n\
  \ndef bootstrap_delta_auc(features_list, col_a, col_b, label_map, B=2000):\n    \"\"\"Bootstrap CI for AUC(col_b) - AUC(col_a)\
  \ on full pooled data.\"\"\"\n    df = pd.DataFrame(features_list)\n    df['y'] = df['label'].map(label_map)\n    df = df.dropna(subset=['y'])\n\
  \    if len(df['y'].unique()) < 2: return None\n    \n    deltas = []\n    for _ in range(B):\n        sample = df.sample(n=len(df),\
  \ replace=True)\n        Xa = sample[col_a].fillna(0).values.reshape(-1,1)\n        Xb = sample[col_b if isinstance(col_b,\
  \ list) else [col_b]].fillna(0).values\n        y = sample['y'].values\n        if len(np.unique(y)) < 2: continue\n   \
  \     \n        sc = StandardScaler()\n        clf_a = LogisticRegression(max_iter=500).fit(sc.fit_transform(Xa), y)\n \
  \       clf_b = LogisticRegression(max_iter=500).fit(sc.fit_transform(Xb), y)\n        \n        auc_a = roc_auc_score(y,\
  \ clf_a.predict_proba(sc.transform(Xa))[:, 1])\n        auc_b = roc_auc_score(y, clf_b.predict_proba(sc.transform(Xb))[:,\
  \ 1])\n        deltas.append(auc_b - auc_a)\n    \n    deltas = np.array(deltas)\n    return {'mean': float(np.mean(deltas)),\
  \ 'ci_lo': float(np.percentile(deltas, 2.5)), 'ci_hi': float(np.percentile(deltas, 97.5))}\n\n# KEY comparison: jaccard2+inv_ecs\
  \ vs jaccard2 alone on boilerplate benchmark\ndelta_boilerplate = bootstrap_delta_auc(\n    boilerplate_features,\n    col_a=['jaccard_2gram'],\n\
  \    col_b=['jaccard_2gram', 'inv_ecs'],\n    label_map=label_map_hard, B=2000\n)\n\n## Step 7: Mann-Whitney U on IoD distributions\n\
  \ndef mann_whitney_iod(features_list):\n    df = pd.DataFrame(features_list)\n    nd = df[df['label']=='near_duplicate']['ecs'].dropna()\n\
  \    hn = df[df['label']=='hard_negative']['ecs'].dropna()\n    u, p = stats.mannwhitneyu(nd, hn, alternative='less')  #\
  \ near-dup IoD < hard-neg IoD\n    return {\n        'median_iod_near_dup': float(nd.median()),\n        'median_iod_hard_neg':\
  \ float(hn.median()),\n        'mann_whitney_p': float(p),\n        'n_near_dup': len(nd), 'n_hard_neg': len(hn)\n    }\n\
  \nwiki_mw = mann_whitney_iod(wiki_features)\nboilerplate_mw = mann_whitney_iod(boilerplate_features)\n\n## Step 8: Assemble\
  \ method_out.json\n\noutput = {\n    'wiki_benchmark': {\n        'cv_results_hard_subset': wiki_results,\n        'cv_results_all_labels':\
  \ wiki_results_all,\n        'mann_whitney_iod': wiki_mw\n    },\n    'boilerplate_benchmark': {\n        'cv_results_hard_subset':\
  \ boilerplate_results,\n        'cv_results_all_labels': boilerplate_results_all,\n        'mann_whitney_iod': boilerplate_mw,\n\
  \        'delta_auc_jaccard2_plus_inv_ecs_vs_jaccard2': delta_boilerplate\n    },\n    'key_findings': {\n        'inv_ecs_auc_wiki_hard':\
  \ wiki_results['inv_ecs_only']['auc_mean'],\n        'inv_ecs_auc_boilerplate_hard': boilerplate_results['inv_ecs_only']['auc_mean'],\n\
  \        'delta_auc_boilerplate_ci_lo': delta_boilerplate['ci_lo'],\n        'hypothesis_confirmed': boilerplate_results['jaccard2_inv_ecs']['auc_mean']\
  \ - boilerplate_results['jaccard2_only']['auc_mean'] >= 0.03\n    }\n}\n\njson.dump(output, open('method_out.json', 'w'),\
  \ indent=2)\nprint('Done. Key AUC delta:', delta_boilerplate)"
fallback_plan: |-
  If Wikipedia API is rate-limited or slow during boilerplate benchmark construction:
  - Use the EXISTING wiki benchmark's articles: re-pair same-category articles and prepend a fixed boilerplate string of ~180 words (no new downloads needed). The iter1 dataset stores category per pair, so articles of the same category can be re-paired.
  - If that yields fewer than 300 boilerplate-hard-neg pairs, reduce to 150 per class (450 total) and note the smaller sample in output.

  If IoD is undefined for pairs with 0 or 1 edit positions (very short texts or near-identical pairs):
  - Assign ECS=0 (maximally clustered, single block) and inv_ecs=1.0. Document this imputation.

  If 5-fold CV folds are missing from the dependency data (fold key absent):
  - Assign folds round-robin by pair_id modulo 5.

  If sklearn or scipy not available:
  - Implement AUC manually via trapezoid rule on sorted predictions; Mann-Whitney via rank-sum formula. All are pure numpy.
testing_plan: |-
  MINI TEST (first 60 rows of wiki benchmark, ~10 seconds):
  1. Load first 60 rows from full_data_out.json (20 per class).
  2. Run extract_features on all 60 — verify no crashes, all 6 features produced, no NaN in jaccard_5gram.
  3. Check median IoD: near_duplicate rows should have lower IoD than hard_negative rows (print medians).
  4. Run a single train/test split (fold 0 as test), fit LogisticRegression on ['jaccard_5gram'] vs ['inv_ecs'], verify both produce a valid AUC (not NaN, in [0,1]).
  5. Print 3 sample feature rows to visually sanity-check values are in expected ranges: jaccard_5gram in [0,1], inv_ecs in (0,1], longest_run_frac in (0,1].

  CONFIRMATION SIGNALS before full run:
  - At least one feature set produces AUC > 0.7 on the mini test (otherwise feature extraction is broken)
  - IoD median for near_dup < IoD median for hard_neg on mini test (validates directional hypothesis)
  - Boilerplate pairs (after construction) have 5-gram Jaccard in [0.15, 0.65] — print histogram

  FULL RUN: only proceed after mini test passes. Full run estimated <5 minutes on CPU.
</artifact_plan>

<dependencies>
Read the files in these dependency workspaces to understand what's available, then copy any you need into your working directory.

--- Dependency 1 ---
id: art_of-sMCpCSjl5
type: dataset
title: Wikipedia Text Pair Benchmark Dataset
summary: >-
  This artifact provides the Wikipedia Text Pair Benchmark, a synthetic dataset of 900 labeled text pairs built from Wikipedia
  articles via the Wikipedia API. The dataset contains three balanced classes (300 each): (1) near_duplicate pairs where text_b
  is a splice-edited version of text_a with 20-40% of words replaced by content from a donor article from a different category,
  producing 5-gram Jaccard similarity of 0.42-0.70 (median 0.54); (2) hard_negative pairs of two different articles from the
  same Wikipedia category, capturing thematic overlap without textual duplication (5-gram Jaccard near 0, emphasizing the
  semantic difficulty); and (3) random pairs of articles from different categories serving as easy negatives (5-gram Jaccard
  ~0). All texts are 80-800 words in English, drawn from 220 Wikipedia articles across 8 categories: science, history, arts,
  sports, technology, nature, society, and architecture. Each pair includes: text_a, text_b, label, pair_id, fold (0-4 for
  5-fold cross-validation), jaccard_5gram, word_count_a, word_count_b, category, and splice_start_pct/splice_length_pct (near_duplicate
  only). The dataset is formatted in the exp_sel_data_out schema with input as a JSON string containing text_a and text_b,
  and output as the class label. Key insight: 5-gram Jaccard cleanly separates near-duplicates from the other two classes,
  making it a useful baseline feature, while the hard_negative class tests whether models can detect category-level topical
  similarity vs. near-textual-copy. Dataset is $0 cost (no LLM calls), built entirely from the Wikipedia API.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json

Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</dependencies>

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

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. Use it for framework choices, implementation patterns, agent orchestration.

- **aii-handbook-multi-llm-agents** — Guide for implementing Multi-LLM Agent Systems research using Mirascope orchestration, HuggingFace datasets/evaluation, and proven multi-agent patterns.
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Use aii-json skill's format script with `--input method_out.json` to generate full, mini, and preview versions. If not in your workspace (see <workspace> above), copy them there. Run 'ls -lh' to verify these three files exist (DO NOT read them).
TODO 2. Apply aii-file-size-limit skill's file size check procedure (100MB limit) to method_out.json and full_method_out.json.
TODO 3. Ensure a `pyproject.toml` exists in your workspace with ALL dependencies pinned to the exact versions installed in your .venv (run `.venv/bin/pip freeze` to get them). This is required for reproducibility. The [project] section must include name, version, requires-python, and a dependencies list with pinned versions (e.g. `numpy==2.0.2`, not `numpy>=2.0`).
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ExperimentExpectedFiles": {
      "description": "All expected output files from experiment artifact.",
      "properties": {
        "script": {
          "description": "Path to method.py script. Example: 'method.py'",
          "title": "Script",
          "type": "string"
        },
        "full_output": {
          "description": "Full method output JSON file. Example: 'full_method_out.json'",
          "title": "Full Output",
          "type": "string"
        },
        "mini_output": {
          "description": "Mini method output JSON file. Example: 'mini_method_out.json'",
          "title": "Mini Output",
          "type": "string"
        },
        "preview_output": {
          "description": "Preview method output JSON file. Example: 'preview_method_out.json'",
          "title": "Preview Output",
          "type": "string"
        }
      },
      "required": [
        "script",
        "full_output",
        "mini_output",
        "preview_output"
      ],
      "title": "ExperimentExpectedFiles",
      "type": "object"
    }
  },
  "description": "Experiment artifact \u2014 structured output + file metadata.\n\nImplements research methodology with baseline comparison.\nProduces method.py and method_out.json files.",
  "properties": {
    "title": {
      "default": "",
      "description": "Artifact title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); describe the content, not a status.",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "layman_summary": {
      "default": "",
      "description": "One-sentence plain-language summary of what this artifact does, accessible to non-experts. Used only in the per-artifact README, not in downstream prompts.",
      "maxLength": 250,
      "minLength": 80,
      "title": "Layman Summary",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Summary for downstream artifacts: what this artifact provides",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/ExperimentExpectedFiles",
      "description": "All output files you created. Must include method.py script plus full/mini/preview method output JSON files."
    },
    "upload_ignore_regexes": {
      "description": "Regex patterns for workspace paths that must NOT be published to the GitHub repo, matched against each file's path relative to this artifact's workspace root (POSIX form, e.g. 'cache/abc.json'). Applied ON TOP OF the deploy step's built-in exclusions. Use this for executor-specific caches, large transient intermediates, or content-addressed blob stores (e.g. a cache/ dir of thousands of hash-named files) that would bloat the repo. Examples: ['(^|/)cache/', '(^|/)\\\\.weight_cache/', '(^|/)checkpoints/']. Leave empty if every workspace file should be published.",
      "items": {
        "type": "string"
      },
      "title": "Upload Ignore Regexes",
      "type": "array"
    }
  },
  "required": [
    "out_expected_files"
  ],
  "title": "ExperimentArtifact",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `./.terminal_claude_agent_struct_out.json`.
````

### [10] SYSTEM-USER prompt · 2026-07-08 10:46:39 UTC

```
<verification_failed>
Your experiment output failed verification (attempt 1/10).
</verification_failed>

<schema_errors>
JSON SCHEMA / CODE VALIDATION ERRORS:
  - full_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)
  - mini_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)
  - preview_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)

Fix: Your JSON files must follow the datasets-grouped exp_gen_sol_out.json schema:
     {
       "datasets": [
         {
           "dataset": "dataset_name",
           "examples": [
             {
               "input": "string (required)",
               "output": "string (required)",
               "metadata_fold": 2,
               "predict_<method_name>": "string - prediction per method"
             }
           ]
         }
       ]
     }

     NO 'split', 'dataset', or 'context' per-example. Dataset name at group level.
     Metadata via flat metadata_<name> fields.
     Read exp_gen_sol_out.json schema in aii-json skill.
     Then update method.py and regenerate the output files.

     If Python syntax errors: fix the syntax in method.py
</schema_errors>

<content_warnings>
CONTENT QUALITY ISSUES:
  - full_method_out.json: Only 3 total examples (expected at least 50)

Fix: Ensure predictions are non-empty and method.py runs correctly.
     Check that baseline and method predictions are being generated.
</content_warnings>

<task>
FIX THESE ISSUES:
2. Fix schema/syntax errors in method.py
3. Re-run method.py to regenerate output files
4. Validate with aii-json skill: validate method_out.json against exp_gen_sol_out schema

After making changes, verify:
- 'ls -la' shows all required files
- 'uv run method.py' completes successfully
- JSON files are valid (use aii-json skill validation)
- full_method_out.json has at least 50 examples
</task>
```
