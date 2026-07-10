# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

import nemoguardrails.manifests as manifests_pkg
from nemoguardrails.rails.llm import rail_manifest as shim


def test_shim_reexports_are_identical_to_manifests_package():
    reexported = [
        "ActionRef",
        "Binding",
        "RailManifest",
        "RailManifestRecord",
        "RailCatalog",
        "RailMetadata",
        "RailSpec",
        "RailSurface",
        "parse_configured_surface",
        "resolve_import_ref",
    ]
    for name in reexported:
        assert getattr(shim, name) is getattr(manifests_pkg, name)


def test_shim_discovery_functions_on_empty_catalog():
    shim._reset_rail_manifest_cache()
    shim.discover_rail_manifests()

    assert isinstance(shim.all_rail_manifests(), dict)
    assert isinstance(shim.rail_surfaces(), dict)
    assert shim.configured_rail_surfaces("input", []) == {}

    shim._reset_rail_manifest_cache()


def test_shim_rail_surfaces_rejects_duplicate_registration(monkeypatch):
    action = shim.ActionRef(name="check", target="pathlib:Path.cwd")

    def _manifest(name):
        return shim.RailManifest(
            name=name,
            spec=shim.RailSpec(
                actions=shim.RailActions(refs=(action,)),
                surfaces=(shim.RailSurface(name="shared", direction=shim.RailDirection.INPUT, action=action),),
            ),
        )

    monkeypatch.setattr(shim, "all_rail_manifests", lambda: {"alpha": _manifest("alpha"), "beta": _manifest("beta")})

    with pytest.raises(ValueError, match="already registered"):
        shim.rail_surfaces("input")
