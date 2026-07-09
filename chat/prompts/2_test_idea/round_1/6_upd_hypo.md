# upd_hypo — test_idea

> Phase: `invention_loop` · round 1 · `upd_hypo`
> Run: `run_E1yko-FJ_C_D` — Near Duplicate Detection
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `upd_hypo` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-07-08 10:30:21 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A hypothesis reviser (Step 3.6: UPD_HYPO in the invention loop)

You received the current hypothesis, all artifacts, and the paper draft.
Revise the hypothesis based on what the evidence supports.

Honest revision → focused research. Inflated confidence → wasted iteration.
</your_role>
</ai_inventor_context>

You are revising a research hypothesis based on empirical evidence gathered
during an iterative invention loop. Your role is internal reflection — honest
assessment of what the evidence supports.

SCOPE: Your ONLY output is the revised hypothesis text. You do NOT run code,
produce artifacts, fix bugs, or otherwise act on the evidence yourself — the
next iteration of the invention loop will spawn fresh artifacts based on your
revised hypothesis. Reflect on the evidence and rewrite the hypothesis;
nothing else.

PRINCIPLES:
- Ground every revision in specific artifacts and results
- Treat negative and null results as valuable contributions. If the original
  approach failed, the null result IS often the contribution — frame it as
  such (e.g. "X does not improve Y under conditions Z"). Only pivot to a
  different positive claim when the evidence actually supports one; never
  fabricate a positive narrative to mask a failed approach.
- Increase specificity as evidence accumulates
- Don't inflate confidence without strong evidence
- Preserve the core AII prompt unless evidence clearly contradicts it
- Revise hypothesis text only — never attempt to address feedback by running
  code, proposing fixes, or producing artifacts; the next loop iteration
  handles all artifact generation

<current_hypothesis>
The hypothesis as it stands. Revise it based on the evidence below.

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
</current_hypothesis>

<all_artifacts>
Complete set of research artifacts across all iterations.

--- Item 1 ---
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
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 2 ---
id: art_4FeNJ3U2uYiw
type: experiment
title: Edit Clustering Score vs Jaccard for Near-Duplicates
summary: >-
  EXPERIMENT: Edit Clustering Score (ECS) vs Jaccard-only vs combined classifiers for near-duplicate text detection on 900
  synthetic pairs (300 near-dup + 300 hard-neg + 300 random). METHOD: ECS = Index of Dispersion (var/mean) of inter-edit-gap
  positions from word-level LCS diff. Near-duplicates constructed by splicing a single contiguous 20-40% word block from a
  different article into a base article. Hard negatives = same-category article pairs; random negatives = cross-category pairs.
  Synthetic articles generated from 5 topic-specific vocabularies (politics/sports/science/business/technology, 60 words each,
  300-word articles). FEATURES: 5-gram Jaccard (k=5 word shingles), ECS (IoD), edit_count_norm, edit_span_frac, longest_run_frac.
  EVALUATION: 4 classifier variants (jaccard_only, ecs_only, jaccard_ecs, all_features) with 5-fold stratified CV and logistic
  regression; Mann-Whitney U test for ECS direction; hard-negative-only AUC; Precision@80%-recall. FULL RUN RESULTS (n=3000
  articles, 300 pairs/class): jaccard_only AUC=1.000, ecs_only AUC=0.973±0.006, jaccard_ecs AUC=1.000, all_features AUC=1.000.
  Delta_AUC(combined-jaccard)=0.000. MW p=1.0 (ECS directionally INVERTED: near-dups have LOWER IoD than negatives because
  a single contiguous splice produces few clustered edit positions, not scattered ones). VERDICT: DISCONFIRMED — 5-gram Jaccard
  is a perfect ceiling classifier for this synthetic dataset; ECS captures real but redundant signal. Key insight: contiguous
  splices preserve k-grams in unchanged regions (Jaccard~0.5-0.7) while scattered edits destroy most k-grams (Jaccard~0),
  making Jaccard inherently sensitive to edit locality in ways that leave no room for ECS. ECS-only (0.97 AUC) demonstrates
  the structural signal is real but complementarity requires scenarios where Jaccard is weaker (e.g., with bigram Jaccard
  or natural-language corpora with boilerplate phrase overlap).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 3 ---
id: art_e6xsDw2pWrBu
type: evaluation
title: ECS vs Jaccard AUC Validation on Wikipedia Pairs
summary: >-
  Evaluation of the Edit Clustering Score (ECS) hypothesis on 900 Wikipedia pairs (300 near-duplicate, 300 hard-negative same-topic,
  300 random). Dataset was constructed by splicing 20-40% word spans between articles to create near-duplicates; hard negatives
  were same-title-prefix articles. Features computed: Jaccard 5-gram similarity and ECS (Index of Dispersion of inter-edit-gap
  positions from word-level LCS diff). Results: (1) Jaccard alone achieves AUC=1.000 on the hard-negative subset — near-duplicate
  construction directly inflates Jaccard by design. (2) ECS alone achieves AUC=0.106, well below the 0.65 threshold. (3) Jaccard+ECS
  combined degrades to AUC=0.118 (delta=-0.882, 95% CI [-0.909,-0.854]). (4) Median IoD is LOWER for near-duplicates (15.08)
  than hard-negatives (59.67), ratio=0.25 — the opposite direction of the hypothesis (Mann-Whitney p=1.0). (5) Cohen's d on
  log-IoD = -0.83 confirms strong effect in the wrong direction. Mechanistic explanation: splice-based near-duplicates have
  ONE large contiguous edit block (low IoD), while hard-negative pairs have many scattered differences (high IoD). Overall
  verdict: DISCONFIRMED on all three criteria. All metrics in eval_out.json (schema: exp_eval_sol_out). Length-stratified
  AUC confirmed the pattern holds across all word-count buckets.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
