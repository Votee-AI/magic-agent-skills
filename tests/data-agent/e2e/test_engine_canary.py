"""
Engine canary — keep CI honest about DataDesigner verification (H3 / gap G2).
============================================================================
The adversarial review found that CI could go green while verifying none of the
DataDesigner engine integration: the integration/fidelity tests `importorskip`
`data_designer`, so on any runner where the engine is absent they vanish silently
and "all green" means nothing more than a markdown linter passed.

This module deliberately has NO module-level `importorskip` so the canary runs
even when the engine is missing. On a runner that is SUPPOSED to have the engine
(CI sets `MAGIC_REQUIRE_ENGINE=1`), a missing engine is a hard FAILURE, not a
skip — so engine coverage can never silently disappear.

Locally (flag unset) it skips when the engine isn't installed, so it stays out of
the way of contributors who don't work on magic-data-synthesis.
"""
import importlib.util
import os

import pytest

_ENGINE_PRESENT = importlib.util.find_spec("data_designer") is not None
_ENGINE_REQUIRED = os.environ.get("MAGIC_REQUIRE_ENGINE") == "1"


def test_dd_installed():
    """FAIL (not skip) when the engine is required but absent; otherwise verify/skip."""
    if _ENGINE_REQUIRED:
        assert _ENGINE_PRESENT, (
            "MAGIC_REQUIRE_ENGINE=1 but `data_designer` is not importable — the engine "
            "integration layer is UNVERIFIED on this runner. Install requirements.txt "
            "(data-designer==0.6.0), or unset MAGIC_REQUIRE_ENGINE if this runner is not "
            "meant to exercise the engine. A silent green here is exactly the gap this "
            "canary exists to prevent."
        )
    elif not _ENGINE_PRESENT:
        pytest.skip("data-designer not installed and MAGIC_REQUIRE_ENGINE != 1")


@pytest.mark.skipif(not _ENGINE_PRESENT, reason="data-designer not installed")
def test_dd_version_is_the_pinned_engine():
    """When present, the engine should be the pinned version the docs/tests verified against.

    A version drift is a warning sign that the verified API surface (processors,
    SchemaTransformProcessorConfig, judge-column shape) may have moved — surface it
    rather than letting tests pass against an unverified engine build.
    """
    from importlib.metadata import PackageNotFoundError, version

    try:
        installed = version("data-designer")
    except PackageNotFoundError:
        installed = None
    # Flag a mismatch loudly when the engine is required (CI), where reproducibility matters.
    if _ENGINE_REQUIRED:
        assert installed == "0.6.0", (
            f"data-designer is {installed!r}, not the pinned 0.6.0 the integration was verified "
            "against — re-verify the DD API surface (processors, judge-column shape) and bump "
            "the pin + tests deliberately."
        )
