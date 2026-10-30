<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img src="./.github/action-stm32-cmake-sample_banner.png" alt="action-stm32-cmake_banner" width="800" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/uoohyo/action-stm32-cmake?logo=github" alt="Latest Release" />
  <img src="https://img.shields.io/github/actions/workflow/status/uoohyo/action-stm32-cmake-sample/sync-test-workflows.yml?branch=main&label=workflow%20sync" alt="Workflow Sync" />
  <img src="https://img.shields.io/badge/STM32CubeCLT%20Versions-13-blue" alt="STM32CubeCLT Versions" />
  <img src="https://img.shields.io/badge/Device-STM32F103C8T6-orange" alt="Target Device" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License" />
</p>
<!-- markdownlint-enable MD033 MD041 -->

This repository provides **comprehensive compatibility testing** for the [uoohyo/action-stm32-cmake](https://github.com/marketplace/actions/build-with-stm32cubeclt-command-line-tools-using-cmake) GitHub Action across all released versions.

<!-- TEST_RESULTS_START -->

## Test Results

Results below refer to the linked completed main-branch run, not a moving branch badge. Missing or legacy configuration evidence is not a passing result.

| Version | Recorded status | Debug / Release | Commit | Run updated (UTC) | Details |
|---|---|---|---|---|---|
| v1.21.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:00Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015160) |
| v1.20.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:47:25Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015095) |
| v1.19.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:43:16Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015063) |
| v1.18.0 | missing | missing / missing | 740f48cb6bba | 2026-10-24T17:48:44Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015125) |
| v1.17.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:04Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015059) |
| v1.16.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:47:00Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015201) |
| v1.15.1 | success | success / success | 740f48cb6bba | 2026-10-24T17:47:47Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015174) |
| v1.15.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:47Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015105) |
| v1.14.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:45:52Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015167) |
| v1.13.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:42Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015151) |
| v1.12.1 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:31Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015072) |
| v1.12.0 | success | success / success | 740f48cb6bba | 2026-10-24T17:48:26Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015114) |
| v1.11.1 | success | success / success | 740f48cb6bba | 2026-10-24T17:47:21Z | [Run](https://github.com/uoohyo/action-stm32-cmake-sample/actions/runs/40117015104) |

<!-- TEST_RESULTS_END -->

## Purpose

Automatically verify that action-stm32-cmake works correctly across various versions of STM32CubeCLT (Command Line Tools). When new STM32CubeCLT versions are released, workflow tests are automatically generated and build tests are performed.

## Key Features

- **Automated Version Discovery**: Automatically detect new STM32CubeCLT versions via GitHub Releases API
- **Single-Project Testing**: One CMake project tests all action versions for consistent validation
- **Comprehensive Testing**: Coverage of 13 STM32CubeCLT versions (v1.11.1 ~ v1.21.0)
- **Continuous Integration**: Automatic build testing for all versions on push to main branch
- **Real-Time Status Dashboard**: Check build status for each version in the table below

## Target Configuration

- **Device**: STM32F103C8T6 (ARM Cortex-M3, 64KB Flash, 20KB RAM)
- **Manufacturer**: STMicroelectronics
- **Output Format**: ELF (Executable and Linkable Format)
- **Build Configurations**: Debug, Release
- **Toolchain**: ARM GNU Toolchain (arm-none-eabi-gcc)
- **Build System**: CMake 3.22+ with Ninja generator

## License

[MIT License](./LICENSE)

Copyright (c) 2024-2026 [uoohyo](https://github.com/uoohyo)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

See [automation validation and support boundaries](docs/automation-validation.md) for result semantics, local tests, and remaining production verification.