</all_artifacts>

<new_artifacts_this_iteration>
These 3 artifacts were created THIS iteration.

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
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

id: art_4FeNJ3U2uYiw
type: experiment
title: Edit Clustering Score vs Jaccard for Near-Duplicates
summary: >-
  EXPERIMENT: Edit Clustering Score (ECS) vs Jaccard-only vs combined classifiers for near-duplicate text detection on 900
  synthetic pairs (300 near-dup + 300 hard-neg + 300 random). METHOD: ECS = Index of Dispersion (var/mean) of inter-edit-gap
  positions from word-level LCS diff. Near-duplicates constructed by splicing a single contiguous 20-40% word block from a
  different article into a base article. Hard negatives = same-category article pairs; random negatives = cross-category pairs.
  Synthetic articles generated from 5 topic-specific vocabularies (politics/sports/science/business/technology, 60 words each,
  300-word articles). FEATURES: 5-gram Jaccard (k=5 word shingles), ECS (IoD), edit_count_norm, edit_span_frac, longest_run_frac.
  EVALUATION: 4 classifier variants (jaccard_only, ecs_only, jaccard_ecs, all_features) with 5-fold stratified CV and logistic
  regression; Mann-Whitney U test for ECS direction; hard-negative-only AUC; Precision@80%-recall. FULL RUN RESULTS (n=3000
  articles, 300 pairs/class): jaccard_only AUC=1.000, ecs_only AUC=0.973±0.006, jaccard_ecs AUC=1.000, all_features AUC=1.000.
  Delta_AUC(combined-jaccard)=0.000. MW p=1.0 (ECS directionally INVERTED: near-dups have LOWER IoD than negatives because
  a single contiguous splice produces few clustered edit positions, not scattered ones). VERDICT: DISCONFIRMED — 5-gram Jaccard
  is a perfect ceiling classifier for this synthetic dataset; ECS captures real but redundant signal. Key insight: contiguous
  splices preserve k-grams in unchanged regions (Jaccard~0.5-0.7) while scattered edits destroy most k-grams (Jaccard~0),
  making Jaccard inherently sensitive to edit locality in ways that leave no room for ECS. ECS-only (0.97 AUC) demonstrates
  the structural signal is real but complementarity requires scenarios where Jaccard is weaker (e.g., with bigram Jaccard
  or natural-language corpora with boilerplate phrase overlap).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

id: art_e6xsDw2pWrBu
type: evaluation
title: ECS vs Jaccard AUC Validation on Wikipedia Pairs
summary: >-
  Evaluation of the Edit Clustering Score (ECS) hypothesis on 900 Wikipedia pairs (300 near-duplicate, 300 hard-negative same-topic,
  300 random). Dataset was constructed by splicing 20-40% word spans between articles to create near-duplicates; hard negatives
  were same-title-prefix articles. Features computed: Jaccard 5-gram similarity and ECS (Index of Dispersion of inter-edit-gap
  positions from word-level LCS diff). Results: (1) Jaccard alone achieves AUC=1.000 on the hard-negative subset — near-duplicate
  construction directly inflates Jaccard by design. (2) ECS alone achieves AUC=0.106, well below the 0.65 threshold. (3) Jaccard+ECS
  combined degrades to AUC=0.118 (delta=-0.882, 95% CI [-0.909,-0.854]). (4) Median IoD is LOWER for near-duplicates (15.08)
  than hard-negatives (59.67), ratio=0.25 — the opposite direction of the hypothesis (Mann-Whitney p=1.0). (5) Cohen's d on
  log-IoD = -0.83 confirms strong effect in the wrong direction. Mechanistic explanation: splice-based near-duplicates have
  ONE large contiguous edit block (low IoD), while hard-negative pairs have many scattered differences (high IoD). Overall
  verdict: DISCONFIRMED on all three criteria. All metrics in eval_out.json (schema: exp_eval_sol_out). Length-stratified
  AUC confirmed the pattern holds across all word-count buckets.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
</new_artifacts_this_iteration>

<current_paper>
The paper draft from this iteration — represents the current state of the research story.

# Introduction

Near-duplicate text detection is a foundational task in web crawling, LLM training data curation, and plagiarism detection. At scale—hundreds of billions of documents—computational cost forbids exhaustive pairwise comparison, motivating compact hash-based methods that estimate Jaccard similarity over character or word shingles [1, 2]. These methods have one architectural assumption in common: they measure the *quantity* of overlap between two documents but are blind to the *spatial arrangement* of differences. Two documents may share 60% of their 5-grams because one is a localized edit of the other (a near-duplicate) or because both discuss the same topic with domain-specific vocabulary and shared boilerplate headers (a thematic near-match). Current methods cannot distinguish these cases without auxiliary signals.

We ask: can the geometric pattern of where edits occur in a word-level diff distinguish genuine near-duplicates from coincidental lexical overlap?

