## ccache in CI

The workflows keep a ccache directory (`.ccache` in the workspace) between runs so monero-project doesn't get rebuilt from scratch every time. This is what to expect from it and where it stops helping.

### How it's wired

- monero-project already uses ccache on its own (`USE_CCACHE`, `FindCcache`). Nothing is passed to it. Don't set `CMAKE_CXX_COMPILER_LAUNCHER` in the environment for that step, it would be wrapped twice.
- monero-cpp is a submodule and doesn't know about ccache. The workflows and `docker/build.sh` pass `-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache` when configuring it.
- monero-python picks ccache up itself if it finds it. `-DUSE_CCACHE=OFF` turns that off. A launcher passed on the command line or in the environment wins.
- `CCACHE_DIR` is `.ccache`, `CCACHE_MAXSIZE` is 500M per job.

### Where the cache lives

- Key is `ccache-<name>_<sha>`, restore falls back to the newest `ccache-<name>_`. The `_` is there because `macos-15` is a prefix of `macos-15-intel`.
- macOS and Windows share a cache between `test.yml` and the `build-*.yml` workflows, the compile commands are the same. Linux tests have their own, the deb builds have one per distro and arch.
- Pull requests only restore. Pushes to main and manual runs (`workflow_dispatch`) save. This is on purpose, see quota below.
- A cache saved on a branch is only visible to that branch. Main's caches are visible to everyone. So the first run on main after merging this is cold.
- The save step runs after the build and before the tests, so a flaky test doesn't throw the cache away. Failed builds save too, whatever got compiled is still good.

### What isn't cached

- Coverage. `ENABLE_COVERAGE` adds `-fprofile-update=atomic`, and ccache 4.9.1 (what Ubuntu 24.04 ships) doesn't support that option. Those compiles go straight to the compiler, they don't fail. In the Linux test job that's the 12 monero-cpp files and the 7 binding files. monero-project is built without coverage and is cached normally. Newer ccache might handle it, not checked.
- Don't drop the flag to get hits. The tests are multithreaded and non-atomic counters give garbage coverage. `--coverage` alone is fine with ccache, a hit restores the `.gcno` and lcov reads it as usual.

### Per platform

- macOS: `CCACHE_COMPILERCHECK` is `%compiler% -v`. The default hashes mtime and size of `/usr/bin/c++`, which is a shim and stays the same when Xcode updates, so you'd keep getting objects from an old clang. Costs one extra process per compile.
- Windows: ccache comes from the rolling MSYS2 repo through `setup-msys2`, the toolchain is pinned afterwards with `pacman -U`. If ccache stops starting after you touch the pins, look there first. If it keeps being a problem, remove the ccache steps from the two Windows jobs, nothing else depends on them.
- deb: `.ccache` sits in the workspace that is mounted into the container, `CCACHE_DIR` is passed to `docker run`. Files end up owned by root on the host, the cache action only reads them. The runner has no ccache, so the stats are printed by `docker/build.sh`. Builds under qemu (arm64, armhf) are the slow ones and gain the most.

### Quota

GitHub gives 10 GB per repo, least recently used goes first, and anything not touched for 7 days is dropped. The deb matrix alone is 12 caches and the buildx layer cache (`type=gha`) shares the same quota. 500M is a guess. Look at the numbers once there are a few runs and adjust.

### Checking it works

Run `test.yml` twice on the same branch with `workflow_dispatch`. Second run should show mostly hits in the "Show ccache statistics" step (for deb it's the end of the `build.sh` output). Stats are zeroed at the start of each job, so they're only for that run.

To start over: `gh cache list`, then `gh cache delete <id>`.
