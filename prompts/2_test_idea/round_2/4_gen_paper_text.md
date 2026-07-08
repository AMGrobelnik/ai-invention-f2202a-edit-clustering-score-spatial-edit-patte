# gen_paper_text — test_idea

> Phase: `invention_loop` · round 2 · `gen_paper_text`
> Run: `run_E1yko-FJ_C_D` — Edit Clustering Score: Spatial Edit Patterns for Near-Duplicate Text Detection
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_paper_text` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-07-08 10:51:47 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A research paper writer (Step 3.4: GEN_PAPER_TEXT in the invention loop)

You received the hypothesis, all artifacts, the previous paper draft (if any), and reviewer feedback.
Write a complete paper draft with figure placeholders.

Publication-quality paper → strong contribution. Weak paper → wasted iteration.
</your_role>
</ai_inventor_context>

<research_methodology>
Write like a researcher drafting a paper, not a chatbot summarizing bullet points.

- Structure as a paper would: research question → methodology → results → analysis → limitations. Not a list of "we did X, then Y."
- Ground every claim in specific artifacts and specific numbers. "Results show improvement" is empty — state effect sizes, baselines, and conditions.
- Be honest about what worked, what didn't, and why. Don't spin failures as "future work."
- The paper's headline contribution should be a positive or surprising finding. Negative results are valuable context but should not be the primary narrative — lead with what works.
- Address reviewer feedback from previous iterations explicitly — show you've thought about each critique.
</research_methodology>

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

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. Use it for related-work positioning and how this field frames a genuinely novel contribution.

- **aii-handbook-multi-llm-agents** — Guide for implementing Multi-LLM Agent Systems research using Mirascope orchestration, HuggingFace datasets/evaluation, and proven multi-agent patterns.
</available_domain_handbooks>
<previous_paper>
STARTING POINT: This is your paper draft from the previous iteration.

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
</previous_paper>

<reviewer_feedback>
STEP 1 — REVIEW: A reviewer evaluated the previous paper draft above and produced this feedback.

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

<pipeline_steps>
STEP 2 — STRATEGY: The pipeline's strategy generator (gen_strat) read the reviewer feedback
and designed a new research strategy to address the critiques.

STEP 3 — PLANNING: The planner (gen_plan) turned the strategy into concrete artifact plans —
specific experiments, datasets, or research tasks to execute.

STEP 4 — EXECUTION: The executor (gen_art) ran those plans and produced the new artifacts
shown in <new_artifacts_this_iteration> below.
</pipeline_steps>

<hypothesis>
STEP 5 — HYPOTHESIS UPDATE: The hypothesis was revised based on evidence from previous iterations.

kind: hypothesis
title: Low Edit Dispersion Flags Near-Duplicates
hypothesis: >-
  When a near-duplicate text is created by locally modifying an original (rewriting one paragraph, inserting a sentence, changing
  a contiguous region), the edit operations in the word-level diff between the two texts form a single concentrated block
  rather than being scattered uniformly. Empirical evidence shows this produces a LOWER Index of Dispersion (IoD = variance/mean
  of inter-edit-gap lengths) for genuine near-duplicates (median IoD ≈ 15) compared to hard negatives with scattered vocabulary
  overlap (median IoD ≈ 60), with a large inverted effect (Cohen's d = -0.83 on log-IoD). The correct discriminant is therefore
  ECS < threshold (not ECS > threshold as originally predicted). ECS alone achieves AUC ≈ 0.89 on the near-duplicate vs. hard-negative
  task when the threshold direction is correctly inverted. However, ECS is redundant given 5-gram Jaccard in the current benchmark
  because contiguous splicing by construction inflates Jaccard to 0.52 for near-duplicates vs. ≈0 for hard negatives, making
  Jaccard a perfect ceiling classifier. ECS provides complementary signal specifically in regimes where Jaccard is degraded:
  (1) pairs sharing substantial boilerplate or legal headers that inflate Jaccard for unrelated documents to 0.3–0.6, where
  ECS correctly identifies the high-Jaccard overlap as distributed (high IoD) rather than localized (low IoD); (2) short-shingle
  (bigram/unigram) Jaccard regimes where the baseline degrades on noisy text; and (3) multi-segment edits where two or more
  separated edit regions each contribute a cluster. To establish genuine complementarity, the next iteration should construct
  hard negatives that are hard for Jaccard (boilerplate-sharing pairs with Jaccard 0.3–0.6) and confirm that ECS < threshold
  correctly downgrades these while preserving recall on splice-based near-duplicates. The core claim is reframed: a single
  concentrated edit block (low IoD) is the spatial signature of contiguous near-duplication, and this signal is orthogonal
  to Jaccard only when Jaccard is not already saturated.
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
_relation_rationale: >-
  Same IoD/ECS frame; directional prediction corrected and complementarity narrowed to non-ceiling Jaccard regimes.
_confidence_delta: decreased
_key_changes:
- >-
  Corrected directional prediction: ECS < threshold signals near-duplicates (not ECS > threshold); single contiguous block
  suppresses IoD rather than inflating it.
- >-
  Quantified inverted effect: median IoD 15 (near-dup) vs 60 (hard-neg), Cohen's d = -0.83; inverted ECS achieves AUC ≈ 0.89.
- >-
  Identified Jaccard ceiling as the reason ECS fails to complement: splice construction inflates 5-gram Jaccard by design,
  leaving no room for ECS to add signal.
- >-
  Narrowed the complementarity claim to specific regimes where Jaccard is degraded: boilerplate-inflated hard negatives (Jaccard
  0.3-0.6), short-shingle baselines, or multi-segment edits.
- >-
  Added requirement for next iteration: construct genuinely Jaccard-hard hard negatives (boilerplate-sharing pairs) to test
  whether ECS correctly distinguishes distributed from localized high-Jaccard overlap.
- >-
  Flagged data discrepancy: cross-validation (AUC=0.973) used synthetic vocabulary-template data, not the Wikipedia benchmark;
  next iteration must run 5-fold CV on a consistent dataset.
relation_type: evolution
</hypothesis>

<all_artifacts>
FULL EVIDENCE BASE: All 6 research artifacts across all iterations.

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

--- Item 4 ---
id: art_tvr4WHa6fK5S
type: dataset
title: Wikipedia Boilerplate Hard-Negative Benchmark
summary: |-
  Built from Wikipedia API (zero cost, no LLM calls): 900 text pairs balanced across 3 classes.

  NEAR-DUPLICATE (300 pairs): Original Wikipedia article A + splice version where 20-30% of words are replaced by a contiguous block from an unrelated donor article B. 5-gram Jaccard mean=0.582, range [0.50, 0.75] — high overlap due to preserved majority.

  BOILERPLATE-HARD-NEGATIVE (300 pairs): Two completely unrelated Wikipedia articles C and D, each prepended with an identical ~300-400-word CC-BY-SA license/disclaimer block. 5-gram Jaccard mean=0.465, range [0.25, 0.61] — critically in the non-ceiling regime targeted by [0.25, 0.65]. boilerplate_frac mean≈0.83 indicating most shared signal comes from the header. This class is the key challenge: high Jaccard from shared boilerplate, but articles are semantically unrelated — a naive Jaccard-based detector would mis-classify these as near-duplicates.

  RANDOM (300 pairs): Two unrelated Wikipedia articles with no boilerplate. 5-gram Jaccard mean=0.000, range [0.00, 0.002] — trivially distinguishable.

  Fields per example: pair_id (int), text_a (str), text_b (str), label (str), fold (int 0-4 for 5-fold CV), jaccard_5gram (float), jaccard_2gram (float), boilerplate_frac (float).

  The dataset directly tests the core hypothesis: whether an ECS (ensemble/combined similarity) method can distinguish boilerplate-hard-negatives from true near-duplicates, which requires recognizing that shared n-grams concentrated in a boilerplate header are not evidence of document-level similarity. The non-ceiling Jaccard regime [0.25, 0.65] for the hard-negative class ensures the task is not trivially solvable by a Jaccard threshold.

  All 900 pairs have 5-fold CV assignments (fold 0-4), enabling proper cross-validation. Dataset size: 6.9MB. Built from ~195 cached Wikipedia articles fetched via MediaWiki API with proper User-Agent headers.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 5 ---
id: art_6LbUk9kFi7QV
type: experiment
title: ECS vs Jaccard Near-Duplicate Detection Experiment
summary: >-
  This experiment compares Edit Clustering Score (inverted Index of Dispersion of edit positions, ECS) against n-gram Jaccard
  similarity for near-duplicate text detection, across two benchmarks: (1) the original 900-pair Wikipedia benchmark (300
  near-duplicate / 300 hard-negative same-category / 300 random) and (2) a new 900-pair boilerplate benchmark where hard-negative
  pairs are prepended with ~180 words of identical boilerplate text. Key results: (a) inv_ECS alone achieves AUC=0.809±0.025
  on both benchmarks, capturing structural edit-clustering signal without any n-gram overlap. (b) 2-gram and 5-gram Jaccard
  achieve perfect AUC=1.000 on both benchmarks — the boilerplate inflation (mean 5-gram Jaccard=0.089 on boilerplate-hard-neg
  pairs) did NOT degrade Jaccard because boilerplate-hard-neg J5 (0.08–0.15) remains far below near-duplicate J5 (0.42–0.70).
  (c) The primary hypothesis (delta AUC ≥ 0.03 for J2+ECS vs J2 alone on boilerplate benchmark) was NOT confirmed (delta≈0).
  (d) However, the IoD distributional signal IS confirmed: near-duplicate pairs have strongly lower IoD (median=20.3) vs hard-negative
  pairs (median=81.8), Mann-Whitney p≈4×10⁻³⁹ on both benchmarks. ECS captures a complementary, boilerplate-independent structural
  signal, but Jaccard remains so discriminative on these benchmarks that adding ECS yields no marginal gain. Output contains
  1800 examples (900 wiki + 900 boilerplate) each with 6 predict_* fields (per feature set: jaccard5_only, jaccard2_only,
  inv_ecs_only, jaccard5_inv_ecs, jaccard2_inv_ecs, all_features) and per-pair metadata (fold, jaccard scores, ECS metrics).
  5-fold CV with LogisticRegression + StandardScaler. Bootstrap CI (B=2000) for delta AUC. All computation is CPU-only, $0
  cost, runtime ~45 seconds.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 6 ---
id: art_0t7LHI3OhoTn
type: evaluation
title: ECS vs Jaccard Statistical Evaluation
summary: |-
  EVALUATION: ECS vs Jaccard Statistical Evaluation on 605 synthetic near-duplicate text pairs (300 near_dup, 5 hard_neg, 300 random) from the iter_1 experiment (art_4FeNJ3U2uYiw). SOURCE: synthetic_vocab_template (NOT Wikipedia-derived). All articles generated from 5 topic-specific 60-word vocabularies.

  KEY RESULTS:
  - Inverted-ECS AUC on hard subset (near_dup vs hard_neg): 0.9533, CI [0.914, 0.984]. Exceeds 0.65 threshold.
  - Jaccard AUC on hard subset: 1.0000 (ceiling classifier, blocks complementarity measurement).
  - Delta AUC (inv_ECS - jaccard) on hard subset: -0.0464, CI [-0.088, -0.016]. Does NOT exceed 0.03 threshold.
  - Boilerplate-augmented benchmark (jaccard += 0.35 for hard_neg): ECS AUC=0.9536, Jaccard AUC=1.0, delta=-0.0467 (Jaccard remains ceiling).
  - Mann-Whitney U=70.0, p=0.000508 (two-sided), p_less=0.000254. Median IoD near_dup=4.341, hard_neg=22.889, ratio=0.190. Cohen's d on log-IoD=-2.193 (large effect).
  - Decision tree (max_depth=2): root split on Jaccard at threshold=0.206, feature importance jaccard=1.0, inv_ecs=0.0. ECS adds no split after Jaccard.
  - Length-stratified AUC: only 'long' tercile had class diversity; inv_ECS AUC=0.855, jaccard AUC=1.0.

  VERDICT: PARTIAL — inverted-ECS AUC condition MET (0.953 > 0.65), delta_AUC condition NOT MET (-0.046, not > 0.03). Jaccard is a perfect ceiling classifier on the hard subset (all hard_neg have Jaccard=0.0), which structurally blocks ECS complementarity. ECS captures a real and strong structural signal (MW p<0.001, d=-2.19) but cannot complement a perfect Jaccard classifier on this synthetic dataset. Complementarity would require a regime where Jaccard is weaker (natural corpora with boilerplate overlap, or bigram Jaccard). NOTE: hard_neg n=5 (very small), limiting statistical power for delta-AUC estimation.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
</all_artifacts>

<new_artifacts_this_iteration>
NEW THIS ITERATION: These 3 artifacts were created to address the reviewer
feedback. Their findings should be the primary basis for your revisions.

id: art_tvr4WHa6fK5S
summary: |-
  Built from Wikipedia API (zero cost, no LLM calls): 900 text pairs balanced across 3 classes.

  NEAR-DUPLICATE (300 pairs): Original Wikipedia article A + splice version where 20-30% of words are replaced by a contiguous block from an unrelated donor article B. 5-gram Jaccard mean=0.582, range [0.50, 0.75] — high overlap due to preserved majority.

  BOILERPLATE-HARD-NEGATIVE (300 pairs): Two completely unrelated Wikipedia articles C and D, each prepended with an identical ~300-400-word CC-BY-SA license/disclaimer block. 5-gram Jaccard mean=0.465, range [0.25, 0.61] — critically in the non-ceiling regime targeted by [0.25, 0.65]. boilerplate_frac mean≈0.83 indicating most shared signal comes from the header. This class is the key challenge: high Jaccard from shared boilerplate, but articles are semantically unrelated — a naive Jaccard-based detector would mis-classify these as near-duplicates.

  RANDOM (300 pairs): Two unrelated Wikipedia articles with no boilerplate. 5-gram Jaccard mean=0.000, range [0.00, 0.002] — trivially distinguishable.

  Fields per example: pair_id (int), text_a (str), text_b (str), label (str), fold (int 0-4 for 5-fold CV), jaccard_5gram (float), jaccard_2gram (float), boilerplate_frac (float).

  The dataset directly tests the core hypothesis: whether an ECS (ensemble/combined similarity) method can distinguish boilerplate-hard-negatives from true near-duplicates, which requires recognizing that shared n-grams concentrated in a boilerplate header are not evidence of document-level similarity. The non-ceiling Jaccard regime [0.25, 0.65] for the hard-negative class ensures the task is not trivially solvable by a Jaccard threshold.

  All 900 pairs have 5-fold CV assignments (fold 0-4), enabling proper cross-validation. Dataset size: 6.9MB. Built from ~195 cached Wikipedia articles fetched via MediaWiki API with proper User-Agent headers.
type: dataset
title: Wikipedia Boilerplate Hard-Negative Benchmark

id: art_6LbUk9kFi7QV
summary: >-
  This experiment compares Edit Clustering Score (inverted Index of Dispersion of edit positions, ECS) against n-gram Jaccard
  similarity for near-duplicate text detection, across two benchmarks: (1) the original 900-pair Wikipedia benchmark (300
  near-duplicate / 300 hard-negative same-category / 300 random) and (2) a new 900-pair boilerplate benchmark where hard-negative
  pairs are prepended with ~180 words of identical boilerplate text. Key results: (a) inv_ECS alone achieves AUC=0.809±0.025
  on both benchmarks, capturing structural edit-clustering signal without any n-gram overlap. (b) 2-gram and 5-gram Jaccard
  achieve perfect AUC=1.000 on both benchmarks — the boilerplate inflation (mean 5-gram Jaccard=0.089 on boilerplate-hard-neg
  pairs) did NOT degrade Jaccard because boilerplate-hard-neg J5 (0.08–0.15) remains far below near-duplicate J5 (0.42–0.70).
  (c) The primary hypothesis (delta AUC ≥ 0.03 for J2+ECS vs J2 alone on boilerplate benchmark) was NOT confirmed (delta≈0).
  (d) However, the IoD distributional signal IS confirmed: near-duplicate pairs have strongly lower IoD (median=20.3) vs hard-negative
  pairs (median=81.8), Mann-Whitney p≈4×10⁻³⁹ on both benchmarks. ECS captures a complementary, boilerplate-independent structural
  signal, but Jaccard remains so discriminative on these benchmarks that adding ECS yields no marginal gain. Output contains
  1800 examples (900 wiki + 900 boilerplate) each with 6 predict_* fields (per feature set: jaccard5_only, jaccard2_only,
  inv_ecs_only, jaccard5_inv_ecs, jaccard2_inv_ecs, all_features) and per-pair metadata (fold, jaccard scores, ECS metrics).
  5-fold CV with LogisticRegression + StandardScaler. Bootstrap CI (B=2000) for delta AUC. All computation is CPU-only, $0
  cost, runtime ~45 seconds.
type: experiment
title: ECS vs Jaccard Near-Duplicate Detection Experiment

id: art_0t7LHI3OhoTn
summary: |-
  EVALUATION: ECS vs Jaccard Statistical Evaluation on 605 synthetic near-duplicate text pairs (300 near_dup, 5 hard_neg, 300 random) from the iter_1 experiment (art_4FeNJ3U2uYiw). SOURCE: synthetic_vocab_template (NOT Wikipedia-derived). All articles generated from 5 topic-specific 60-word vocabularies.

  KEY RESULTS:
  - Inverted-ECS AUC on hard subset (near_dup vs hard_neg): 0.9533, CI [0.914, 0.984]. Exceeds 0.65 threshold.
  - Jaccard AUC on hard subset: 1.0000 (ceiling classifier, blocks complementarity measurement).
  - Delta AUC (inv_ECS - jaccard) on hard subset: -0.0464, CI [-0.088, -0.016]. Does NOT exceed 0.03 threshold.
  - Boilerplate-augmented benchmark (jaccard += 0.35 for hard_neg): ECS AUC=0.9536, Jaccard AUC=1.0, delta=-0.0467 (Jaccard remains ceiling).
  - Mann-Whitney U=70.0, p=0.000508 (two-sided), p_less=0.000254. Median IoD near_dup=4.341, hard_neg=22.889, ratio=0.190. Cohen's d on log-IoD=-2.193 (large effect).
  - Decision tree (max_depth=2): root split on Jaccard at threshold=0.206, feature importance jaccard=1.0, inv_ecs=0.0. ECS adds no split after Jaccard.
  - Length-stratified AUC: only 'long' tercile had class diversity; inv_ECS AUC=0.855, jaccard AUC=1.0.

  VERDICT: PARTIAL — inverted-ECS AUC condition MET (0.953 > 0.65), delta_AUC condition NOT MET (-0.046, not > 0.03). Jaccard is a perfect ceiling classifier on the hard subset (all hard_neg have Jaccard=0.0), which structurally blocks ECS complementarity. ECS captures a real and strong structural signal (MW p<0.001, d=-2.19) but cannot complement a perfect Jaccard classifier on this synthetic dataset. Complementarity would require a regime where Jaccard is weaker (natural corpora with boilerplate overlap, or bigram Jaccard). NOTE: hard_neg n=5 (very small), limiting statistical power for delta-AUC estimation.
type: evaluation
title: ECS vs Jaccard Statistical Evaluation
</new_artifacts_this_iteration>

<data_files>
Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</data_files>

<task>
Write a research paper draft with LaTeX-ready text, BibTeX citations, and figure placeholders.

YOUR TURN (gen_paper_text): Revise the paper.

You are a researcher improving your paper after receiving a conference review.
Take the feedback seriously and make substantive changes, not cosmetic ones.

1. ADDRESS REVIEWER FEEDBACK: For each critique in <reviewer_feedback>, either fix the
   issue in the paper or argue convincingly why it doesn't apply. Major critiques MUST
   be resolved -- they would cause rejection if left unaddressed.
2. USE THE NEW EVIDENCE: The artifacts in <new_artifacts_this_iteration> were created
   specifically to address the reviewer's concerns. Reference their findings to
   strengthen the sections that were flagged as weak.
3. REWRITE, DON'T PATCH: Don't just append new paragraphs. Restructure and rewrite
   the sections the reviewer identified as problematic.
4. MAINTAIN CONSISTENCY: Ensure the paper aligns with the updated hypothesis.
</task>

<figure_instructions>
FIGURE FORMAT: Use [FIGURE:fig_id] markers in paper_text to indicate where each figure goes.
Then provide the full figure specs in the separate `figures` structured output array.
Each figure in the array must have an `id` matching a marker in the text. Set the `aspect_ratio`
field per figure: 21:9 for architecture / pipeline / flow-chart diagrams (the hero figure should
be one of these — place its marker near the END of the Introduction so it floats to the top of
page 2), 16:9 for comparisons / multi-panel results, 4:3 for dense charts, 1:1 for heatmaps /
confusion matrices / scatter plots.

Example in paper_text:
  "...our method achieves state-of-the-art results as shown below.\n\n[FIGURE:fig3]\n\nThe results demonstrate..."

Example in figures array (results comparison):
  {"id": "fig3", "title": "Performance Comparison", "caption": "Comparison of geometric mean query latency across optimizers.", "image_gen_detailed_description": "Grouped bar chart. X-axis: model names. Y-axis: latency (seconds, 0-5). Values: PostgreSQL=4.6s (red), Bao=2.8s (blue), RLQOpt=2.0s (green). Error bars +/-0.3-0.8. Sans-serif font, white background.", "aspect_ratio": "16:9", "summary": "Compares latency across optimizers"}

Example in figures array (architecture diagram, hero):
  {"id": "fig1", "title": "System Architecture", "caption": "End-to-end pipeline: encoder feeds latents into the planner, which queries the value head before emitting actions.", "image_gen_detailed_description": "Horizontal flow diagram, left to right. Five labeled boxes: 'Input' (gray), 'Encoder' (blue), 'Latent (z, 256-dim)' (light blue, narrow), 'Planner' (green), 'Action Head' (orange). Arrows labeled with shapes. Value head as separate green box below 'Planner', bidirectional arrow. Sans-serif font, clean white background, no 3D.", "aspect_ratio": "21:9", "summary": "Hero architecture diagram"}

CRITICAL: Before writing figure specs, look through artifact workspace output files (*_out.json)
and code to find ALL the exact values. The figure generator cannot read files — every exact number
and value MUST be in the image_gen_detailed_description.
</figure_instructions>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-writing, aii-semscholar-bib.
TODO 2. LITERATURE REVIEW: Use web search tools to research the landscape — search key terms from
<hypothesis> and <all_artifacts>. Then use aii_semscholar_bib__fetch to batch-fetch real
BibTeX entries. Build a comprehensive Related Work section. Do NOT fabricate entries.
TODO 3. READ ARTIFACTS: Before writing each section, READ the relevant artifact source code, output
files, and data in the workspace. Extract concrete implementation details, technical innovations,
algorithmic specifics, and quantitative results. Do NOT write surface-level descriptions.

ARTIFACT REFERENCES: When you reference results, methodology, or findings from a specific artifact,
place an [ARTIFACT:artifact_id] marker inline. These become footnotes linking to the artifact's code
in the GitHub repository (first mention gets a footnote with URL, subsequent mentions are omitted).
Use the exact artifact ID from <all_artifacts>. Place the marker right after the claim it supports.
Example:
  "Our evaluation showed a 15% improvement over baselines [ARTIFACT:art_4f9d2c81ab37]." 
TODO 4. WRITE PAPER: Write the full paper text with [FIGURE:fig_id] markers per <figure_instructions>,
and provide the figure specs in the figures array. Cite with numeric references [1], [2], etc.
At the end of the paper text, include a full bibliography section. Do NOT compile LaTeX or generate
actual image/figure files. Your ONLY output is the structured JSON.
</todos><user_data>
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
    "FigureSpec": {
      "description": "Figure specification \u2014 structured output from paper writing agent.\n\nThe LLM fills these as a list in PaperText.figures.\nLater converted to Figure objects for viz gen.",
      "properties": {
        "id": {
          "description": "Figure ID matching the [FIGURE:id] marker in paper_text (e.g., 'fig1')",
          "title": "Id",
          "type": "string"
        },
        "title": {
          "description": "Figure title in plain, everyday language \u2014 short and jargon-free. Aim for about 4-8 words (~40 characters).",
          "title": "Title",
          "type": "string"
        },
        "caption": {
          "description": "LaTeX figure caption \u2014 appears below the figure in the paper. Should describe what the figure shows and highlight key takeaways.",
          "title": "Caption",
          "type": "string"
        },
        "image_gen_detailed_description": {
          "description": "Detailed image generation prompt \u2014 axes, labels, ALL numeric values, colors, aspect ratio, layout. The image generator cannot read files; this is its ONLY input.",
          "title": "Image Gen Detailed Description",
          "type": "string"
        },
        "summary": {
          "description": "Brief summary of what this figure communicates",
          "title": "Summary",
          "type": "string"
        }
      },
      "required": [
        "id",
        "title",
        "caption",
        "image_gen_detailed_description",
        "summary"
      ],
      "title": "FigureSpec",
      "type": "object"
    }
  },
  "description": "Paper text \u2014 structured output from paper writing agent.\n\nStructured output fields (LLMPrompt + LLMStructOut):\n- title, abstract, paper_text, figures, summary\n\npaper_text contains [FIGURE:fig_id] markers for positioning.\nfigures contains the full specs as structured objects.\n\nMetadata fields (plain, set by pipeline code):\n- id",
  "properties": {
    "title": {
      "description": "Paper title \u2014 clear, plain-language, and short so a non-expert understands the main contribution at a glance. Aim for about 6-10 words; avoid jargon and acronyms.",
      "title": "Title",
      "type": "string"
    },
    "abstract": {
      "description": "Paper abstract",
      "title": "Abstract",
      "type": "string"
    },
    "paper_text": {
      "description": "Full paper body text with markdown section headers (# Introduction, # Methods, # Results, # Discussion, # Conclusion). Use [FIGURE:fig_id] markers (e.g. [FIGURE:fig1]) to indicate where each figure should appear.",
      "title": "Paper Text",
      "type": "string"
    },
    "figures": {
      "description": "List of figure specifications. Each must have an id matching a [FIGURE:id] marker in paper_text.",
      "items": {
        "$ref": "#/$defs/FigureSpec"
      },
      "title": "Figures",
      "type": "array"
    },
    "summary": {
      "description": "Brief summary of the paper's main contribution and findings",
      "title": "Summary",
      "type": "string"
    }
  },
  "required": [
    "title",
    "abstract",
    "paper_text",
    "summary"
  ],
  "title": "PaperText",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `./.terminal_claude_agent_struct_out.json`.
````

### [2] HUMAN-USER prompt · 2026-07-08 10:51:47 UTC

```
Propose a simple, novel, testable ML method for near-duplicate text detection and validate it with a tiny experiment.
```

### [3] SKILL-INPUT — aii-paper-writing · 2026-07-08 10:51:51 UTC

The agent loaded the **aii-paper-writing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-writing
description: Academic paper writing guidance for AI research. Covers paper structure, figure placeholders, bibliography building with Semantic Scholar, and citation rules. Does NOT cover LaTeX compilation or figure file generation — see aii-paper-to-latex for that.
---

## Technical Papers

Guidance for the standard "technical paper" format: propose a method/system/framework, evaluate it experimentally, report results. This is the main track at most CS venues (NeurIPS, ICML, ICLR, ACL, AAAI, etc.). Does NOT cover: pure theory/formal proofs, survey papers, position papers, or dataset/benchmark papers — those have different structures.

### Paper Structure

Target 6-8 pages. Use formal academic language, third person. Support claims with evidence from artifacts.

#### Rough Page Budget (8-page paper)

| Section | Pages | Notes |
|---|---|---|
| Abstract | 0.3 | Problem, approach, key result |
| Introduction | 1.0-1.5 | The most important section |
| Related Work | 0.5-1.0 | Beginning or end (see below) |
| Methods | 1.5-2.0 | Architecture fig on page 1 |
| Experiments | 1.5-2.0 | Setup + results + ablations |
| Discussion | 0.5-1.0 | Limitations go here |
| Conclusion | 0.3-0.5 | Do not repeat the abstract |
| References | 0.5-1.0 | Not counted in page limit |

**Critical rule**: A clear new technical contribution must be articulated by page 3 (quarter of the paper). If the reader doesn't know what you did by then, you've lost them.

#### Section Details

**Abstract** (150-250 words): State the problem, your approach, and the main results. Be factual and comprehensive. Do not repeat the abstract word-for-word later in the paper.

**Introduction** — Follow this 5-paragraph structure:

1. **What is the problem?** Define the task concretely.
2. **Why is it interesting and important?** Real-world impact, scale.
3. **Why is it hard?** Why do naive approaches fail?
4. **Why hasn't it been solved before?** What's wrong with prior solutions? How does yours differ?
5. **What are the key components of your approach and results?** Include specific limitations.

End with a "Summary of Contributions" subsection — bullet list of contributions with section references. This doubles as an outline, saving space.

**Related Work** — Placement decision:
- **Beginning** (Section 2): If it can be short yet detailed, or if you need a strong defensive stance against prior work early.
- **End** (before Conclusions): If comparisons require your technical content, or if it can be summarized briefly in the Introduction. Can be titled "Discussion and Related Work."

**Methods/Approach**: Every section tells a story — the story of the results, NOT the story of how you arrived at them. Use top-down description: readers should see where the material is going and be able to skip ahead. Move gory details to appendices.

**Experiments**: Setup (datasets, metrics, baselines) → main results → ablations → analysis. Every claim needs quantitative evidence.

**Discussion**: Interpret results, compare to prior work, state limitations honestly. Limitations should be specific and actionable, not vague disclaimers.

**Conclusion**: Short summarizing paragraph. Do NOT repeat material from the Abstract or Introduction. Make original claims more concrete (e.g., reference quantitative results). Include future work as bullet list — if actively pursuing follow-up, say so to mark territory.

#### Writing Quality Rules

- Define all notation/terminology before use, only once. Group global definitions in Preliminaries.
- Do NOT use nonreferential "this", "that", "these", "it". Always specify the referent. BAD: "This is important because..." GOOD: "This accuracy gap is important because..."
- Do NOT use "etc." unless remaining items are completely obvious. BAD: "We measure volatility, scalability, etc." GOOD: "We measure volatility and scalability."
- Do NOT write "for various reasons" — state the actual reasons.
- "That" is defining, "which" is nondefining. "The algorithms that are easy to implement" vs "The algorithms, which are easy to implement."
- Use italics for definitions and quotes, not for emphasis. Context alone should provide emphasis.

### Figure Format

Figures use a hybrid marker + structured array approach. ALL figures are generated by a separate pipeline step using an AI image model — your `image_gen_detailed_description` is the ONLY input that model sees. It cannot read files or access data. Do NOT generate actual image files yourself (no matplotlib, no PIL, no image generation scripts).

**In paper_text**: Place `[FIGURE:fig_id]` markers where figures should appear.

**In figures array**: Provide full specs as structured objects with these fields:
- `id` — matches the `[FIGURE:id]` marker in paper_text
- `title` — short descriptive title
- `caption` — LaTeX caption that appears below the figure in the paper
- `image_gen_detailed_description` — detailed prompt for the image generator (axes, ALL values, colors, layout)
- `summary` — brief summary of what the figure communicates

Example in paper_text:
```
...our method achieves state-of-the-art results as shown below.