The motivation comes from spatial ecology. The Index of Dispersion (IoD = variance/mean of inter-event gap lengths) is a classical test for whether a 1D point process is clustered (IoD $\gg 1$), Poisson-random (IoD $\approx 1$), or regular (IoD $\ll 1$) [7]. Ecologists use IoD to detect animal herding: clustered occurrences signal social behavior, while uniform spacing signals territorial distribution. Transplanting this to the 1D process of edit positions in a text diff is the conceptual transfer at the core of this work: edit positions are the events, text length is the space, and the IoD should distinguish locally-edited near-duplicates (clustered edits) from documents differing uniformly throughout (scattered edits).

This framing yields the Edit Clustering Score (ECS): run a word-level longest-common-subsequence (LCS) diff, extract the word-index positions of all edit tokens, compute the IoD of the inter-gap sequence. We hypothesize that ECS $\gg 1$ for near-duplicates (clustered human edits) and ECS $\approx 1$ for hard negatives (uniformly scattered mismatches). Combining ECS with Jaccard should improve precision over Jaccard alone, particularly on hard negatives where two documents share topic-specific vocabulary.

[FIGURE:fig1]

Our experiments on a 900-pair Wikipedia benchmark yield a surprising and instructive result: the directional prediction is inverted. Near-duplicates constructed by splicing one contiguous 20--40\% span from a donor article have a *lower* median IoD (15.1) than hard negatives (59.7), with the gap confirmed at high confidence (Mann-Whitney $p = 1.0$ in the reversed direction, Cohen's $d = -0.83$ on log-IoD). The mechanism is clear in retrospect: a single contiguous splice produces exactly one large edit block, concentrating all edits in one region and suppressing inter-gap variance. Hard negatives, sharing only individual words and phrases scattered throughout both articles, produce many small edit blocks distributed across the text, which inflates variance and thus IoD. The ecological analogy is therefore inverted: near-duplicates resemble a single migrating herd (one cluster) while thematic near-matches resemble a scattered population (many small clusters).

Despite this inversion, ECS alone achieves AUC = 0.97 [ARTIFACT:art_4FeNJ3U2uYiw] on 5-fold cross-validation, confirming that spatial edit structure is a highly discriminating signal. The failure to improve over Jaccard stems from a ceiling effect: contiguous splicing directly preserves 5-gram overlap in unchanged regions ($\tilde{J} = 0.52$ for near-duplicates vs. $\tilde{J} \approx 0$ for both negative classes), making Jaccard a perfect classifier for this construction. ECS is redundant given perfect Jaccard, not uninformative.

**Summary of Contributions:**
\begin{itemize}
    \item We introduce the Edit Clustering Score (ECS), a training-free feature based on the Index of Dispersion of inter-edit-gap positions in a word-level LCS diff, inspired by spatial point-process statistics (Section~\ref{sec:method}).
    \item We construct the Wikipedia Text Pair Benchmark: 900 labeled pairs across three classes (near-duplicate, hard negative, random), drawn from 220 Wikipedia articles in 8 subject categories (Section~\ref{sec:data}).
    \item We demonstrate that ECS captures strong discriminative signal (AUC = 0.97 standalone), but with inverted directionality relative to the ecological hypothesis (Section~\ref{sec:results}).
    \item We provide a mechanistic explanation of why contiguous splicing suppresses IoD rather than inflating it, and identify the conditions under which ECS would complement Jaccard (Section~\ref{sec:discussion}).
\end{itemize}

# Related Work
\label{sec:related}

**MinHash and SimHash.** Broder [1] introduced min-wise independent permutations (MinHash) to estimate Jaccard similarity over character $k$-grams at web scale; the AltaVista crawler used this to cluster tens of millions of near-duplicate pages. Manku et al. [2] introduced SimHash, a locality-sensitive hashing scheme based on random projections of TF-IDF feature vectors, which allows near-duplicate detection in $O(1)$ per query using Hamming distance lookup. Both methods operate on bag-of-shingles representations and are entirely insensitive to the spatial arrangement of differences.

**Neural similarity.** RETSim [3] (Zhang et al., 2023) trains a character-level embedding model specifically for near-duplicate detection, achieving high throughput and robustness to adversarial edits. It learns a similarity metric end-to-end and does not expose or exploit spatial edit patterns. ECS is complementary: it is training-free, requires no labeled data, and provides an interpretable geometric characterization.

**Compression-based similarity.** The normalized compression distance (NCD; Li et al. [4]) uses the ratio of joint to individual compression lengths as a similarity proxy, implicitly capturing repeated structure. NCD is sensitive to spatial redundancy in that repeated substrings compress better, but it does not expose the positions of differences or their clustering.

**LLM training data deduplication.** Lee et al. [5] showed that exact and near-duplicate deduplication of pretraining corpora substantially improves LLM quality by reducing memorization and improving sample diversity. The Pile [6] and subsequent large-scale datasets apply MinHash deduplication as a standard preprocessing step. Abbas et al. [8] introduced SemDeDup, which clusters semantic embeddings to remove near-semantic-duplicates while preserving information-rich pairs—a different regime from lexical near-duplication. None of these approaches exploit the spatial structure of differences.

**Passage-level plagiarism detection.** Zou et al. [9] detect copied passages using TF-IDF clustering followed by sequence alignment of candidate passages. This is the closest prior work in spirit: it groups matching passages (a form of spatial analysis) but uses frequency vectors rather than point-process statistics on diff positions, and targets cross-document passage reuse rather than pairwise near-duplicate classification.

**Spatial point processes.** The Index of Dispersion and related statistics (Ripley's $K$, Morisita's index) are standard tools in spatial ecology and geography for classifying point patterns as clustered, random, or regular [7]. Their application to text analysis is, to our knowledge, novel.

# Dataset Construction
\label{sec:data}

We construct the Wikipedia Text Pair Benchmark [ARTIFACT:art_of-sMCpCSjl5] from Wikipedia articles retrieved via the Wikipedia API. The dataset contains 900 pairs balanced across three classes of 300 pairs each.

**Near-duplicates.** For each near-duplicate pair, we take a base article (text\_a) and construct text\_b by identifying a contiguous 20--40\% word span, replacing it with the corresponding content from a randomly selected donor article from a *different* Wikipedia category. This simulates the localized-edit model of near-duplicate creation. The splice position and length are recorded. The resulting 5-gram Jaccard similarity ranges from 0.42 to 0.70 (median 0.52), as the unchanged 60--80\% of the article contributes to high 5-gram overlap.

**Hard negatives.** Hard-negative pairs consist of two independently written articles from the same Wikipedia category (e.g., two science articles, two sports articles). These pairs share domain vocabulary, named entities, and structural conventions, but have no textual copying relationship. Their 5-gram Jaccard similarity is near zero (median $\approx 0$), confirming that 5-gram Jaccard cleanly discriminates this class from near-duplicates in our construction.

**Random pairs.** Random pairs are drawn from articles in *different* categories, serving as easy negatives with near-zero Jaccard similarity.

All articles are 80--800 words in English. The dataset spans 220 Wikipedia articles across 8 categories: science, history, arts, sports, technology, nature, society, and architecture. Each pair records a fold identifier (0--4) for 5-fold cross-validation, enabling reproducible evaluation.

# Method: Edit Clustering Score
\label{sec:method}

## Word-Level Diff

Given a text pair $(A, B)$, we tokenize both texts into word sequences by whitespace splitting after lowercasing. We then compute the longest common subsequence (LCS) alignment using Python's `difflib.SequenceMatcher` [10], which identifies matched and unmatched token spans. Each unmatched token (an insertion or deletion in the diff) is assigned a position index in the concatenated aligned sequence.

## Index of Dispersion on Edit Positions

Let $p_1 < p_2 < \cdots < p_k$ be the sorted positions of all edit tokens in the aligned sequence, and let $g_i = p_{i+1} - p_i$ for $i = 1, \ldots, k-1$ be the sequence of inter-edit gaps. The Edit Clustering Score (ECS) is defined as:
$$
\text{ECS} = \text{IoD}(g) = \frac{\text{Var}(g)}{\text{Mean}(g)}
$$
when $k \geq 3$ (i.e., at least 3 edit tokens exist, yielding at least 2 gaps). For pairs with fewer than 3 edit positions, ECS is set to 0 by convention (indicating no meaningful spatial structure).

For a homogeneous Poisson process (random scattering of edits), IoD = 1 in expectation. IoD $\gg$ 1 indicates over-dispersed gaps (clustered edits separated by long stretches of matching text). IoD $\ll$ 1 indicates under-dispersed gaps (regularly spaced edits).

## Additional Features

We compute three auxiliary edit-structure features:
\begin{itemize}
    \item \textbf{edit\_count\_norm}: Number of edit tokens divided by total aligned length (normalized edit density).
    \item \textbf{edit\_span\_frac}: Fraction of the aligned sequence spanned from the first to the last edit token (coverage).
    \item \textbf{longest\_run\_frac}: Length of the longest contiguous edit run, divided by total edit count (concentration ratio).
\end{itemize}

## Classifiers

We evaluate four logistic-regression classifier variants using 5-fold stratified cross-validation:
\begin{enumerate}
    \item \textbf{Jaccard-only}: 5-gram Jaccard similarity as the sole feature.
    \item \textbf{ECS-only}: ECS (IoD) as the sole feature.
    \item \textbf{Jaccard+ECS}: Both Jaccard and ECS.
    \item \textbf{All features}: Jaccard, ECS, edit\_count\_norm, edit\_span\_frac, longest\_run\_frac.
\end{enumerate}

We report ROC-AUC (macro-averaged across folds), precision at 80\% recall, and Mann-Whitney $U$ tests comparing IoD distributions between near-duplicates and negatives.

# Results
\label{sec:results}

## IoD Distributions Confirm Structural Signal—With Inverted Direction

The most consequential finding is the directionality of the IoD signal. Near-duplicate pairs produced by contiguous splicing have a significantly *lower* median IoD (15.1, experiment run; 15.1, evaluation run) than hard-negative pairs (22.9 in the experiment; 59.7 in the evaluation), and lower still than random pairs (median IoD $\approx 47.5$) [ARTIFACT:art_4FeNJ3U2uYiw]. The Mann-Whitney test gives $p = 1.0$ in the direction predicted by the original hypothesis (i.e., near-duplicates have lower IoD than negatives with certainty), and Cohen's $d = -0.83$ on log-IoD confirms a large effect in the inverted direction [ARTIFACT:art_e6xsDw2pWrBu].

[FIGURE:fig2]

The mechanism is straightforward. A contiguous splice produces a single large edit block: long stretches of identical text bracket one region of complete mismatch. This pattern minimizes variance in the inter-gap sequence (few gaps, all similar in length), yielding low IoD. In contrast, two independent articles on the same topic share isolated words, phrases, and named entities scattered throughout, producing many small edit events distributed across the text. The variance of many small gaps is high, producing high IoD. Table~1 summarizes the feature statistics by class.

\begin{table}[h]
\centering
\caption{Median feature values by pair class on the 900-pair benchmark.}
\begin{tabular}{lccc}
\hline
Class & 5-gram Jaccard & ECS (IoD) & Edit Span Frac \\
\hline
Near-duplicate & 0.522 & 15.1 & -- \\
Hard negative & $\approx$0.000 & 59.7 & -- \\
Random & $\approx$0.000 & 47.5 & -- \\
\hline
\end{tabular}
\end{table}

## Classification Performance

Table~2 reports AUC results from 5-fold cross-validation [ARTIFACT:art_4FeNJ3U2uYiw] and from the independent evaluation on 600 hard-subset pairs [ARTIFACT:art_e6xsDw2pWrBu].

\begin{table}[h]
\centering
\caption{ROC-AUC by classifier variant. Cross-val: 5-fold on 900 pairs (300/class). Eval: independent evaluation on 600 hard-subset pairs (near-duplicate vs. hard-negative only).}
\begin{tabular}{lcc}
\hline
Classifier & AUC (Cross-val) & AUC (Eval, hard subset) \\
\hline
Jaccard-only & 1.000 $\pm$ 0.000 & 1.000 \\
ECS-only & 0.973 $\pm$ 0.006 & 0.106 \\
Jaccard+ECS & 1.000 $\pm$ 0.000 & 0.118 \\
All features & 1.000 $\pm$ 0.000 & -- \\
\hline
\end{tabular}
\end{table}

[FIGURE:fig3]

Three findings stand out:

**ECS alone is highly discriminative in cross-validation (AUC = 0.97).** Because ECS is lower for near-duplicates than for all negatives (including random pairs), a classifier using only IoD can almost perfectly separate the three classes in the cross-validation setting, which pools all three classes.

**ECS fails on the hard-negative vs. near-duplicate evaluation (AUC = 0.106).** When evaluated only against hard negatives—the intended challenge—ECS degrades to near-chance. Near-duplicates (low IoD) and random pairs (high IoD) are well-separated, but hard negatives happen to sit between them (IoD $\approx$ 60), and ECS cannot reliably distinguish hard negatives from near-duplicates in a head-to-head evaluation.

**Jaccard is a perfect classifier (AUC = 1.0) and leaves no room for ECS.** The splice construction directly inflates 5-gram Jaccard: near-duplicates have median Jaccard 0.52, while both negative classes have Jaccard $\approx 0$. Adding ECS to Jaccard yields no improvement ($\Delta\text{AUC} = 0.000$ in cross-validation; $\Delta\text{AUC} = -0.882$ in the hard-subset evaluation, CI $[-0.909, -0.854]$). Jaccard has already solved the problem.

## Length Stratification

The ceiling-Jaccard finding holds consistently across document-length strata [ARTIFACT:art_e6xsDw2pWrBu]. In the evaluation run, Jaccard-only achieves AUC = 1.0 in all three buckets ($<$200, 200--500, $>$500 words), while the combined classifier degrades to 0.158, 0.306, and 0.094 respectively—confirming that ECS adds noise, not signal, when Jaccard is saturated.

# Discussion
\label{sec:discussion}

## Why the Directional Hypothesis Failed

The original ecological analogy predicted IoD $\gg 1$ for near-duplicates (local edits = clustered events = high variance). This prediction conflates two different senses of "clustering": (a) *spatial concentration* (edits occur in one region) and (b) *statistical clustering* in the point-process sense (high inter-event gap variance). A single contiguous edit block is the most spatially concentrated possible arrangement, but it produces only two or three gap values—a nearly degenerate distribution with low variance. Uniform scatter produces many gap values with high variance. The IoD therefore measures the *count and regularity* of edit clusters, not the spatial concentration of a single cluster. Future formulations should use statistics sensitive to single-cluster presence, such as the fraction of edits in the longest run (`longest_run_frac`) or the spatial entropy of the edit density function.

## When ECS Would Complement Jaccard

The failure to improve over Jaccard here is specific to the experimental construction: contiguous splicing *by design* inflates Jaccard, making it a perfect separator. ECS becomes a complementary signal in at least three scenarios:

1. **Bigram or unigram Jaccard.** When similarity is estimated from shorter shingles (bigrams, unigrams), the baseline degrades substantially, creating room for ECS to add signal.
2. **Boilerplate inflation.** When two unrelated documents share a legal header, disclaimer, or structured template that inflates Jaccard, ECS can flag that the matching content is distributed rather than localized.
3. **Multi-segment edits.** If near-duplicates involve two or more separated edit regions (e.g., both introduction and conclusion rewritten), the IoD of those two clusters would be high, matching the original prediction.

## Practical Implications

Even in its inverted form, ECS provides a meaningful signal. A threshold on IoD below a value of $\sim$20 (using the observed median of 15.1 for near-duplicates vs. 59.7 for hard negatives) could serve as a pre-filter to flag candidate near-duplicates for more expensive verification. This is particularly relevant for LLM training data pipelines [5, 6] where false positives (rejecting legitimate documents) are costly and a fast spatial screen can reduce computation.

## Limitations

**Synthetic near-duplicates.** All near-duplicates are constructed by contiguous splicing. Real-world human editing behavior may involve multiple separate edits, sentence reordering, or paraphrase—patterns not captured here. The experiment should be replicated on a corpus of real revision histories (e.g., Wikipedia edit logs).

**Hard-negative construction.** Hard negatives are same-category pairs with near-zero 5-gram Jaccard. In practice, hard negatives that are challenging for Jaccard (i.e., high-Jaccard pairs from shared boilerplate) are precisely where ECS would be most useful—but this regime is absent from the dataset by construction.

**Single Wikipedia domain.** The benchmark draws entirely from Wikipedia, which has consistent article structure, neutral tone, and encyclopedic vocabulary. Results may not generalize to web-crawled text with diverse formatting, code-switching, or structured data.

# Conclusion

We proposed the Edit Clustering Score, a training-free near-duplicate detection feature derived from the Index of Dispersion of inter-edit-gap positions in a word-level LCS diff. The spatial-point-process framing—transplanting IoD from spatial ecology to the 1D sequence of edit positions—is novel in the near-duplicate detection literature. Our main empirical finding is a productive surprise: the directional prediction of the ecological analogy is inverted in the contiguous-splice setting, where a single concentrated edit block produces low IoD rather than high IoD. Despite this directional inversion, ECS achieves a standalone AUC of 0.97, confirming that spatial edit structure is highly discriminative. The failure to improve over Jaccard similarity is a ceiling artifact of the experimental construction, not a statement about the value of spatial edit features in general.

Future work should evaluate ECS in regimes where Jaccard is weak: low-order shingling, boilerplate-inflated similarity, or natural revision histories with multi-segment edits. Alternative statistics—such as the concentration ratio of the longest edit run or the entropy of the edit density—may better capture the single-cluster signature that distinguishes contiguous near-duplicates from scattered hard negatives.

# References

[1] A. Z. Broder. On the resemblance and containment of documents. *Proceedings of the Compression and Complexity of Sequences*, 1997, pp. 21--29.

[2] G. Manku, A. Jain, and A. Sarma. Detecting near-duplicates for web crawling. *Proceedings of the 16th International Conference on World Wide Web (WWW)*, 2007, pp. 141--150.

[3] M. Zhang, O. Vallis, A. Bumin, T. Vakharia, and E. Bursztein. RETSim: Resilient and efficient text similarity. *International Conference on Learning Representations*, 2023.

[4] M. Li, X. Chen, X. Li, B. Ma, and P. M. B. Vitanyi. The similarity metric. *IEEE Transactions on Information Theory*, 50(12):3250--3264, 2004.

[5] K. Lee, D. Ippolito, A. Nystrom, C. Zhang, D. Eck, C. Callison-Burch, and N. Carlini. Deduplicating training data makes language models better. *Proceedings of ACL*, 2022, pp. 8424--8445.

[6] L. Gao, S. Biderman, S. Black, L. Golding, T. Hoppe, C. Foster, J. Phang, H. He, A. Thite, N. Nabeshima, S. Presser, and C. Leahy. The Pile: An 800GB dataset of diverse text for language modeling. *arXiv:2101.00027*, 2020.

[7] D. R. Cox and P. A. W. Lewis. *The Statistical Analysis of Series of Events*. Methuen, 1966.

[8] A. Abbas, K. Tirumala, D. Simig, S. Ganguli, and A. S. Morcos. SemDeDup: Data-efficient learning at web-scale through semantic deduplication. *arXiv:2303.09540*, 2023.

[9] D. Zou, W. Lu, Y. Li, L. Tang, and G. Qu. External plagiarism detection using information retrieval and sequence alignment. *CLEF Working Notes*, 2010.

[10] T. Peters. difflib: Helpers for computing deltas. *Python Standard Library*, 2001.

[11] J. W. Hunt and T. G. Szymanski. A fast algorithm for computing longest common subsequences. *Communications of the ACM*, 20(5):350--353, 1977.

\bibliographystyle{plainnat}
\bibliography{references}
</current_paper>

<reviewer_feedback>
Feedback from the paper reviewer this iteration.

- [MAJOR] (methodology) The benchmark construction is circular with respect to the evaluation goal. Near-duplicates are created by contiguous splicing, which by design preserves 60-80% of 5-grams unchanged, giving them median Jaccard=0.52. Hard negatives and random pairs have Jaccard≈0. Jaccard therefore achieves AUC=1.000 and leaves zero room for ECS to improve upon it. This means the experiment cannot answer its stated question ('does ECS complement Jaccard?') because the baseline has already saturated. The paper acknowledges this as a 'ceiling artifact of the experimental construction' but does not fix it by running the experiment in a non-ceiling regime.
  Action: Construct a hard-negative class that is genuinely hard for Jaccard: pairs of documents sharing substantial boilerplate (headers, legal text, structured templates) that inflates Jaccard to 0.3-0.6 despite no duplication relationship. Test whether ECS correctly identifies that the high-Jaccard overlap is distributed (not localized). Alternatively, use bigram Jaccard (k=2) which degrades on the same construction, creating room for ECS to add signal. Report results in this complementary regime alongside the current disconfirmation.
- [MAJOR] (evidence) There is an unexplained discrepancy between the two experimental artifacts. The experiment artifact (art_4FeNJ3U2uYiw) summary states: 'Synthetic articles generated from 5 topic-specific vocabularies (politics/sports/science/business/technology, 60 words each, 300-word articles)'—not Wikipedia articles. The dataset artifact (art_of-sMCpCSjl5) and the paper describe Wikipedia API articles of 80-800 words across 8 categories. The cross-validation AUC=0.973 is reported from the experiment artifact, but which data did it run on? If the 5-fold CV was on synthetic vocabulary-template data, the cross-validation results are not representative of the Wikipedia benchmark described in the paper.
  Action: Clarify in the paper and artifacts which data source produced which result. If the cross-validation (AUC=0.973) and the evaluation (AUC=0.106) used different datasets, report them separately and clearly label each. Ensure the 5-fold cross-validation is run on the Wikipedia benchmark to ensure consistency.
- [MAJOR] (scope) The benchmark is entirely synthetic, small (900 pairs), and confined to a single domain (Wikipedia). The paper's motivation invokes web-crawled LLM training corpora 'at scale—hundreds of billions of documents,' but the experiment uses 900 synthetic pairs. No evaluation on any real near-duplicate corpus is provided. The hard negatives are same-category Wikipedia pairs with Jaccard≈0, which are not representative of the practically challenging case (high-Jaccard boilerplate matches or near-paraphrase).
  Action: Add experiments on at least one established benchmark: the PAN plagiarism detection corpus (which includes real copied and paraphrased pairs), Wikipedia revision history pairs (consecutive edits creating genuine near-duplicates with variable edit patterns), or a sample from Common Crawl with known near-duplicates. Even 200-500 pairs from a real corpus would substantially strengthen the paper's external validity claims.
- [MAJOR] (rigor) ECS-only achieves AUC=0.106 on the hard-negative vs. near-duplicate evaluation. This is not just near-chance—it is dramatically below 0.5, indicating the feature reliably predicts the wrong class. The paper notes this but does not analyze it as a finding in its own right: a feature with AUC=0.106 is informative (negatively) and could be inverted to achieve AUC≈0.894. The paper should acknowledge and test this inversion, since 'use ECS<threshold to flag near-duplicates' is the proposed practical application, and the threshold direction must be correctly specified.
  Action: Report the AUC for inverted ECS (1 - ECS or equivalently AUC=1-0.106=0.894) on the hard subset. This reframes the result: ECS is actually highly discriminative (AUC~0.90) for near-duplicate vs. hard-negative even in the challenging regime—but the threshold direction is opposite to the ecological prediction. This is a stronger and more accurate representation of what was found.
- [MINOR] (novelty) The related work section does not cover recent LLM data curation deduplication work beyond Lee et al. 2022 and Abbas et al. 2023. Missing: SlimPajama (2023), FineWeb (2024), and the broader discussion of exact vs. fuzzy deduplication in LLM pipelines, where the practical tradeoffs of hash-based vs. embedding-based approaches are actively debated. This is the context in which the paper's contribution would land.
  Action: Add 2-3 citations covering the current state of LLM dataset deduplication (e.g., FineWeb/HuggingFace data curation papers, SlimPajama) and briefly position ECS relative to exact-deduplication (Bloom filters) vs. fuzzy (MinHash/SimHash) vs. semantic (SemDeDup) pipelines.
- [MINOR] (clarity) Table 1 shows Edit Span Frac as '--' for all three classes without explanation. The caption does not explain why this column is empty. Additionally, the paper cites two different median IoD values for hard negatives in the same paragraph (22.9 in the 'experiment run' vs. 59.7 in the 'evaluation run'), which is confusing given the dataset discrepancy issue above.
  Action: Fill in the Edit Span Frac column in Table 1, or remove the column and add a note explaining why it is omitted. Clarify in the text why the experiment and evaluation runs give different median IoD values for hard negatives (22.9 vs. 59.7)—this discrepancy should be explained as arising from different datasets or random seeds, not left implicit.
- [MINOR] (methodology) The paper evaluates only logistic regression classifiers. Given that ECS and Jaccard are likely not linearly separable in all regimes (they interact multiplicatively: ECS is only meaningful when edit count is high, which correlates with low Jaccard), a simple threshold or decision-tree classifier might better reveal complementarity.
  Action: Add a simple threshold-based classifier (ECS < T AND Jaccard > J) as an additional baseline, or use a decision tree with depth 2. This would reveal interaction effects between ECS and Jaccard that logistic regression may miss.
</reviewer_feedback>



<task>
IMPORTANT: Your ONLY output is the revised hypothesis text. Do NOT run code, produce artifacts,
fix bugs, or attempt to address the evidence yourself — the next iteration of the invention loop
will generate fresh artifacts based on your revised hypothesis. Reflect and rewrite; nothing else.

Do NOT generate a completely new hypothesis. Take the current hypothesis and REVISE it
to incorporate new evidence. Keep the core idea — refine, narrow, or strengthen it.

1. Does the evidence support the hypothesis? Narrow or broaden scope as needed.
2. Which claims now have strong evidence? Which are still unsupported?
3. Should the hypothesis become more specific based on what we've learned?
4. If reviewer feedback is provided, address the critiques directly.

STABILITY IS OK: If progress is good and evidence supports the current direction, keep the
hypothesis similar or identical. Only make substantive changes when evidence clearly calls for
them — e.g., contradictory results, fundamental reviewer critiques, or findings that refine scope.

You must also classify two kinds of edges in the research trace:

(A) The H↔H edge — how does this revised hypothesis relate to the previous one?
    Set `relation_type` (Moulines's structuralist typology) to one of:
    - "evolution": refining specialised claims, same conceptual frame
    - "embedding": previous hypothesis is now a special case of a broader frame
    - "replacement": rejecting the previous frame entirely (Kuhnian shift)
    Set `relation_rationale` to a brief justification (≤120 chars).

(B) The A↔A edges — for each artifact created THIS iteration, classify each of its
    `in_dependencies` (predecessor → dependent) using MultiCite's citation-function
    typology (Lauscher et al., NAACL 2022) — emit one entry in `artifact_relations`
    per (predecessor, dependent) pair. Predecessors are ALWAYS artifacts from EARLIER
    iterations — artifacts within one iteration run in parallel and cannot depend on
    each other, so never emit a relation between two same-iteration artifacts (it
    will be dropped):
    - "background": predecessor is treated as background context
    - "motivation": predecessor motivated this artifact's research
    - "uses": this artifact uses the predecessor's data, method, or output
    - "extends": this artifact extends the predecessor
    - "similarities": this artifact's results agree with the predecessor's
    - "differences": this artifact's results disagree with the predecessor's
    Each `relation_rationale` must be ≤120 characters.

Output the COMPLETE revised hypothesis (with the H↔H relation fields) AND the full
list of A↔A `artifact_relations` for this iteration's new artifacts.
</task><user_data>
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
  "$defs": {
    "ArtifactRelation": {
      "description": "One typed A\u2194A edge between a dependent artifact and one of its in_dependencies.\n\nMultiCite citation-function typology (Lauscher et al., NAACL 2022),\nreduced to 6 plain-English types.",
      "properties": {
        "from_id": {
          "description": "ID of the predecessor artifact (the one being depended on)",
          "title": "From Id",
          "type": "string"
        },
        "to_id": {
          "description": "ID of the dependent artifact (the new artifact this iteration)",
          "title": "To Id",
          "type": "string"
        },
        "relation_type": {
          "description": "MultiCite citation-function type for the predecessor\u2192dependent edge: 'background' \u2014 predecessor is treated as background context; 'motivation' \u2014 predecessor motivated this artifact's research; 'uses' \u2014 this artifact uses the predecessor's data, method, or output; 'extends' \u2014 this artifact extends the predecessor; 'similarities' \u2014 this artifact's results agree with the predecessor's; 'differences' \u2014 this artifact's results disagree with the predecessor's.",
          "enum": [
            "background",
            "motivation",
            "uses",
            "extends",
            "similarities",
            "differences"
          ],
          "title": "Relation Type",
          "type": "string"
        },
        "relation_rationale": {
          "description": "Brief rationale for this relation type (one short line, max 120 characters).",
          "maxLength": 120,
          "title": "Relation Rationale",
          "type": "string"
        }
      },
      "required": [
        "from_id",
        "to_id",
        "relation_type",
        "relation_rationale"
      ],
      "title": "ArtifactRelation",
      "type": "object"
    }
  },
  "description": "Revised hypothesis after reviewing iteration results.\n\nOutput matches the hypothesis dict structure so it can replace the\noriginal hypothesis in subsequent iterations.",
  "properties": {
    "title": {
      "description": "Revised hypothesis title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); may be unchanged if still accurate.",
      "title": "Title",
      "type": "string"
    },
    "hypothesis": {
      "description": "Revised hypothesis statement \u2014 what we now believe based on evidence",
      "title": "Hypothesis",
      "type": "string"
    },
    "relation_rationale": {
      "description": "Brief rationale for the H\u2194H revision type (one short line, max 120 characters).",
      "maxLength": 120,
      "title": "Relation Rationale",
      "type": "string"
    },
    "confidence_delta": {
      "description": "How confidence changed: 'increased', 'decreased', or 'unchanged'",
      "title": "Confidence Delta",
      "type": "string"
    },
    "key_changes": {
      "description": "Bullet list of specific changes made to the hypothesis",
      "items": {
        "type": "string"
      },
      "title": "Key Changes",
      "type": "array"
    },
    "relation_type": {
      "description": "Moulines's structuralist typology of this hypothesis revision: 'evolution' \u2014 refining specialised claims while keeping the same conceptual frame; 'embedding' \u2014 the previous hypothesis is now a special case of a broader frame; 'replacement' \u2014 rejecting the previous frame entirely (incommensurable, Kuhnian revolution).",
      "enum": [
        "evolution",
        "embedding",
        "replacement"
      ],
      "title": "Relation Type",
      "type": "string"
    },
    "artifact_relations": {
      "description": "Typed A\u2194A edges for this iteration's new artifacts. Emit one entry per (predecessor \u2192 dependent) edge for every in_dependency on each artifact produced this iteration.",
      "items": {
        "$ref": "#/$defs/ArtifactRelation"
      },
      "title": "Artifact Relations",
      "type": "array"
    }
  },
  "required": [
    "title",
    "hypothesis",
    "relation_rationale",
    "confidence_delta",
    "key_changes",
    "relation_type"
  ],
  "title": "RevisedHypothesis",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `./.terminal_claude_agent_struct_out.json`.
````

### [2] HUMAN-USER prompt · 2026-07-08 10:30:21 UTC

```
Propose a simple, novel, testable ML method for near-duplicate text detection and validate it with a tiny experiment.
```

### [3] SYSTEM-USER prompt · 2026-07-08 10:31:00 UTC

```
<validation-feedback>
Attempt 1 failed validation.

Schema validation found 1 problem — fix ALL of them at once:
  - at `relation_rationale`: 'Same IoD/ECS frame, but directional prediction corrected and complementarity condition narrowed to non-ceiling Jaccard regimes.' is too long (at most 120 characters, got 127)
Every required field must be present and every field type must match the schema.

Please use the Write tool to overwrite `.terminal_claude_agent_struct_out.json` with corrected JSON. Do not invent new fields; match the schema you were given.
</validation-feedback>
```
