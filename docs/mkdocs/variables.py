"""The variables of the pages, for mkdocs-macros (module_name of the plugin in mkdocs.yml)."""

from __future__ import annotations

import os
from typing import Any


def define_env(env: Any) -> None:
    """Defines the variables that the pages read."""
    # the commit that the site is built from, in CI: the coverage page links it, the reports of that page are of the same commit. It is read
    # from the environment and not with !ENV in mkdocs.yml, which parses it as YAML: a sha of digits alone, or of digits and one "e", would
    # be a number there
    env.variables["commit"] = os.environ.get("GITHUB_SHA", "")
