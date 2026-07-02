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

"""Rail manifest API exposed under the `rails.llm` namespace.

Re-exports the manifest types and catalog from `nemoguardrails.manifests` and
adds the discovery and cache entry points used by the LLM rails pipeline
(`discover_rail_manifests`, `all_rail_manifests`,
`rail_surfaces`, `configured_rail_surfaces`).
"""

import nemoguardrails.manifests as _manifests
from nemoguardrails.manifests.manifest import configured_rail_surfaces as _configured_rail_surfaces

ActionRef = _manifests.ActionRef
Binding = _manifests.Binding
ConfigSpecRef = _manifests.ConfigSpecRef
EnvVar = _manifests.EnvVar
ExampleRef = _manifests.ExampleRef
ImportRef = _manifests.ImportRef
ModelRequirement = _manifests.ModelRequirement
RailActions = _manifests.RailActions
RailCapability = _manifests.RailCapability
RailCatalog = _manifests.RailCatalog
RailCategory = _manifests.RailCategory
RailConfigSchema = _manifests.RailConfigSchema
RailDirection = _manifests.RailDirection
RailFlows = _manifests.RailFlows
RailLifecycle = _manifests.RailLifecycle
RailManifest = _manifests.RailManifest
RailManifestRecord = _manifests.RailManifestRecord
RailMetadata = _manifests.RailMetadata
RailPrivacy = _manifests.RailPrivacy
RailRequirements = _manifests.RailRequirements
RailSpec = _manifests.RailSpec
RailStatus = _manifests.RailStatus
RailSurface = _manifests.RailSurface
ServiceRequirement = _manifests.ServiceRequirement
TransformTarget = _manifests.TransformTarget
default_rail_catalog = _manifests.default_rail_catalog
import_ref_target = _manifests.import_ref_target
iter_manifest_import_refs = _manifests.iter_manifest_import_refs
iter_manifest_import_targets = _manifests.iter_manifest_import_targets
normalize_configured_surface_name = _manifests.normalize_configured_surface_name
parse_configured_surface = _manifests.parse_configured_surface
rail_catalog = _manifests.rail_catalog
resolve_import_ref = _manifests.resolve_import_ref
selected_rail_surfaces = _manifests.selected_rail_surfaces
surface_names = _manifests.surface_names


__all__ = [
    "ActionRef",
    "Binding",
    "ConfigSpecRef",
    "EnvVar",
    "ExampleRef",
    "ImportRef",
    "ModelRequirement",
    "RailActions",
    "RailCapability",
    "RailCatalog",
    "RailCategory",
    "RailConfigSchema",
    "RailDirection",
    "RailFlows",
    "RailLifecycle",
    "RailManifest",
    "RailManifestRecord",
    "RailMetadata",
    "RailPrivacy",
    "RailRequirements",
    "RailSpec",
    "RailStatus",
    "RailSurface",
    "ServiceRequirement",
    "TransformTarget",
    "all_rail_manifests",
    "configured_rail_surfaces",
    "default_rail_catalog",
    "discover_rail_manifests",
    "import_ref_target",
    "iter_manifest_import_refs",
    "iter_manifest_import_targets",
    "normalize_configured_surface_name",
    "parse_configured_surface",
    "rail_catalog",
    "rail_surfaces",
    "resolve_import_ref",
    "selected_rail_surfaces",
    "surface_names",
]


_manifest_discovered = False
_manifest_discovering = False


def discover_rail_manifests() -> None:
    global _manifest_discovered
    if _manifest_discovering:
        raise RuntimeError("Built-in rail manifest discovery re-entered while loading rail modules.")
    _manifests.default_rail_catalog()
    _manifest_discovered = True


def all_rail_manifests():
    discover_rail_manifests()
    return _manifests.all_rail_manifests()


def rail_surfaces(direction=None):
    discover_rail_manifests()
    parsed_direction = RailDirection(direction) if direction is not None else None
    surfaces = {}
    owners = {}
    for manifest in all_rail_manifests().values():
        for surface in manifest.surfaces:
            if parsed_direction is not None and surface.direction != parsed_direction:
                continue
            key = (surface.direction, surface.name)
            if key in surfaces:
                raise ValueError(
                    f"Rail surface {surface.name!r} for direction {surface.direction.value!r} is already "
                    f"registered by rail {owners[key]!r}; cannot register it from rail {manifest.name!r}."
                )
            surfaces[key] = surface
            owners[key] = manifest.name
    return surfaces


def configured_rail_surfaces(direction, flows):
    parsed_direction = RailDirection(direction)
    return _configured_rail_surfaces(parsed_direction, flows, rail_surfaces(parsed_direction))


def _reset_rail_manifest_cache() -> None:
    global _manifest_discovered, _manifest_discovering
    _manifests._reset_rail_manifest_cache()
    _manifest_discovered = False
    _manifest_discovering = False
