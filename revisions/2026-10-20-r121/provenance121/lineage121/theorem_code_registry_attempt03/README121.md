# R121 retained theorem, proof and code index

This is a complete byte and structural scan of the currently retained TeX and Python sources, with immutable R120/R119 custody links. It is not a fresh mathematical revalidation or scientific replay.

## Actual scope

- 260 TeX files; 189 Python files; 4,773,121 source bytes.
- 113 statement environments, 95 proof environments, 66 proof-heading segments, and 853 literal labels.
- 2117 Python definition records; 0 retained syntax-error files. Indexed programs were never imported or executed.
- All 69 historical route-bound TeX files and all 13 historical route-bound Python files are indexed.
- All 132 original source objects are retained: 103 exact direct-tree identities and 29 result archive-member bindings. This census does not reread the 29 raw result members.
- Current wrapper reachability records placement. The explicit correctness corrigendum and superseded original core source retain their individual notes; no truth status is inferred from filenames or inclusion.
- Repeated labels in archived copies, unresolved literal references and nearest-heading associations are structural observations, not TeX build or theorem-validation verdicts.

## Wrapper inclusion closure

| Root | Literal source files | Role |
|---|---:|---|
| ECTA.tex | 11 | current_main |
| supp.tex | 23 | current_supplement |
| appendix.tex | 210 | development_companion |
| RESPONSE_TO_REFEREE.tex | 2 | current_response |

## Directory families

| Family | Files |
|---|---:|
| ECTA.tex | 1 |
| RESPONSE_TO_REFEREE.tex | 1 |
| appendix.tex | 1 |
| build121.py | 1 |
| code119 | 2 |
| code120 | 7 |
| code121 | 11 |
| frozen108 | 143 |
| new | 13 |
| new109 | 4 |
| new110 | 15 |
| new119 | 47 |
| new120 | 12 |
| new121 | 9 |
| preamble.tex | 1 |
| provenance121 | 25 |
| results121 | 2 |
| sections | 69 |
| supp.tex | 1 |
| tables | 75 |
| verification121 | 9 |

## Reproduction

Run the supplied source with a Git metadata checkout containing the immutable baseline trees and the current native revision. The output directory must not exist:

    python provenance121/lineage121/build_theorem_code_registry121.py --repo REPO --revision REVISION --output NEW_DIRECTORY

Only Python standard-library reading, AST parsing and read-only Git metadata commands are used. Lazy object fetch and optional Git locks are disabled. The exact current source bytes are rechecked before successful completion. Different later author sources produce a new dated snapshot rather than rewriting this one.
