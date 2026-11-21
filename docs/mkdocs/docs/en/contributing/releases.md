---
title: Releases
---
# Releases

A release is built from a commit of `main` that CI built and tested: its wheels and its coverage are the ones of that run of CI,
and only the deb packages are built again, for every release of Debian and Ubuntu.

## Making a release

1. **The version.** It is written in one place, `version` in `pyproject.toml`: `CMakeLists.txt`, `debian/set-version.sh` and the
   release workflow read it from there. The commit that changes it is `version: bump to vX.Y.Z`, merged to `main`.
2. **CI.** The run of CI of that commit on `main` has to succeed, every build and every test.
3. **The tag.** A tag `vX.Y.Z` on that commit, pushed:
    ```bash
    git tag vX.Y.Z <commit>
    git push origin vX.Y.Z
    ```
4. **The workflow.** `release.yml` runs on the tag:
    - checks that the tag is the version of `pyproject.toml`, and finds the successful run of CI on `main` of its commit; it stops
      when there is none;
    - builds the deb packages of every release and architecture;
    - packs the source with its submodules, `monero-python-X.Y.Z.tar.gz` (the archives of GitHub have none of them);
    - takes the wheels of macOS and Windows and the coverage report from the run of CI;
    - lists the sums of the files in `SHA256SUMS`, and attests that the workflow built them;
    - makes a **draft** release with the files, the notes below and the changes since the last release.
5. **Publishing.** A maintainer reads the draft, and publishes it.

## The notes of a release

Every release has these notes (`.github/release-notes.md`):

--8<-- ".github/release-notes.md"