[FIGURE:fig_1]

The results in Figure 1 demonstrate...
```

Example figure spec in figures array:
```json
{"id": "fig_1", "title": "Performance Comparison", "caption": "Comparison of geometric mean query latency across optimizers on JOB benchmark. RLQOpt achieves 2.3x speedup over PostgreSQL.", "image_gen_detailed_description": "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: ModelA=0.847, ModelB=0.762, Baseline=0.531. Error bars with std: 0.02, 0.03, 0.05. Sans-serif font, white background.", "summary": "Compares accuracy of proposed methods vs baseline."}
```

Every marker in text MUST have a matching figure in the array, and vice versa.

#### Data Precision Requirement

`image_gen_detailed_description` MUST include exact numbers from artifact output files. Read the actual output files before writing figure specs.

- BAD: "Compare accuracy metrics across configurations"
- GOOD: "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: K=3: 0.765, K=5: 0.729, Baseline: 0.121."

#### Figure vs Table Decision

Do NOT create figures for tabular data (rows/columns of text or numbers). Use `\begin{table}` in LaTeX instead. Figures are for actual visualizations only (charts, plots, diagrams).

#### Figure Placement Strategy

Be intentional with figure ordering. The architectural/method overview figure explaining the proposed approach MUST appear early — in the Introduction or at the start of Methods — so readers can immediately orient themselves. Readers skim papers top-down; if the first figure they see is a results bar chart, they have no mental model for interpreting it.

Recommended ordering:
1. **Architecture/method diagram** — Introduction or early Methods (so readers understand the approach before diving into details)
2. **Conceptual/analogy figures** — Introduction or Methods (to build intuition)
3. **Results figures** (bar charts, line plots, scatter plots) — Results section
4. **Analysis/ablation figures** — Discussion or later Results

#### Guidelines

- Plan 3-6 figures total across the paper
- Place [FIGURE:fig_id] markers INLINE where referenced in text
- Include axes, labels, ALL numeric values in figure descriptions
- Both data-driven figures (bar charts, line plots) and conceptual diagrams (architecture, flowcharts)
- Be as detailed as possible in descriptions: specify aspect ratio, preferred colors, all data values, axis labels, ranges, legend entries, and any other visual details. The more specific the description, the better the generated figure

### Bibliography with Semantic Scholar

Build `./references.bib` using the aii-semscholar-bib skill (real BibTeX from Semantic Scholar):

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in one batch
3. Write the returned .bib text into `./references.bib`

Rules:
- Do NOT fabricate BibTeX entries — always fetch from Semantic Scholar
- If a paper isn't found (very recent preprint), write the entry manually as fallback
- Use `\bibliography{references}` and `\bibliographystyle{plainnat}`
- Do NOT use inline `thebibliography` environment

### Citation Format (for Research Artifacts)

When writing research with numbered citations:

1. Every factual claim MUST have a numbered citation: `[1]`, `[2]`, `[1, 3]`, etc.
2. Each source in the "sources" array MUST have an "index" field
3. The index MUST EXACTLY MATCH citation numbers in the text
4. NEVER cite a number without a matching source index
5. Example: "LLMs show 40% improvement with multi-agent collaboration [1]."
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-07-08 10:51:55 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: Build bibliographies using Semantic Scholar. Batch-fetch BibTeX for papers by DOI, ArXiv ID, or title. Use when writing papers, generating reference lists, or building .bib files.
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar. Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Post-process** → fix entry type, fix citation key (AuthorYYYY), inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": ""}],
  "failed": []
}
```

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in **one call**
3. Save `bib_text` from the response to your `references.bib` file
4. Check `failed` — for any missed papers, follow the **fallback procedure** below

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract title, authors, year, venue, DOI/ArXiv ID
3. If DOI/ArXiv found → retry `aii_semscholar_bib__fetch` with it
4. Last resort: write BibTeX by hand using **only verified info from the actual paper page**

---

### CLI (for manual use / debugging)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````
