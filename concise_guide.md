# concise guide

This short guide explains how modern DNA-based data archiving systems work, referencing canonical research, and connects those findings to the modular prototype in this repository. It focuses on the practical pipeline, why systems use layered codes (inner indel-handling + outer powerful ECC), what mapping choices mean, and which parts of the literature motivated each decision.

---

## Key papers / reading (very short list)
- Church et al., Science (2012) — “Next-generation digital information storage in DNA” — early assembly & address-block approach, demonstrated megabit-scale storage with redundancy/consensus. Fundamental demo of feasibility and practical choices.
- Goldman et al., Nature (2013) — “Towards practical, high-capacity, low-maintenance DNA storage” — encoded compressions, used small addressed blocks and design choices to avoid problematic sequences (GC content, homopolymers).
- Bornholt et al., (2016) — "A DNA-based archival storage system" — end-to-end system architecture (synthesis, pool management, sequencing), early pipeline thinking.
- Erlich & Zielinski, “DNA Fountain” (2017) — high-density fountain-code approach with robust recovery from dropouts; emphasizes efficient outer-layer rateless codes.
- Organick et al., Nature Biotech (2018/2019) — scale-up + random-access demonstrations (lab-scale large pools, index design and retrieval methods).
- Yazdi et al. / VT-code & inner-code papers (various years) — address indel-handling, including Varshamov–Tenengolts (VT) type and later HEDGES-style indel correction.

These works cluster around a few key design patterns: careful mapping to avoid difficult DNA sequences, use of many molecular copies plus consensus to suppress synthesis/sequencing errors, and layered ECCs (inner indel-aware + outer substitution/erasure codes). 

---

## Typical production pipeline (high level)
1. Input splitting and addressing — split data into short payload blocks (oligo-sized) and add per-oligo addresses/indexes so reads can be grouped and ordered.
2. Inner / base-level design — choose mapping + small inner codes to reduce homopolymers, control GC and optionally correct single indels (VT, HEDGES, sync markers, run‑length limited encodings).
3. Outer / block ECC — apply a strong long-block code (Reed–Solomon, fountain codes) across oligos to tolerate dropouts, sequence errors, and missing molecules.
4. Synthesis / pool creation — oligo libraries are synthesized (array or column) and usually amplified by PCR for sequencing.
5. Sequencing (reads collected) — produce many noisy reads per original oligo (multiple copies). Errors include substitutions, deletions and insertions; insertions/deletions (“indels”) cause alignment problems.
6. Grouping & alignment — group reads per unique oligo (addresses/UMIs), run MSA / alignment, produce quality-weighted consensus; inner codes or sync markers aid re-synchronization across indels.
7. Outer decoding — map consensus reads back to byte-level symbols (or RS symbols) and run an outer decoder (e.g., RS or fountain) to recover original data blocks.

This layered approach is exactly what the top papers and practical experiments used: the outer code (fountain/RS) provides erasure/packet-level robustness; the inner layer + alignment handles alignment-sensitive errors (insertions/deletions) which would otherwise wreck block decoders.

---

## Why many groups use RS/fountain over GF(256) (outer) and inner base-level codes (GF(4))
- Byte-aligned RS (GF(256)) is convenient: our raw data is always bytes; GF(256) lets each RS symbol protect a full byte, and many software tools/libraries already support GF(256) arithmetic.
- Mapping bytes → 4 base symbols (2 bits / base) is straightforward: one byte → four GF(4) symbols → four nucleotides. That interoperation between byte‑oriented ECC and quaternary mapping is common in literature (outer RS/fountain + base-level mapping).
- However, indels break alignment at base level. Papers therefore either: (a) add an inner indel-aware code or markers (VT/HEDGES) at the base level or (b) rely on heavy duplicate sampling + consensus/UMAs + MSA before outer decode.

---

## Concrete practice: how it maps to this project
- Inputter: chunk_size chooses message bytes per oligo (this repo’s `FileInputter`). Real systems pick chunk_size so the mapped oligo + ECC + adapters fit typical oligo lengths (e.g., 150–300 nt).
- Encoder options in this repo:
  - Toy GF(4)-parity: educational, directly in quaternary (small inner / demonstration only).
  - RS (GF(256)) encoder/decoder: the prototype outer code in this workspace — treats bytes as GF(256) symbols and is compatible with byte-based pipelines and mapping to GF(4).
- Mapper: the rotating mapper here is a simple deterministic mapping to reduce homopolymers. Real mappers use GC balancing, homopolymer limiting, and reserved sync sequences.
- Channel: IDSChannel + SoupDuplicator simulate substitutions, deletions & multiple reads — this repo provides a small testbed for consensus/alignment logic.
- Aligner: a SimpleAligner is included to demonstrate why grouping + MSA-like consensus matters to fix indels; production systems use clustering/UMIs and quality-weighted MSA.

---

## Practical recommendations coming from the literature
1. Always design for indels — either add an inner code or do grouping + robust MSA. Indels are common in sequencing and fatal for naive symbol decoders.
2. Use an outer robust code for dropouts (fountain/RS). Fountain codes scale well for large pools; RS is easy for block-level erasures and short runs.
3. Reserve short sync markers or addresses per oligo for grouping and re-synchronization, especially when you expect insertions/deletions.
4. Model synthesis & sequencing realistically — simulate PCR bias, overdispersed copy counts (lognormal/negative-binomial), and read coverage variability.
5. Use UMIs or unique addresses so reads can be clustered per original oligo — publications show that robust pairing + clustering drastically improves consensus.

---

## Experiments to try with this repository
1. Try the RS pipeline with `oligo_len` and `overhead` matched to a target platform; increase chunk_size and confirm the helper warns when encoders do not fit.
2. Add a VT-code inner encoder and compare the Levenshtein distance with/without it on noisy IDSChannel outputs.
3. Replace SimpleAligner with a weighted MSA or add UMI-based grouping — compare recovery rates at different deletion probabilities.
4. Replace RS interpolation decoder with full Berlekamp–Massey+Forney to correct symbol errors (not just erasures) — literature shows this increases practical robustness.

---

## Short bibliography / links (for deeper reading)
- Church, G. et al. Next-generation digital information storage in DNA. Science (2012).
- Goldman, N. et al. Towards practical, high-capacity, low-maintenance DNA storage. Nature (2013).
- Bornholt, J. et al. A DNA-based archival storage system (2016).
- Erlich, Y., Zielinski, D. DNA Fountain (2017) — rateless fountain approach for DNA storage.
- Organick, L. et al. Random access in large-scale DNA data storage (2018–2019).
- Yazdi et al. papers on addressing/inner codes and indel handling; HEDGES / VT-code references for indel-aware codes.

---

