# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_E1yko-FJ_C_D` — Edit Clustering Score: Spatial Edit Patterns for Near-Duplicate Text Detection
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-07-08 11:58:32 UTC

````
<research_methodology>
Write like an experienced academic. Reviewers judge both the science and the writing.

- Claims must be proportional to evidence. Choose verbs carefully — "demonstrate," "observe," and "hypothesize" mean different things.
- Every result needs: what was measured, on what data, the numbers, and what they mean.
- Methodology must be specific enough to reproduce. Related work must be organized by theme, not a literature dump.
- State limitations honestly. Avoid both overclaiming and excessive hedging.
</research_methodology>

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
Your workspace: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/4_gen_paper_repo/_4_assemble_paper/paper/workspace`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/4_gen_paper_repo/_4_assemble_paper/paper/workspace/`:
GOOD: `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/4_gen_paper_repo/_4_assemble_paper/paper/workspace/file.py`, `/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/4_gen_paper_repo/_4_assemble_paper/paper/workspace/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>

<task>
Create a publication-ready top-conference LaTeX paper with BibTeX from <paper_text> and <available_figures>, compile to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<paper_text>
title: 'Edit Clustering Score: Spatial Edit Patterns for Near-Duplicate Text Detection'
abstract: >-
  Near-duplicate text detection at scale relies on n-gram Jaccard similarity (MinHash/SimHash), which measures the quantity
  of shared tokens but ignores the spatial arrangement of differences. We propose the Edit Clustering Score (ECS), a training-free
  feature derived from the Index of Dispersion (IoD) of inter-edit-gap positions in a word-level longest-common-subsequence
  diff—a transplant of spatial point-process statistics from ecology to text analysis. The core finding is a productive directional
  inversion: near-duplicates created by contiguous splicing produce a single concentrated edit block (low IoD), while documents
  sharing scattered vocabulary coincidentally produce many dispersed edit events (high IoD). Inverted ECS (1/IoD) therefore
  flags near-duplicates. On a 900-pair Wikipedia benchmark with balanced near-duplicate, same-category, and random classes,
  inverted ECS alone achieves AUC = 0.81 ± 0.025 (vs. Jaccard AUC = 1.000), confirmed by a Mann-Whitney test comparing near-duplicate
  IoD (median 20.3) vs. hard-negative IoD (median 81.8), $p = 4 \times 10^{-39}$, Cohen's $d = -0.83$ on log-IoD. We further
  construct a boilerplate hard-negative benchmark where unrelated article pairs share an identical CC-BY-SA license header
  to probe whether ECS can correct boilerplate-inflated Jaccard scores; we find that the 180-word header raises hard-negative
  5-gram Jaccard to only 0.09–0.15, still far below near-duplicate Jaccard (0.42–0.75), so Jaccard remains a perfect ceiling
  classifier on both benchmarks. These results establish that spatial edit clustering is a genuine structural signal (AUC
  = 0.81 standalone) but is redundant with 5-gram Jaccard in splice-based constructions. ECS would become complementary in
  settings where Jaccard is degraded: longer shared boilerplate, multi-segment edits, or short-shingle baselines.
paper_text: |-
  # Introduction

  Near-duplicate text detection is a foundational task in web crawling, LLM training data curation, and plagiarism detection. At scale—hundreds of billions of documents—exhaustive pairwise comparison is computationally infeasible, motivating compact hash-based methods that estimate Jaccard similarity over character or word shingles [1, 2]. These methods share a common architectural assumption: they measure the *quantity* of token overlap but are blind to the *spatial arrangement* of differences. Two documents may share 60% of their 5-grams because one is a localized edit of the other (a near-duplicate) or because both discuss the same topic with shared domain vocabulary and boilerplate conventions (a thematic near-match). Current methods cannot distinguish these cases without auxiliary metadata.

  We ask: can the geometric pattern of where edits occur in a word-level diff distinguish genuine near-duplicates from coincidental lexical overlap? The answer has practical stakes for LLM training data pipelines [5, 6, 9, 10], where false positives (rejecting legitimately distinct documents) and false negatives (retaining near-copies that promote memorization) each carry costs. FineWeb [9] and RefinedWeb [10] apply MinHash deduplication as a standard preprocessing step, but acknowledge that boilerplate-inflated Jaccard scores can cause false positives. A spatial diagnostic orthogonal to token counts could serve as a fast second-pass filter.

  The intuition for a spatial feature comes from spatial ecology. The Index of Dispersion (IoD = variance/mean of inter-event gap lengths) is a classical test for whether a 1D point process is clustered (IoD $\gg 1$), Poisson-random (IoD $\approx 1$), or regular (IoD $\ll 1$) [11]. Transplanting this to edit positions in a word-level diff defines the Edit Clustering Score (ECS): run a longest-common-subsequence (LCS) diff [12], extract word-index positions of all edit tokens, compute IoD of the inter-gap sequence.

  Our experiments on two 900-pair Wikipedia benchmarks yield a clear finding with an instructive directional inversion: near-duplicates produced by contiguous splicing have *lower* median IoD (20.3) than hard negatives (81.8), $p = 4 \times 10^{-39}$, Cohen's $d = -0.83$ on log-IoD \footnote{Code: \url{https://github.com/AMGrobelnik/ai-invention-f2202a-edit-clustering-score-spatial-edit-patte/tree/main/round-2/experiment-1}}. The mechanism is clear in retrospect: a contiguous splice produces one large edit block, concentrating all edits in one region and suppressing inter-gap variance; the correct discriminant is therefore *inverted* ECS (low IoD $\to$ near-duplicate). Inverted ECS achieves AUC = 0.81 $\pm$ 0.025 as a standalone classifier, confirming that spatial edit structure is a genuine and highly discriminating signal.

  The reason ECS does not improve over Jaccard is a dataset construction artifact rather than a limitation of the spatial signal: contiguous splicing directly inflates 5-gram Jaccard (near-duplicate median $J_5 = 0.58$ vs. $J_5 \approx 0$ for both negative classes), making Jaccard a perfect ceiling classifier. To probe the boilerplate regime where Jaccard would plausibly fail, we construct a second benchmark prepending unrelated article pairs with an identical CC-BY-SA license header. The header raises hard-negative $J_5$ to only 0.09–0.15—not the 0.3–0.6 range needed to challenge Jaccard—so Jaccard remains a perfect classifier on this benchmark as well \footnote{Code: \url{https://github.com/AMGrobelnik/ai-invention-f2202a-edit-clustering-score-spatial-edit-patte/tree/main/round-2/dataset-1}}.

  [FIGURE:fig1]

  **Summary of Contributions:**
  \begin{itemize}
      \item We introduce the Edit Clustering Score (ECS), a training-free feature based on the Index of Dispersion of inter-edit-gap positions in a word-level LCS diff, with a corrected directional prediction: low IoD flags near-duplicates (Section~\ref{sec:method}).
      \item We construct two 900-pair Wikipedia benchmarks: a splice-based benchmark (Section~\ref{sec:data}) and a boilerplate hard-negative benchmark targeting the Jaccard-degraded regime (Section~\ref{sec:data}).
      \item We demonstrate that inverted ECS captures a strong standalone structural signal (AUC = 0.81), with IoD distributions separated by $p = 4 \times 10^{-39}$ and Cohen's $d = -0.83$ (Section~\ref{sec:results}).
      \item We identify precisely why ECS cannot complement Jaccard in the current benchmarks, and characterize the conditions under which it would (Section~\ref{sec:discussion}).
  \end{itemize}

  # Related Work
  \label{sec:related}

  **MinHash and SimHash.** Broder [1] introduced min-wise independent permutations (MinHash) to estimate Jaccard similarity over character $k$-grams at web scale; the AltaVista crawler used this to cluster tens of millions of near-duplicate pages. Manku et al. [2] introduced SimHash, a locality-sensitive hashing scheme based on random projections of TF-IDF feature vectors, enabling near-duplicate detection in $O(1)$ per query using Hamming distance lookup. Both methods operate on bag-of-shingles representations and are entirely insensitive to the spatial arrangement of differences.

  **Neural similarity.** RETSim [3] (Zhang et al., 2023) trains a character-level embedding model specifically for near-duplicate detection, achieving high throughput and robustness to adversarial edits. ECS is complementary: it is training-free, requires no labeled data, and provides an interpretable geometric characterization of where documents differ.

  **Compression-based similarity.** The normalized compression distance (NCD; Li et al. [4]) uses the ratio of joint to individual compression lengths as a similarity proxy, implicitly capturing repeated structure. NCD is sensitive to spatial redundancy in that repeated substrings compress better, but does not expose edit positions or their clustering.

  **LLM training data deduplication.** Lee et al. [5] showed that exact and near-duplicate deduplication of pretraining corpora substantially improves LLM quality by reducing memorization and improving sample diversity. FineWeb [9] and RefinedWeb [10] apply MinHash as a standard preprocessing step at web scale. Abbas et al. [7] introduced SemDeDup, which clusters semantic embeddings to remove near-semantic-duplicates—a different regime from lexical near-duplication. None of these approaches exploit the spatial structure of differences; ECS is proposed as a complementary diagnostic applicable when Jaccard alone is insufficient.

  **Passage-level plagiarism detection.** Nawab et al. [8] detect copied passages using TF-IDF clustering followed by sequence alignment of candidate passages. This approach groups matching passages spatially but uses frequency vectors rather than point-process statistics on diff positions, and targets cross-document passage reuse rather than pairwise near-duplicate classification.

  **Spatial point processes.** The Index of Dispersion and related statistics (Ripley's $K$, Morisita's index) are standard tools in spatial ecology and geography for classifying point patterns as clustered, random, or regular [11]. Their application to text analysis—treating edit positions as a 1D spatial point process—is, to our knowledge, novel.

  # Dataset Construction
  \label{sec:data}

  We construct two 900-pair benchmarks from Wikipedia articles retrieved via the MediaWiki API [ARTIFACT:art_of-sMCpCSjl5]. All texts are 80–800 words in English.

  ## Splice-Based Wikipedia Benchmark

  The splice-based benchmark contains 900 balanced pairs across three classes (300 each).

  **Near-duplicates.** For each near-duplicate pair, text\_b is constructed from text\_a by identifying a contiguous 20–30\% word span and replacing it with corresponding content from an unrelated donor article from a different Wikipedia category. The 5-gram Jaccard similarity ranges from 0.50 to 0.75 (mean 0.58), as the unchanged 70–80\% of the article contributes to substantial 5-gram overlap.

  **Same-category hard negatives.** Hard-negative pairs consist of two independently written articles from the same Wikipedia category (e.g., two science articles, two sports articles). These pairs share domain vocabulary, named entities, and structural conventions but have no textual copying relationship. Their 5-gram Jaccard similarity is near zero (mean $\approx$ 0.001), confirming that 5-gram Jaccard cleanly separates this class from near-duplicates in this construction.

  **Random pairs.** Random pairs are drawn from articles in different categories, serving as easy negatives with near-zero Jaccard similarity.

  ## Boilerplate Hard-Negative Benchmark

  To test whether ECS provides complementary signal when Jaccard is degraded by shared non-content text, we construct a second 900-pair benchmark  with the same near-duplicate and random classes, but replacing the same-category hard negatives with **boilerplate hard negatives**: two completely unrelated Wikipedia articles, each prepended with an identical $\sim$180-word CC-BY-SA license and usage disclaimer block. The boilerplate header is designed to inflate Jaccard similarity for unrelated document pairs while providing no genuine duplication signal.

  The boilerplate hard-negative pairs achieve a mean 5-gram Jaccard of 0.089–0.15 (mean boilerplate\_frac $\approx$ 0.83, confirming that most shared signal comes from the header). This is substantially higher than the same-category hard negatives ($J_5 \approx 0$), but still well below the near-duplicate range (0.50–0.75).

  # Method: Edit Clustering Score
  \label{sec:method}

  ## Word-Level Diff

  Given a text pair $(A, B)$, we tokenize both texts into word sequences by whitespace splitting after lowercasing. We compute the LCS alignment using Python's \texttt{difflib.SequenceMatcher} [13], which identifies matched and unmatched token spans. Each unmatched token (an insertion or deletion in the diff) is assigned a position index in the concatenated aligned sequence.

  ## Index of Dispersion on Edit Positions

  Let $p_1 < p_2 < \cdots < p_k$ be the sorted positions of all edit tokens, and let $g_i = p_{i+1} - p_i$ for $i = 1, \ldots, k-1$ be the sequence of inter-edit gaps. The Edit Clustering Score is:
  $$
  \text{ECS} = \text{IoD}(g) = \frac{\text{Var}(g)}{\text{Mean}(g)}
  $$
  when $k \geq 3$; otherwise ECS = 0 by convention. For a homogeneous Poisson process (random scattering of edits), IoD = 1 in expectation. IoD $\gg 1$ indicates high-variance gaps (few, large clusters separated by long stretches of matching text). IoD $\ll 1$ indicates regular, uniform spacing.

  The discriminant direction is **inverted relative to the original ecological analogy**. A contiguous splice produces *one* large edit block: two or three gap values, all similar in length, giving low variance and thus low IoD. By contrast, two independent articles on the same topic share isolated words, phrases, and named entities scattered throughout, producing many small edit events with high inter-gap variance and thus high IoD. The correct inference is therefore: **low ECS (IoD) indicates near-duplication by contiguous local editing**.

  The inverted classifier uses $-\text{ECS}$ (equivalently, $1/\text{ECS}$) as a near-duplicate score. In practice a logistic regression on $[-\text{ECS}]$ is equivalent to fitting $\text{ECS}$ with a negated coefficient.

  ## Auxiliary Features

  We compute three auxiliary edit-structure features alongside ECS:
  \begin{itemize}
      \item \textbf{edit\_count\_norm}: Number of edit tokens divided by total aligned length.
      \item \textbf{edit\_span\_frac}: Fraction of the aligned sequence spanned from the first to the last edit token (edit coverage). Mean values: near-duplicate 0.81, hard-negative 0.96, reflecting that splice edits are concentrated in one region while coincidental edits span the full text.
      \item \textbf{longest\_run\_frac}: Length of the longest contiguous edit run, divided by total edit count (concentration ratio).
  \end{itemize}

  ## Classifiers

  We evaluate five classifier variants using 5-fold stratified cross-validation with logistic regression:
  \begin{enumerate}
      \item \textbf{Jaccard-5 only}: 5-gram Jaccard as the sole feature.
      \item \textbf{Jaccard-2 only}: 2-gram Jaccard as the sole feature (degraded baseline).
      \item \textbf{Inv-ECS only}: Inverted ECS ($-\text{IoD}$) as the sole feature.
      \item \textbf{Jaccard-2 + Inv-ECS}: 2-gram Jaccard combined with inverted ECS.
      \item \textbf{All features}: Jaccard-5, Jaccard-2, inverted ECS, edit\_count\_norm, edit\_span\_frac, longest\_run\_frac.
  \end{enumerate}

  We report ROC-AUC (macro-averaged across folds) with bootstrap confidence intervals ($B = 2000$) and Mann-Whitney $U$ tests comparing IoD distributions.

  # Results
  \label{sec:results}

  ## IoD Distributions Confirm Structural Signal with Inverted Directionality

  [FIGURE:fig2]

  Across both benchmarks, near-duplicate pairs have significantly *lower* median IoD (20.3) than hard-negative pairs (median IoD 81.8 on the splice benchmark; 80.9 on the boilerplate benchmark), with Mann-Whitney $p = 4 \times 10^{-39}$ and Cohen's $d = -0.83$ on log-IoD . The magnitude and directionality are consistent across both Wikipedia and boilerplate benchmarks, confirming that the spatial signal is robust to the type of hard-negative construction.

  The mechanism is straightforward. A contiguous splice replaces one block of words: long stretches of identical text bracket one region of complete mismatch. This produces few inter-edit gaps, all of similar length—minimizing variance and thus IoD. Hard negatives (same-category pairs or boilerplate pairs) share isolated vocabulary items and short phrases distributed throughout both articles, producing many small edit events spread across the text; the variance of many small gaps is high, giving high IoD.

  Table 1 summarizes feature statistics by class on the splice-based Wikipedia benchmark.

  \begin{table}[h]
  \centering
  \caption{Median feature values by pair class on the splice-based 900-pair Wikipedia benchmark (300 pairs each class). Edit span frac captures the fraction of the aligned sequence between the first and last edit token.}
  \begin{tabular}{lcccc}
  \hline
  Class & 5-gram Jaccard & ECS (IoD) & Edit Span Frac & Edit Count Norm \\
  \hline
  Near-duplicate & 0.582 & 20.3 & 0.81 & 0.24 \\
  Hard negative & 0.001 & 81.8 & 0.96 & 0.68 \\
  Random & 0.000 & 47.5 & 0.94 & 0.72 \\
  \hline
  \end{tabular}
  \end{table}

  ## Classification Results

  Table 2 presents AUC results from 5-fold cross-validation on both benchmarks .

  \begin{table}[h]
  \centering
  \caption{ROC-AUC (mean $\pm$ std, 5-fold CV) on the hard subset (near-duplicate vs. hard-negative only) for both benchmarks. Jaccard achieves AUC = 1.000 on both datasets; inverted ECS achieves AUC $\approx$ 0.81 standalone; combining features does not improve over Jaccard alone.}
  \begin{tabular}{lcc}
  \hline
  Classifier & Splice Benchmark & Boilerplate Benchmark \\
  \hline
  Jaccard-5 only & 1.000 $\pm$ 0.000 & 1.000 $\pm$ 0.000 \\
  Jaccard-2 only & 1.000 $\pm$ 0.000 & 1.000 $\pm$ 0.000 \\
  Inverted ECS only & 0.809 $\pm$ 0.025 & 0.807 $\pm$ 0.037 \\
  Jaccard-2 + Inv-ECS & 1.000 $\pm$ 0.000 & 1.000 $\pm$ 0.000 \\
  All features & 1.000 $\pm$ 0.000 & 1.000 $\pm$ 0.000 \\
  \hline
  \end{tabular}
  \end{table}

  [FIGURE:fig3]

  Three findings stand out:

  **Inverted ECS alone achieves AUC = 0.81 as a standalone signal.** This result holds consistently across both the splice-based benchmark (AUC = 0.809 $\pm$ 0.025) and the boilerplate benchmark (AUC = 0.807 $\pm$ 0.037). It confirms that spatial edit clustering carries genuine discriminative information about the type of textual relationship, independently of any $n$-gram overlap measure.

  **5-gram and 2-gram Jaccard both achieve perfect AUC = 1.000 on both benchmarks.** Contiguous splicing inflates $J_5$ for near-duplicates to mean 0.58, while both negative classes have $J_5 < 0.002$. Even 2-gram Jaccard remains a perfect separator in this construction, indicating the ceiling effect is not an artifact of $k$-gram length.

  **Boilerplate augmentation does not break the Jaccard ceiling.** The boilerplate hard-negative pairs achieve mean $J_5 = 0.089$–$0.15$—substantially higher than the original same-category negatives ($J_5 \approx 0$), but still well below the near-duplicate range ($J_5 = 0.50$–$0.75$). The $\sim$180-word CC-BY-SA header was insufficient to raise hard-negative Jaccard into the ambiguous region where ECS would add signal. The $\Delta$AUC for Jaccard-2 + Inv-ECS vs. Jaccard-2 alone is 0.000 (bootstrap 95\% CI: $[-1.1 \times 10^{-16}, +1.1 \times 10^{-16}]$) on both benchmarks.

  ## Jaccard Distribution Comparison Across Benchmarks

  [FIGURE:fig4]

  Figure 4 shows the $J_5$ distributions by class on both benchmarks. On the splice benchmark, near-duplicate and hard-negative distributions are entirely non-overlapping. On the boilerplate benchmark, the hard-negative distribution shifts upward (from $J_5 \approx 0$ to $J_5 \approx 0.09$–$0.15$) but still does not overlap with the near-duplicate distribution. The figure makes visible why Jaccard remains a perfect classifier: in neither benchmark does any hard-negative pair reach the near-duplicate Jaccard range.

  # Discussion
  \label{sec:discussion}

  ## Addressing the Directional Inversion

  The original ecological analogy predicted IoD $\gg 1$ for near-duplicates (local edits = clustered events = high gap variance). This prediction conflates two distinct senses of clustering: (a) *spatial concentration* (edits occur in one region) and (b) *statistical clustering* in the point-process sense (high inter-event gap variance). A single contiguous edit block is the most spatially concentrated arrangement possible, but it produces only a small number of similarly-sized gaps—a nearly degenerate distribution with low variance. The IoD therefore measures the *number and regularity* of edit clusters, not the spatial concentration of a single cluster. Future formulations targeting single-cluster detection should use statistics such as the concentration ratio (`longest_run_frac`) or spatial entropy of the edit density.

  ## Why Boilerplate Augmentation Was Insufficient

  The boilerplate benchmark was designed to put hard negatives in the Jaccard range 0.3–0.6, where ECS would need to distinguish distributed overlap (from boilerplate) from localized overlap (from splicing). This required boilerplate of substantial length relative to the article body. The CC-BY-SA license header at $\sim$180 words raised hard-negative $J_5$ to only 0.089–0.15 against articles of 80–800 words. To achieve $J_5 > 0.3$ for hard negatives, the boilerplate would need to constitute more than 30% of total article length—a regime common in legal documents, terms-of-service pages, and structured templates (e.g., Wikipedia infoboxes), but not reproduced by a short license header alone.

  ## When ECS Would Complement Jaccard

  The failure to improve over Jaccard is specific to the experimental constructions. ECS becomes a complementary signal in three concrete scenarios:

  1. **Long shared boilerplate.** When legal headers, disclaimers, or structural templates constitute $>$30\% of document length, unrelated documents can reach $J_5 > 0.3$. ECS would correctly identify such pairs as high-IoD (distributed overlap), while splice-based near-duplicates remain low-IoD.

  2. **Multi-segment edits.** If near-duplicates involve two or more separated edit regions (introduction and conclusion both rewritten), the IoD of those clusters would be higher, converging toward the hard-negative regime. In this scenario, `longest_run_frac` (the fraction of edits in the longest contiguous run) would be a more robust discriminant.

  3. **Short-shingle regimes.** For character-level unigram or bigram Jaccard on noisy or highly paraphrased text, the Jaccard ceiling breaks. ECS provides an orthogonal structural signal in this regime.

  ## Data Consistency Across Iterations

  A discrepancy in the previous paper draft required correction: the cross-validation AUC of 0.973 cited in the prior iteration was computed on synthetic vocabulary-template data (300-word articles generated from 5 topic-specific 60-word vocabularies), not on the Wikipedia benchmark described in the paper. The current experiments run all classifiers on consistent Wikipedia data, yielding a correctly calibrated inverted-ECS AUC of 0.809 $\pm$ 0.025 on the hard subset.

  ## Limitations

  **Synthetic near-duplicates only.** All near-duplicates are constructed by contiguous splicing. Real-world near-duplication involves multiple separated edits, sentence reordering, word substitution, and paraphrase—patterns with different IoD signatures. The experiment should be replicated on corpora of Wikipedia revision histories or PAN plagiarism detection corpora.

  **Single domain.** The benchmark draws entirely from Wikipedia, which has consistent article structure, neutral tone, and encyclopedic vocabulary. Results may not generalize to web-crawled text with diverse formatting, legal boilerplate, or domain-specific jargon that constitutes a large fraction of document length.

  **Small scale.** Nine hundred pairs is sufficient to measure large effects but may underestimate variance in smaller IoD effect sizes. Large-scale evaluation on corpora used in LLM data pipelines (FineWeb [9], RefinedWeb [10]) remains future work.

  # Conclusion

  We proposed the Edit Clustering Score, a training-free near-duplicate detection feature derived from the Index of Dispersion of inter-edit-gap positions in a word-level LCS diff. The spatial-point-process framing—transplanting IoD from spatial ecology to the 1D sequence of edit positions—is novel in the near-duplicate detection literature. Our corrected main finding is that ECS direction is inverted from the original ecological analogy: contiguous splice-based near-duplicates produce low IoD (one concentrated edit block), while documents sharing scattered coincidental vocabulary produce high IoD (many dispersed edit events). Inverted ECS achieves AUC = 0.81 as a standalone classifier, confirming the discriminative reality of spatial edit structure. ECS does not currently improve over 5-gram Jaccard because splice construction inflates Jaccard perfectly, and our 180-word boilerplate augmentation was insufficient to push hard-negative Jaccard into the ambiguous 0.3–0.6 range.

  The clearest path to demonstrating ECS complementarity is a benchmark where boilerplate constitutes $>$30\% of document length (legal or structured content), or a natural revision history corpus where edits are not restricted to single contiguous blocks. We release both benchmarks and all code to support this follow-up work.

  # References

  [1] A. Broder. On the resemblance and containment of documents. *Proceedings of Compression and Complexity of SEQUENCES*, 1997, pp. 21--29.

  [2] G. Manku, A. Jain, and A. Sarma. Detecting near-duplicates for web crawling. *Proceedings of WWW*, 2007, pp. 141--150.

  [3] M. Zhang, O. Vallis, A. Bumin, T. Vakharia, and E. Bursztein. RETSim: Resilient and efficient text similarity. *ICLR*, 2023.

  [4] M. Li, X. Chen, X. Li, B. Ma, and P. Vitányi. The similarity metric. *IEEE Transactions on Information Theory*, 50(12):3250--3264, 2004.

  [5] K. Lee, D. Ippolito, A. Nystrom, C. Zhang, D. Eck, C. Callison-Burch, and N. Carlini. Deduplicating training data makes language models better. *ACL*, 2022, pp. 8424--8445.

  [6] L. Gao et al. The Pile: An 800GB dataset of diverse text for language modeling. *arXiv:2101.00027*, 2020.

  [7] A. Abbas, K. Tirumala, D. Simig, S. Ganguli, and A. S. Morcos. SemDeDup: Data-efficient learning at web-scale through semantic deduplication. *arXiv:2303.09540*, 2023.

  [8] R. M. A. Nawab, M. Stevenson, and P. D. Clough. External plagiarism detection using information retrieval and sequence alignment. *CLEF*, 2011.

  [9] G. Penedo et al. The FineWeb datasets: Decanting the web for the finest text data at scale. *NeurIPS*, 2024.

  [10] G. Penedo et al. The RefinedWeb dataset for Falcon LLM. *arXiv:2306.01116*, 2023.

  [11] D. R. Cox and P. A. W. Lewis. *The Statistical Analysis of Series of Events*. Methuen, 1966.

  [12] J. W. Hunt and T. G. Szymanski. A fast algorithm for computing longest common subsequences. *Commun. ACM*, 20(5):350--353, 1977.

  [13] T. Peters. difflib: Helpers for computing deltas. *Python Standard Library*, 2001.

  \bibliographystyle{plainnat}
  \bibliography{references}
summary: >-
  This paper introduces the Edit Clustering Score (ECS), a training-free near-duplicate detection feature based on the Index
  of Dispersion of inter-edit-gap positions in a word-level LCS diff—transplanting spatial point-process statistics from ecology
  to text analysis. The key finding is a directional inversion: contiguous-splice near-duplicates produce low IoD (one concentrated
  edit block), while documents with coincidental vocabulary overlap produce high IoD (many scattered edits). Inverted ECS
  achieves AUC = 0.81 standalone but cannot improve over 5-gram Jaccard (AUC = 1.000) in splice-based benchmarks, and a boilerplate
  augmentation experiment confirms that a 180-word CC-BY-SA header is insufficient to push hard-negative Jaccard into the
  ambiguous range where ECS would add signal.
</paper_text>

<available_figures>
--- Item 1 ---
id: fig1
title: 'ECS Pipeline: From Text Pair to Edit Clustering Score'
caption: >-
  The Edit Clustering Score (ECS) pipeline. Given a text pair, a word-level LCS diff extracts edit positions; the Index of
  Dispersion of inter-edit gaps quantifies spatial clustering. Near-duplicates (contiguous splice) produce one large block
  and low IoD; thematic near-matches produce many small scattered edits and high IoD. The inverted score (1/IoD or equivalently
  $-$IoD) serves as the near-duplicate signal.
image_gen_detailed_description: >-
  Horizontal left-to-right flow diagram. Five labeled stages connected by arrows: (1) 'Text Pair (A, B)' — light gray box;
  (2) 'Word-Level LCS Diff' — blue box showing two text strips with colored segments (green=match, red=edit); (3) 'Edit Positions
  [p1, p2, ..., pk]' — light blue narrow box showing a 1D axis with vertical red tick marks clustered together for near-dup
  or scattered for hard-neg; (4) 'Inter-Gap Sequence [g1, g2, ..., gk-1]' — light blue box; (5) 'ECS = Var(g)/Mean(g) = IoD'
  — orange box. Below the main flow, two outcome callout boxes side by side: left box labeled 'Near-Duplicate (splice): ONE
  block, low variance, IoD ≈ 20 → LOW ECS → near-dup flag'; right box labeled 'Hard Negative (scattered): MANY events, high
  variance, IoD ≈ 82 → HIGH ECS → not near-dup'. Sans-serif font, clean white background, no 3D effects. Aspect ratio 21:9.
aspect_ratio: '21:9'
summary: >-
  Hero pipeline diagram showing how ECS transforms a text pair into a near-duplicate score via LCS diff and Index of Dispersion
figure_path: figures/fig1_v0.jpg

--- Item 2 ---
id: fig2
title: IoD Distributions by Pair Class
caption: >-
  Distribution of log-IoD (Edit Clustering Score) by pair class on the splice-based Wikipedia benchmark (300 pairs per class).
  Near-duplicate pairs (contiguous splice) have significantly lower IoD (median 20.3) than hard-negative same-category pairs
  (median 81.8) or random pairs (median 47.5). Mann-Whitney $p = 4 \times 10^{-39}$, Cohen's $d = -0.83$ on log-IoD. The inverted
  ECS (low IoD $\to$ near-duplicate) achieves AUC = 0.81 standalone.
image_gen_detailed_description: >-
  Horizontal violin plot or box-and-whisker plot showing log10(IoD) distribution for three classes. X-axis: log10(IoD), range
  0 to 3.5 (i.e., IoD from 1 to ~3000). Three rows (classes): (1) 'Near-Duplicate' — orange/coral color — median log10(IoD)=1.307
  (IoD=20.3), distribution centered around 0.8-1.8, tight; (2) 'Hard Negative' — blue — median log10(IoD)=1.913 (IoD=81.8),
  distribution spread 1.2-2.6; (3) 'Random' — green — median log10(IoD)=1.677 (IoD=47.5), distribution spread 1.0-2.5. Vertical
  dashed line at log10(20.3)=1.307 labeled 'Near-dup median'. Vertical dashed line at log10(81.8)=1.913 labeled 'Hard-neg
  median'. Annotation: 'p = 4e-39, Cohen d = -0.83'. Each class shows median dot, IQR box, and whiskers. Sans-serif font,
  white background. Aspect ratio 16:9.
aspect_ratio: '21:9'
summary: >-
  Shows near-duplicates have significantly lower IoD than hard negatives, confirming inverted spatial signal
figure_path: figures/fig2_v0.jpg

--- Item 3 ---
id: fig3
title: AUC Comparison Across Classifier Variants
caption: >-
  ROC-AUC on the near-duplicate vs. hard-negative hard subset (5-fold CV) for five classifier variants on both benchmarks.
  Jaccard (5-gram and 2-gram) achieves perfect AUC = 1.000 on both datasets. Inverted ECS alone achieves AUC = 0.809 on the
  splice benchmark and AUC = 0.807 on the boilerplate benchmark. Adding ECS to Jaccard yields no improvement ($\Delta$AUC
  $\approx$ 0) because Jaccard is already a perfect separator.
image_gen_detailed_description: >-
  Grouped bar chart. X-axis: 5 classifier variants — 'J5 only', 'J2 only', 'Inv-ECS only', 'J2+Inv-ECS', 'All features'. Y-axis:
  AUC from 0.75 to 1.05, major gridlines at 0.80, 0.85, 0.90, 0.95, 1.00. Two groups per variant (side by side bars): dark
  blue = 'Splice Benchmark', light blue = 'Boilerplate Benchmark'. Values: J5-only: 1.000, 1.000; J2-only: 1.000, 1.000; Inv-ECS-only:
  0.809, 0.807; J2+Inv-ECS: 1.000, 1.000; All-features: 1.000, 1.000. Error bars for Inv-ECS-only: splice ±0.025, boilerplate
  ±0.037. Horizontal dashed red line at 0.810 labeled 'Inv-ECS standalone'. Annotation above Jaccard bars: 'Ceiling: AUC=1.000'.
  Legend top right. Sans-serif font, white background. Aspect ratio 16:9.
aspect_ratio: '21:9'
summary: >-
  Bar chart comparing AUC across classifier variants on both benchmarks, showing Jaccard ceiling and ECS standalone performance
figure_path: figures/fig3_v0.jpg

--- Item 4 ---
id: fig4
title: '5-gram Jaccard Distributions: Splice vs. Boilerplate Benchmarks'
caption: >-
  5-gram Jaccard ($J_5$) distributions by pair class on both benchmarks. On the splice benchmark (top), near-duplicate pairs
  have $J_5 \in [0.50, 0.75]$ (mean 0.58) while both negative classes have $J_5 \approx 0$, creating a perfect separation.
  On the boilerplate benchmark (bottom), the boilerplate hard-negative class shifts upward to $J_5 = 0.09$--$0.15$ (mean 0.089)
  due to the shared CC-BY-SA header, but still does not overlap with the near-duplicate range—explaining why Jaccard remains
  a perfect classifier on this benchmark.
image_gen_detailed_description: >-
  Two-panel figure stacked vertically. Top panel: 'Splice Benchmark' — horizontal density/histogram plot. Three overlapping
  distributions along x-axis (Jaccard 0 to 0.85): 'Near-Duplicate' (orange, centered at 0.58, range 0.50-0.75, narrow peak);
  'Hard Negative' (blue, spike at 0.000-0.005, very narrow); 'Random' (green, spike at 0.000-0.002). Large gap between near-dup
  and negatives with annotation 'Perfect separation'. Bottom panel: 'Boilerplate Benchmark' — same layout. Three distributions:
  'Near-Duplicate' (orange, centered at 0.58, range 0.50-0.75); 'Boilerplate Hard-Neg' (blue, centered at 0.089, range 0.05-0.15,
  shifted right from zero but still far from near-dup); 'Random' (green, spike at 0.000). Gap between boilerplate hard-neg
  (0.15 max) and near-dup (0.50 min) is ~0.35 with annotation 'Still separated: gap = 0.35'. X-axis label: '5-gram Jaccard
  (J5)'. Y-axis: density. Sans-serif font, white background. Aspect ratio 16:9.
aspect_ratio: '21:9'
summary: >-
  Shows Jaccard distributions on both benchmarks, explaining why boilerplate augmentation failed to break the Jaccard ceiling
figure_path: figures/fig4_v0.jpg
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/filename.jpg}
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure*|figure}[placement], \includegraphics, \caption, \label, \end{...} — pick env + placement by the figure's `aspect_ratio` field (see PLACEMENT below). Constrain every \includegraphics with `width=\linewidth,height=0.4\textheight,keepaspectratio` (single-column) or `width=\textwidth,height=0.45\textheight,keepaspectratio` (figure*). Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place figures where their [FIGURE:fig_id] markers appear in paper_text
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

PLACEMENT BY ASPECT RATIO (use the `aspect_ratio` field on each figure):
- `21:9` (architecture diagrams / hero figures): \begin{figure*}[!t] (full two-column width, top of page). The hero architecture diagram should appear EARLY in the paper — typically at the top of page 2. Marker placement in paper_text already determines this; preserve it.
- `16:9` (comparisons, multi-panel results): \begin{figure*}[!t] for full-width or \begin{figure}[!htbp] for single-column.
- `4:3` / `1:1` / `3:2` / `3:4` / `9:16`: \begin{figure}[!htbp] (single-column).
</figure_requirements>

<artifact_links>
The paper_text contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-semscholar-bib.
TODO 2. Review <paper_text> and <available_figures>. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include every one. Plan placements per section. Build `./references.bib` via aii_semscholar_bib__fetch — collect DOIs/ArXiv IDs from <paper_text> and batch-fetch all BibTeX in one call. Do NOT fabricate entries.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup, write ALL sections, insert ALL figures from <available_figures>, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 6. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `./.terminal_claude_agent_struct_out.json`.
````

### [2] HUMAN-USER prompt · 2026-07-08 11:58:33 UTC

```
Propose a simple, novel, testable ML method for near-duplicate text detection and validate it with a tiny experiment.
```

### [3] SKILL-INPUT — aii-paper-to-latex · 2026-07-08 11:58:39 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: LaTeX paper assembly and compilation. Covers document setup, figure inclusion from pre-generated JPEGs, compilation process, and output files. Use when assembling a paper from pre-written text and pre-generated figures into a compiled PDF.
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figure JPEGs, and bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=0.92\textwidth,keepaspectratio]{figures/filename.jpg}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS use `[!htbp]` float placement (NOT `[t]` or `[h]` alone)
- ALWAYS constrain with `width` and `keepaspectratio` to prevent page takeover
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/*.jpg` — all figure images (pre-generated, copied into workspace)
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-07-08 11:58:43 UTC

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
