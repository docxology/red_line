# release — Release editing guidance

This folder owns release assembly: provenance digests, the deterministic release-input snapshot, the hash-addressed release manifest, and two-pass render-determinism comparison. Functions here return data structures; they never print, exit, or parse arguments. The CLIs under `scripts/` are thin wrappers around them.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `sha256_file` | <code>def&nbsp;sha256_file(path:&nbsp;Path)&nbsp;-&gt;&nbsp;str:</code> | Return the SHA-256 digest of one file, read in bounded chunks. | [provenance.py](provenance.py) |
| `git_revision` | <code>def&nbsp;git_revision(path:&nbsp;Path)&nbsp;-&gt;&nbsp;str&nbsp;\|&nbsp;None:</code> | Return the checked-out revision, or `None` when it cannot be read. | [provenance.py](provenance.py) |
| `git_dirty` | <code>def&nbsp;git_dirty(path:&nbsp;Path)&nbsp;-&gt;&nbsp;bool&nbsp;\|&nbsp;None:</code> | Report whether the checkout has uncommitted changes, or `None` when unknown. | [provenance.py](provenance.py) |
| `template_root_candidates` | <code>def&nbsp;template_root_candidates(root:&nbsp;Path)&nbsp;-&gt;&nbsp;tuple[Path,&nbsp;...]:</code> | Ancestor-relative locations searched for a template checkout. | [provenance.py](provenance.py) |
| `find_template_root` | <code>def&nbsp;find_template_root(root:&nbsp;Path)&nbsp;-&gt;&nbsp;Path&nbsp;\|&nbsp;None:</code> | Locate the external render toolchain, or report that there is none. | [provenance.py](provenance.py) |
| `require_template_root` | <code>def&nbsp;require_template_root(root:&nbsp;Path)&nbsp;-&gt;&nbsp;Path:</code> | Return the render toolchain path, or raise `TemplateRootUnavailable` naming what is missing. | [provenance.py](provenance.py) |
| `digest_tree` | <code>def&nbsp;digest_tree(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;root:&nbsp;Path,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;directory:&nbsp;str,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;suffixes:&nbsp;Iterable[str],</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;*,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;exclude_names:&nbsp;Collection[str]&nbsp;=&nbsp;(),</code><br><code>)&nbsp;-&gt;&nbsp;dict[str,&nbsp;str]:</code> | Digest every matching file under one directory, keyed by root-relative path. | [provenance.py](provenance.py) |
| `analysis_metrics` | <code>def&nbsp;analysis_metrics()&nbsp;-&gt;&nbsp;dict[str,&nbsp;object]:</code> | Derive manuscript-facing numeric facts from the live analysis APIs. | [snapshot.py](snapshot.py) |
| `build_snapshot` | <code>def&nbsp;build_snapshot(root:&nbsp;Path)&nbsp;-&gt;&nbsp;dict[str,&nbsp;object]:</code> | Return the source and generated inputs carried into a release tree. | [snapshot.py](snapshot.py) |
| `write_snapshot` | <code>def&nbsp;write_snapshot(root:&nbsp;Path)&nbsp;-&gt;&nbsp;Path:</code> | Write the deterministic release-input snapshot and return its path. | [snapshot.py](snapshot.py) |
| `candidate_ledger` | <code>def&nbsp;candidate_ledger(root:&nbsp;Path)&nbsp;-&gt;&nbsp;dict[str,&nbsp;str]&nbsp;\|&nbsp;None:</code> | Return the candidate ledger path and digest, or `None` when it is absent. | [manifest.py](manifest.py) |
| `candidate_validation` | <code>def&nbsp;candidate_validation(root:&nbsp;Path)&nbsp;-&gt;&nbsp;dict:</code> | Report whether the candidate red-line ledger is present and digestible. | [manifest.py](manifest.py) |
| `template_validation` | <code>def&nbsp;template_validation(path:&nbsp;Path)&nbsp;-&gt;&nbsp;dict:</code> | Interpret the template output-validation report as a pass or fail result. | [manifest.py](manifest.py) |
| `render_validation` | <code>def&nbsp;render_validation(path:&nbsp;Path)&nbsp;-&gt;&nbsp;dict:</code> | Interpret the render-determinism report as a pass or fail result. | [manifest.py](manifest.py) |
| `undecided_before_render` | <code>def&nbsp;undecided_before_render(manifest:&nbsp;dict)&nbsp;-&gt;&nbsp;list[str]:</code> | Name the validations a render must run before they can be judged. | [manifest.py](manifest.py) |
| `decidable_failures` | <code>def&nbsp;decidable_failures(manifest:&nbsp;dict)&nbsp;-&gt;&nbsp;list[str]:</code> | Name the validations that failed for a reason no render would change. | [manifest.py](manifest.py) |
| `release_ready` | <code>def&nbsp;release_ready(manifest:&nbsp;dict,&nbsp;*,&nbsp;strict:&nbsp;bool&nbsp;=&nbsp;False)&nbsp;-&gt;&nbsp;bool:</code> | Report whether manifest validation results satisfy the publication gate. | [manifest.py](manifest.py) |
| `build_manifest` | <code>def&nbsp;build_manifest(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;root:&nbsp;Path,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;*,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;\|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;render_timestamp:&nbsp;str&nbsp;\|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;dict:</code> | Assemble source, artifact, and validation bindings into one manifest. | [manifest.py](manifest.py) |
| `artifact_hashes` | <code>def&nbsp;artifact_hashes(root:&nbsp;Path)&nbsp;-&gt;&nbsp;dict[str,&nbsp;str]:</code> | Digest every comparable rendered artifact under the output tree. | [determinism.py](determinism.py) |
| `pdf_text` | <code>def&nbsp;pdf_text(path:&nbsp;Path)&nbsp;-&gt;&nbsp;str&nbsp;\|&nbsp;None:</code> | Extract laid-out PDF text, or `None` when extraction is unavailable. | [determinism.py](determinism.py) |
| `pdf_texts_equal` | <code>def&nbsp;pdf_texts_equal(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;first:&nbsp;dict[str,&nbsp;str&nbsp;\|&nbsp;None],</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;second:&nbsp;dict[str,&nbsp;str&nbsp;\|&nbsp;None],</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;pdf_paths:&nbsp;list[str],</code><br><code>)&nbsp;-&gt;&nbsp;bool:</code> | Report whether both passes extracted identical text for every expected PDF. | [determinism.py](determinism.py) |
| `classify_nondeterminism` | <code>def&nbsp;classify_nondeterminism(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;*,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;byte_identical:&nbsp;bool,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;non_pdf_equal:&nbsp;bool,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;pdf_text_equal:&nbsp;bool,</code><br><code>)&nbsp;-&gt;&nbsp;list[str]:</code> | Name the artifact drift observed between two passes, if any. | [determinism.py](determinism.py) |
| `template_render_passes` | <code>def&nbsp;template_render_passes(root:&nbsp;Path)&nbsp;-&gt;&nbsp;Callable[[],&nbsp;None]:</code> | Build the callable that runs one canonical render pass in the sibling template. | [determinism.py](determinism.py) |
| `compare_artifacts` | <code>def&nbsp;compare_artifacts(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;root:&nbsp;Path,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;*,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;render:&nbsp;Callable[[],&nbsp;None]&nbsp;\|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;dict:</code> | Compare two artifact passes for content-identical render output. | [determinism.py](determinism.py) |

## Import direction

May import stdlib, the root package, `analysis/`, `canary/`, and `contracts/`. Must not import `figures/` or `scripts/`. Nothing in the older policy packages may import `release/`.

## Invariants

- No module-level path bootstrapping and no module-level `ROOT`; every entry point takes `root: Path` explicitly so temporary trees are first-class.
- Rendering is injected, not assumed. `compare_artifacts` renders only when a callable is supplied, which keeps the comparison testable without the sibling template checkout.
- Digest keys stay root-relative and suffix matching stays case-insensitive; changing either silently invalidates every recorded manifest.
- `release_ready` fails closed: an empty `validation_results` map is never ready.
- Report interpretation fails closed. A missing, unreadable, or summary-less report is a failure, never a skip.
- Manifest and snapshot JSON shapes are recorded evidence. Adding a key is a schema change; renaming or removing one breaks published manifests.

## Tests

Tests for this folder live in:
- [../../../tests/release/test_provenance.py](../../../tests/release/test_provenance.py)
- [../../../tests/release/test_snapshot.py](../../../tests/release/test_snapshot.py)
- [../../../tests/release/test_manifest.py](../../../tests/release/test_manifest.py)
- [../../../tests/release/test_determinism.py](../../../tests/release/test_determinism.py)
- [../../../tests/integration/test_release_bindings.py](../../../tests/integration/test_release_bindings.py)
