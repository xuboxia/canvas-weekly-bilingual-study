# Weekly lecture synthesis

## Teaching-week map

Create a reviewed `metadata/week-map.json` with course/timezone and an explicit `weeks` array. Each week has `week`, `start`, `end`, `evidence` and `lectures`. Each lecture has stable `id`, actual `date`, `title`, slide paths/page ranges, transcript path and `mapping_status`. Use timetable/module evidence, not automatic ISO calendar weeks. Record holidays and unresolved mappings. A two-hour recording is not automatically two lectures. If material crosses weeks, cite the relevant page/transcript ranges in each.

## Coverage before prose

Inventory definitions, assumptions, theorems, derivations, algorithms, diagrams, worked examples, counterexamples, lecturer corrections and substantive spoken additions. Each source unit retains a page/slide/line locator and its eventual section ID. Review every assigned page and complete transcript chunk, including chunks with no additions.

For a long lecture, read contiguous overlapping chunks while maintaining a term/notation map and additions ledger. Deduplicate repetitions without losing corrections or useful examples. Do not let housekeeping crowd out the rest of a recording.

For every lecturer-only addition, retain locally a short evidence excerpt, exact TXT line range or real timestamp, teaching significance and destination section. If wording is uncertain, compare nearby transcript and slides (or audio if available). Label unresolved ambiguity instead of inventing certainty.

## Bilingual depth

Both languages independently explain definition and conditions, intuition, notation/units, steps with reasons, fully worked examples, and useful boundary/failure cases. Select relevant dimensions: an administrative note does not need a proof. Diagrams need bilingual explanations of axes/nodes/direction and conclusions; code needs inputs, outputs, state changes and design reasoning. Preserve runnable identifiers.

Use side-by-side or consecutively paired Chinese/English explanations. Titles, captions, table headers, warnings, glossary entries, practice prompts and worked answers must also be bilingual. Shared formulas/code are language-neutral; the surrounding explanation is not.

“More detailed than slides” means missing reasoning and scaffolding, not a word-count target, translation alone or longer bullets. Label original model teaching expansions. Do not invent professor emphasis or claims about exam scope.

## Weekly artifact and review

Start with learning goals and a list of every lecture, then teach in a sensible order. Put professor additions beside the concept they clarify. Include bilingual worked examples, pitfalls, recap, glossary and reasoned practice answers where useful. Missing sources create visible partial-coverage notices.

Compare the finished guide to the original inventory, not its own table of contents. Check both languages independently, verify attributions and at least one full worked calculation. A schema validator cannot prove that every source concept was inventoried or correctly translated. Only mark complete after semantic review and resolution of substantive coverage gaps.
