# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import shutil
from typing import Tuple

from swell.utilities.logger import Logger
from jedi_bundle.utils.yaml import load_yaml
from jedi_bundle.config.config import check_platform
from jedi_bundle.bin.jedi_bundle import get_default_config

from swell.utilities.pinned_versions.check_hashes import get_pinned_vers_path

# --------------------------------------------------------------------------------------------------


def build_and_source_dirs(package_path: str) -> Tuple[str, str]:

    # Make package directory
    # ----------------------
    os.makedirs(package_path, 0o755, exist_ok=True)

    package_build_path = os.path.join(package_path, 'build')
    package_source_path = os.path.join(package_path, 'source')

    # Remove trailing slash if needed
    package_build_path = package_build_path.rstrip('/')
    package_source_path = package_source_path.rstrip('/')

    return package_build_path, package_source_path


# --------------------------------------------------------------------------------------------------


def link_path(source: str, target: str) -> None:

    # Remove existing source path if present
    if os.path.islink(target):  # Is a link
        os.remove(target)
    elif os.path.isdir(target):  # Is a directory
        shutil.rmtree(target)

    # Link existing source into the directory
    os.symlink(source, target)


# --------------------------------------------------------------------------------------------------


def set_jedi_bundle_config(
    bundles: list,
    path_to_source: str,
    path_to_build: str,
    platform: str,
    use_pinned: bool,
    cores_to_use_for_make: int = 6
) -> dict:

    # Start from the default jedi_bundle config file
    jedi_bundle_config = get_default_config()

    # Always build certain JEDI packages
    bundles.append('iodaconv')

    # Set the clone stage options
    jedi_bundle_config['clone_options']['bundles'] = bundles
    jedi_bundle_config['clone_options']['path_to_source'] = path_to_source

    # Add GSIbec as extra repo
    if 'fv3-jedi' in bundles:
        jedi_bundle_config['clone_options']['extra_repos'] = ['gsibec']

    # Set the configure stage options
    jedi_bundle_config['configure_options']['path_to_build'] = path_to_build

    # Set the make stage options
    jedi_bundle_config['make_options']['cores_to_use_for_make'] = cores_to_use_for_make

    # Check is swell platform is a jedi_bundle platform and if so use it
    if check_platform(platform):
        jedi_bundle_config['configure_options']['platform'] = platform

    # Always use the swell defined modules to build
    jedi_bundle_config['configure_options']['external_modules'] = True

    # Add pinned_versions to jedi_bundle_config if applicable
    if use_pinned:
        logger = Logger("LoadPinnedVersions")
        pinned_config_file = get_pinned_vers_path()
        pinned_versions_dict = load_yaml(logger, pinned_config_file)
        jedi_bundle_config['pinned_versions'] = pinned_versions_dict

    # Return the dictionary object
    return jedi_bundle_config


# --------------------------------------------------------------------------------------------------
