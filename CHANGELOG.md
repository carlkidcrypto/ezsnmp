Last Updated: 2026-01-19 02:36:00 UTC

# Changelog


<a name="v2.2.0a0"></a>
## [v2.2.0a0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0...v2.2.0a0) (2026-01-18)


### Changes

#### Bug Fixes

- Fix MacPorts cache corruption, missing LD_LIBRARY_PATH, cibuildwheel dependency, and Sphinx Python version issues in CI workflows ([#621](https://github.com/carlkidcrypto/ezsnmp/issues/621))

- Fix duplicate step IDs in tests_homebrew.yml workflow ([#620](https://github.com/carlkidcrypto/ezsnmp/issues/620))


#### Code Refactoring

- Refactor: Extract docker exec logic into separate script ([#586](https://github.com/carlkidcrypto/ezsnmp/issues/586))


#### Dependency Updates

- Bump peter-evans/create-pull-request from 7.0.8 to 8.0.0 ([#560](https://github.com/carlkidcrypto/ezsnmp/issues/560))

- Bump actions/upload-artifact from 5.0.0 to 6.0.0 ([#567](https://github.com/carlkidcrypto/ezsnmp/issues/567))

- Bump urllib3 from 2.6.0 to 2.6.2 ([#563](https://github.com/carlkidcrypto/ezsnmp/issues/563))

- Bump tj-actions/changed-files from 47.0.0 to 47.0.1 ([#564](https://github.com/carlkidcrypto/ezsnmp/issues/564))

- Bump psf/black from 25.9.0 to 25.12.0 ([#550](https://github.com/carlkidcrypto/ezsnmp/issues/550))

- Bump black from 25.9.0 to 25.12.0 ([#555](https://github.com/carlkidcrypto/ezsnmp/issues/555))

- Bump actions/checkout from 5.0.0 to 6.0.1 ([#556](https://github.com/carlkidcrypto/ezsnmp/issues/556))

- Bump actions/download-artifact from 6.0.0 to 7.0.0 ([#568](https://github.com/carlkidcrypto/ezsnmp/issues/568))

- Bump actions/cache from 4.3.0 to 5.0.1 ([#569](https://github.com/carlkidcrypto/ezsnmp/issues/569))

- Bump github/codeql-action from 4.31.3 to 4.31.8 ([#566](https://github.com/carlkidcrypto/ezsnmp/issues/566))


#### Features

- Feature/docker builds py14 2 ([#629](https://github.com/carlkidcrypto/ezsnmp/issues/629))

- Feature/docker builds py14 ([#608](https://github.com/carlkidcrypto/ezsnmp/issues/608))

- Feature 2.2.0 ([#597](https://github.com/carlkidcrypto/ezsnmp/issues/597))


#### Features

- Add CodeCov integration for Python and C++ coverage reporting ([#618](https://github.com/carlkidcrypto/ezsnmp/issues/618))

- Add Python 3.14 and drop Python 3.9 from CentOS 7 Docker image ([#600](https://github.com/carlkidcrypto/ezsnmp/issues/600))


#### Maintenance

- chore: bump pytest from 8.4.2 to 9.0.2 ([#575](https://github.com/carlkidcrypto/ezsnmp/issues/575))

- chore: bump furo from 2025.9.25 to 2025.12.19 ([#577](https://github.com/carlkidcrypto/ezsnmp/issues/577))

- chore: bump coverage from 7.10.7 to 7.13.1 ([#588](https://github.com/carlkidcrypto/ezsnmp/issues/588))

- chore: bump swig from 4.3.1 to 4.4.1 ([#589](https://github.com/carlkidcrypto/ezsnmp/issues/589))

- chore: bump sphinx from 8.2.3 to 9.1.0 ([#596](https://github.com/carlkidcrypto/ezsnmp/issues/596))

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md


#### Merged Pull Requests

- Merge branch 'main' into update-changelog-20622364436


#### Remove

- Remove redundant manual coverage flags when b_coverage=true is set ([#580](https://github.com/carlkidcrypto/ezsnmp/issues/580))


#### Sync

- Sync Docker images with documentation: drop Python 3.9, add Python 3.14 ([#599](https://github.com/carlkidcrypto/ezsnmp/issues/599))


#### Updates & Improvements

- Update Docker images to support Python 3.10-3.14 ([#601](https://github.com/carlkidcrypto/ezsnmp/issues/601))

- Update docs for v2.2.0a0 and Python 3.10+ support ([#603](https://github.com/carlkidcrypto/ezsnmp/issues/603))







### Merged Pull Requests

- Merge pull request [#595](https://github.com/carlkidcrypto/ezsnmp/issues/595) from carlkidcrypto/update-changelog-20622364436

- Merge pull request [#594](https://github.com/carlkidcrypto/ezsnmp/issues/594) from carlkidcrypto/update-changelog-20622364424





---

<a name="v2.1.0"></a>
## [v2.1.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0b2...v2.1.0) (2025-12-30)


### Changes

#### Bug Fixes

- Fix typo: "compatiblewith" → "compatible with" in agent configs ([#582](https://github.com/carlkidcrypto/ezsnmp/issues/582))

- Fix sphinx_build workflow tag resolution on workflow_dispatch ([#544](https://github.com/carlkidcrypto/ezsnmp/issues/544))

- Fix sphinx_build workflow failing to find tags on workflow_dispatch ([#543](https://github.com/carlkidcrypto/ezsnmp/issues/543))

- Fix Sphinx docs workflow: replace deprecated upload-release-asset action and add manual trigger ([#536](https://github.com/carlkidcrypto/ezsnmp/issues/536))


#### Dependency Updates

- Bump Version ([#592](https://github.com/carlkidcrypto/ezsnmp/issues/592))


#### Enhancements

- Enhance auto changelog workflow with caching and intelligent change detection ([#537](https://github.com/carlkidcrypto/ezsnmp/issues/537))


#### Features

- Feature/fix cpp tests post merge from feature branch ([#587](https://github.com/carlkidcrypto/ezsnmp/issues/587))

- Feature/100 percent working docker builds v2 ([#576](https://github.com/carlkidcrypto/ezsnmp/issues/576))

- Feature: Update Docker Containers To Run More Python Tests ([#572](https://github.com/carlkidcrypto/ezsnmp/issues/572))


#### Maintenance

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md

- chore: update CHANGELOG.md


#### Merged Pull Requests

- Merge branch 'main' into update-changelog-20182435898

- Merge branch 'main' into update-changelog-20016166965

- Merge branch 'main' into update-changelog-20016100231

- Merge branch 'main' into update-changelog-20012006173

- Merge branch 'main' into update-changelog-20011809866


#### Updates & Improvements

- Update Sphinx build workflow to run apt update ([#593](https://github.com/carlkidcrypto/ezsnmp/issues/593))







### Merged Pull Requests

- Merge pull request [#570](https://github.com/carlkidcrypto/ezsnmp/issues/570) from carlkidcrypto/update-changelog-20182435898

- Merge pull request [#565](https://github.com/carlkidcrypto/ezsnmp/issues/565) from carlkidcrypto/update-changelog-20150388748

- Merge pull request [#542](https://github.com/carlkidcrypto/ezsnmp/issues/542) from carlkidcrypto/update-changelog-20016166965

- Merge pull request [#539](https://github.com/carlkidcrypto/ezsnmp/issues/539) from carlkidcrypto/update-changelog-20016100231

- Merge pull request [#538](https://github.com/carlkidcrypto/ezsnmp/issues/538) from carlkidcrypto/update-changelog-20012006173

- Merge pull request [#535](https://github.com/carlkidcrypto/ezsnmp/issues/535) from carlkidcrypto/update-changelog-20011809866





---

<a name="v2.1.0b2"></a>
## [v2.1.0b2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0b1...v2.1.0b2) (2025-12-06)


### Changes

#### Bug Fixes

- Fix issue [#355](https://github.com/carlkidcrypto/ezsnmp/issues/355): Strip surrounding quotes from SNMP string values ([#492](https://github.com/carlkidcrypto/ezsnmp/issues/492))


#### Dependency Updates

- Bump pytest from 8.4.2 to 9.0.1 ([#500](https://github.com/carlkidcrypto/ezsnmp/issues/500))


#### Features

- Feature/fix cpp tests ([#527](https://github.com/carlkidcrypto/ezsnmp/issues/527))

- Feature/get uts to run in gh runners 3 ([#510](https://github.com/carlkidcrypto/ezsnmp/issues/510))

- Feature/get uts to run in gh runners 2 ([#505](https://github.com/carlkidcrypto/ezsnmp/issues/505))

- Feature/get uts to run in gh runners ([#504](https://github.com/carlkidcrypto/ezsnmp/issues/504))


#### Maintenance

- chore: update CHANGELOG.md







### Merged Pull Requests

- Merge pull request [#502](https://github.com/carlkidcrypto/ezsnmp/issues/502) from carlkidcrypto/update-changelog-19353407644





---

<a name="v2.1.0b1"></a>
## [v2.1.0b1](https://github.com/carlkidcrypto/ezsnmp/compare/2.1.0b0...v2.1.0b1) (2025-11-12)


### Changes

#### 461

- 461 feature   add support for   exit    enter    del   ([#468](https://github.com/carlkidcrypto/ezsnmp/issues/468))


#### Code Improvements

- Modernize Docker infrastructure: Python 3.9-3.13, g++ 11+, optimized images ([#483](https://github.com/carlkidcrypto/ezsnmp/issues/483))


#### Code Refactoring

- Refactor setup.py: Extract Homebrew detection into reusable functions and parallelize SWIG build ([#485](https://github.com/carlkidcrypto/ezsnmp/issues/485))


#### Dependency Updates

- Bump actions/upload-artifact from 4 to 5 ([#476](https://github.com/carlkidcrypto/ezsnmp/issues/476))

- Bump actions/download-artifact from 5 to 6 ([#475](https://github.com/carlkidcrypto/ezsnmp/issues/475))

- Bump carlkidcrypto/os-specific-runner from 2.1.2 to 2.1.3 ([#474](https://github.com/carlkidcrypto/ezsnmp/issues/474))

- Bump tomli from 2.2.1 to 2.3.0 ([#465](https://github.com/carlkidcrypto/ezsnmp/issues/465))

- Bump github/codeql-action from 3 to 4 ([#462](https://github.com/carlkidcrypto/ezsnmp/issues/462))

- Bump platformdirs from 4.4.0 to 4.5.0 ([#464](https://github.com/carlkidcrypto/ezsnmp/issues/464))

- Bump peter-evans/create-or-update-comment from 4 to 5 ([#454](https://github.com/carlkidcrypto/ezsnmp/issues/454))

- Bump peter-evans/commit-comment from 3 to 4 ([#453](https://github.com/carlkidcrypto/ezsnmp/issues/453))

- Bump tox from 4.30.2 to 4.30.3 ([#455](https://github.com/carlkidcrypto/ezsnmp/issues/455))

- Bump furo from 2025.7.19 to 2025.9.25 ([#451](https://github.com/carlkidcrypto/ezsnmp/issues/451))

- Bump tj-actions/changed-files from 46.0.5 to 47.0.0 ([#439](https://github.com/carlkidcrypto/ezsnmp/issues/439))


#### Documentation Updates

- Document project structure and add missing README files ([#481](https://github.com/carlkidcrypto/ezsnmp/issues/481))


#### Features

- Feature/fix docker test scripts ([#491](https://github.com/carlkidcrypto/ezsnmp/issues/491))

- Feature/add agents ([#489](https://github.com/carlkidcrypto/ezsnmp/issues/489))

- Feature/add agents ([#484](https://github.com/carlkidcrypto/ezsnmp/issues/484))

- Feature/documentation agent ([#482](https://github.com/carlkidcrypto/ezsnmp/issues/482))

- Feature/prep for 2.1.0b1 2 ([#479](https://github.com/carlkidcrypto/ezsnmp/issues/479))


#### Features

- feat: Add logging and dict/json support for Session and Result objects ([#470](https://github.com/carlkidcrypto/ezsnmp/issues/470))


#### Features

- Add comprehensive unit test coverage for cpp_tests error paths and exceptions ([#487](https://github.com/carlkidcrypto/ezsnmp/issues/487))

- Add The Scribe agent documentation guidelines ([#480](https://github.com/carlkidcrypto/ezsnmp/issues/480))


#### Maintenance

- chore: update CHANGELOG.md ([#463](https://github.com/carlkidcrypto/ezsnmp/issues/463))


#### Performance Improvements

- Increase python_tests coverage from 80% to 88% ([#488](https://github.com/carlkidcrypto/ezsnmp/issues/488))


#### Python-related Changes

- Python Tests: Docker ([#498](https://github.com/carlkidcrypto/ezsnmp/issues/498))


#### Release

- Release/prep for 2.1.0b1 ([#472](https://github.com/carlkidcrypto/ezsnmp/issues/472))


#### Updates & Improvements

- Update docs for v2.1.0b1 and refresh styles ([#501](https://github.com/carlkidcrypto/ezsnmp/issues/501))










---

<a name="2.1.0b0"></a>
## [2.1.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0a3...2.1.0b0) (2025-10-06)


### Changes

#### 442

- 442 question session close ([#456](https://github.com/carlkidcrypto/ezsnmp/issues/456))


#### Dependency Updates

- Bump psf/black from 25.1.0 to 25.9.0 ([#444](https://github.com/carlkidcrypto/ezsnmp/issues/444))

- Bump black from 25.1.0 to 25.9.0 ([#445](https://github.com/carlkidcrypto/ezsnmp/issues/445))

- Bump coverage from 7.10.6 to 7.10.7 ([#446](https://github.com/carlkidcrypto/ezsnmp/issues/446))

- Bump pyparsing from 3.2.3 to 3.2.5 ([#447](https://github.com/carlkidcrypto/ezsnmp/issues/447))

- Bump pytest-cov from 6.2.1 to 7.0.0 ([#438](https://github.com/carlkidcrypto/ezsnmp/issues/438))


#### Maintenance

- chore: update CHANGELOG.md







### Merged Pull Requests

- Merge pull request [#450](https://github.com/carlkidcrypto/ezsnmp/issues/450) from carlkidcrypto/update-changelog-17964730341





---

<a name="v2.1.0a3"></a>
## [v2.1.0a3](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0a2...v2.1.0a3) (2025-09-23)


### Changes

#### 384

- 384 bug   macos native tests ([#441](https://github.com/carlkidcrypto/ezsnmp/issues/441))


#### 422

- 422 feature per bulk walk configurable max repetitions ([#443](https://github.com/carlkidcrypto/ezsnmp/issues/443))


#### Critical Bug Fixes

- Hotfix/fix test pypi and pypi ([#449](https://github.com/carlkidcrypto/ezsnmp/issues/449))


#### Dependency Updates

- Bump platformdirs from 4.3.8 to 4.4.0 ([#425](https://github.com/carlkidcrypto/ezsnmp/issues/425))

- Bump actions/setup-python from 5 to 6 ([#430](https://github.com/carlkidcrypto/ezsnmp/issues/430))


#### Maintenance

- chore: update CHANGELOG.md







### Merged Pull Requests

- Merge pull request [#436](https://github.com/carlkidcrypto/ezsnmp/issues/436) from carlkidcrypto/update-changelog-17495929398





---

<a name="v2.1.0a2"></a>
## [v2.1.0a2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0a1...v2.1.0a2) (2025-09-04)


### Changes

#### 401

- 401 feature   add convertvalue to datatypes ([#414](https://github.com/carlkidcrypto/ezsnmp/issues/414))


#### 406

- 406 malloc consolidate invalid chunk size in net snmp less than 59 ([#426](https://github.com/carlkidcrypto/ezsnmp/issues/426))


#### AlmaLinux10

- AlmaLinux10 Docker ([#435](https://github.com/carlkidcrypto/ezsnmp/issues/435))


#### Dependency Updates

- Bump coverage from 7.10.3 to 7.10.6 ([#427](https://github.com/carlkidcrypto/ezsnmp/issues/427))

- Bump pytest-sugar from 1.0.0 to 1.1.1 ([#424](https://github.com/carlkidcrypto/ezsnmp/issues/424))

- Bump pypa/gh-action-pypi-publish[@release](https://github.com/release)/v1.12 from 1.12 to 1.13 ([#431](https://github.com/carlkidcrypto/ezsnmp/issues/431))

- Bump pytest from 8.4.1 to 8.4.2 ([#432](https://github.com/carlkidcrypto/ezsnmp/issues/432))

- Bump MishaKav/pytest-coverage-comment from 1.1.56 to 1.1.57 ([#429](https://github.com/carlkidcrypto/ezsnmp/issues/429))

- Bump actions/download-artifact from 4 to 5 ([#419](https://github.com/carlkidcrypto/ezsnmp/issues/419))

- Bump coverage from 7.9.2 to 7.10.3 ([#417](https://github.com/carlkidcrypto/ezsnmp/issues/417))

- Bump actions/checkout from 4 to 5 ([#418](https://github.com/carlkidcrypto/ezsnmp/issues/418))

- Bump MishaKav/pytest-coverage-comment from 1.1.54 to 1.1.56 ([#416](https://github.com/carlkidcrypto/ezsnmp/issues/416))

- Bump furo from 2024.8.6 to 2025.7.19 ([#407](https://github.com/carlkidcrypto/ezsnmp/issues/407))

- Bump coverage from 7.9.1 to 7.9.2 ([#402](https://github.com/carlkidcrypto/ezsnmp/issues/402))

- Bump pip from 25.1.1 to 25.2 ([#408](https://github.com/carlkidcrypto/ezsnmp/issues/408))

- Bump build from 1.2.2 to 1.3.0 ([#410](https://github.com/carlkidcrypto/ezsnmp/issues/410))

- Bump actions/download-artifact from 4 to 5 ([#413](https://github.com/carlkidcrypto/ezsnmp/issues/413))


#### Features

- Feature/get auto uts in docker containers ([#412](https://github.com/carlkidcrypto/ezsnmp/issues/412))

- Feature: Updating the docker containers ([#411](https://github.com/carlkidcrypto/ezsnmp/issues/411))


#### Maintenance

- chore: update CHANGELOG.md


#### Updates & Improvements

- Update pyproject.toml ([#434](https://github.com/carlkidcrypto/ezsnmp/issues/434))

- Update meson.build ([#433](https://github.com/carlkidcrypto/ezsnmp/issues/433))







### Merged Pull Requests

- Merge pull request [#405](https://github.com/carlkidcrypto/ezsnmp/issues/405) from carlkidcrypto/update-changelog-16362031442





---

<a name="v2.1.0a1"></a>
## [v2.1.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.1.0a0...v2.1.0a1) (2025-07-16)


### Changes

#### 401

- 401 feature   add convertvalue to datatypes ([#403](https://github.com/carlkidcrypto/ezsnmp/issues/403))


#### Dependency Updates

- Bump setuptools from 80.3.1 to 80.9.0 ([#382](https://github.com/carlkidcrypto/ezsnmp/issues/382))


#### Features

- Feature/Update Pyproject File For Linux Builds ([#399](https://github.com/carlkidcrypto/ezsnmp/issues/399))


#### Maintenance

- chore: update CHANGELOG.md ([#398](https://github.com/carlkidcrypto/ezsnmp/issues/398))


#### Updates & Improvements

- Update README.rst ([#400](https://github.com/carlkidcrypto/ezsnmp/issues/400))

- Update auto_change_log.yml ([#397](https://github.com/carlkidcrypto/ezsnmp/issues/397))

- Update auto_change_log.yml ([#396](https://github.com/carlkidcrypto/ezsnmp/issues/396))

- Update auto_change_log.yml ([#395](https://github.com/carlkidcrypto/ezsnmp/issues/395))

- Update auto_change_log.yml ([#394](https://github.com/carlkidcrypto/ezsnmp/issues/394))










---

<a name="v2.1.0a0"></a>
## [v2.1.0a0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.1...v2.1.0a0) (2025-06-22)


### Changes

#### 385

- 385 question getting raw value of timeticks ([#393](https://github.com/carlkidcrypto/ezsnmp/issues/393))


#### Dependency Updates

- Bump pluggy from 1.5.0 to 1.6.0 ([#378](https://github.com/carlkidcrypto/ezsnmp/issues/378))

- Bump pytest from 8.3.5 to 8.4.1 ([#391](https://github.com/carlkidcrypto/ezsnmp/issues/391))

- Bump pytest-cov from 6.2.0 to 6.2.1 ([#388](https://github.com/carlkidcrypto/ezsnmp/issues/388))

- Bump platformdirs from 4.3.7 to 4.3.8 ([#374](https://github.com/carlkidcrypto/ezsnmp/issues/374))

- Bump urllib3 from 2.4.0 to 2.5.0 ([#390](https://github.com/carlkidcrypto/ezsnmp/issues/390))

- Bump coverage from 7.9.0 to 7.9.1 ([#389](https://github.com/carlkidcrypto/ezsnmp/issues/389))

- Bump pycodestyle from 2.13.0 to None - Removed ([#392](https://github.com/carlkidcrypto/ezsnmp/issues/392))

- Bump pytest-cov from 6.1.1 to 6.2.0 ([#386](https://github.com/carlkidcrypto/ezsnmp/issues/386))

- Bump coverage from 7.8.0 to 7.9.0 ([#387](https://github.com/carlkidcrypto/ezsnmp/issues/387))


#### Features

- Feature/manual changelog update ([#373](https://github.com/carlkidcrypto/ezsnmp/issues/373))


#### MacOS

- MacOS Compilation ([#265](https://github.com/carlkidcrypto/ezsnmp/issues/265))










---

<a name="v2.0.1"></a>
## [v2.0.1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0...v2.0.1) (2025-05-06)


### Changes

#### 355

- 355 bug string values returned enclosed in ([#369](https://github.com/carlkidcrypto/ezsnmp/issues/369))


#### AlmaLinux

- AlmaLinux ([#371](https://github.com/carlkidcrypto/ezsnmp/issues/371))


#### Dependency Updates

- Bump MishaKav/pytest-coverage-comment from 1.1.53 to 1.1.54 ([#361](https://github.com/carlkidcrypto/ezsnmp/issues/361))

- Bump pip from 25.0.1 to 25.1.1 ([#365](https://github.com/carlkidcrypto/ezsnmp/issues/365))

- Bump termcolor from 3.0.1 to 3.1.0 ([#363](https://github.com/carlkidcrypto/ezsnmp/issues/363))

- Bump setuptools from 79.0.1 to 80.3.1 ([#370](https://github.com/carlkidcrypto/ezsnmp/issues/370))

- Bump cibuildwheel from 2.23.2 to 2.23.3 ([#359](https://github.com/carlkidcrypto/ezsnmp/issues/359))

- Bump pypa/gh-action-pypi-publish[@release](https://github.com/release)/v1.6 from 1.6 to 1.12 ([#354](https://github.com/carlkidcrypto/ezsnmp/issues/354))

- Bump DoozyX/clang-format-lint-action from 0.18.2 to 0.20 ([#352](https://github.com/carlkidcrypto/ezsnmp/issues/352))

- Bump psf/black from 24.10.0 to 25.1.0 ([#351](https://github.com/carlkidcrypto/ezsnmp/issues/351))

- Bump Limit to 10 ([#353](https://github.com/carlkidcrypto/ezsnmp/issues/353))

- Bump packaging from 24.2 to 25.0 ([#342](https://github.com/carlkidcrypto/ezsnmp/issues/342))

- Bump setuptools from 78.1.0 to 79.0.1 ([#345](https://github.com/carlkidcrypto/ezsnmp/issues/345))

- Bump peter-evans/create-pull-request from 4 to 7 ([#346](https://github.com/carlkidcrypto/ezsnmp/issues/346))

- Bump DoozyX/clang-format-lint-action from 0.18.1 to 0.18.2 ([#347](https://github.com/carlkidcrypto/ezsnmp/issues/347))

- Bump carlkidcrypto/os-specific-runner from 2.1.1 to 2.1.2 ([#348](https://github.com/carlkidcrypto/ezsnmp/issues/348))

- Bump tj-actions/changed-files from 46.0.3 to 46.0.5 ([#349](https://github.com/carlkidcrypto/ezsnmp/issues/349))

- Bump pypa/gh-action-pypi-publish[@release](https://github.com/release)/v1.6 from 1.6 to 1.12 ([#350](https://github.com/carlkidcrypto/ezsnmp/issues/350))


#### Docker

- Docker ([#366](https://github.com/carlkidcrypto/ezsnmp/issues/366))


#### Issue

- Issue 356 migration guide updates ([#357](https://github.com/carlkidcrypto/ezsnmp/issues/357))


#### Updates & Improvements

- Update bug_report.md ([#364](https://github.com/carlkidcrypto/ezsnmp/issues/364))










---

<a name="v2.0.0"></a>
## [v2.0.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0b3...v2.0.0) (2025-04-22)


### Changes

#### Bugfix

- Bugfix/fix dist upload pipeline - 2 ([#339](https://github.com/carlkidcrypto/ezsnmp/issues/339))

- Bugfix/fix dist upload pipeline ([#338](https://github.com/carlkidcrypto/ezsnmp/issues/338))


#### Dependency Updates

- Bump pytest-cov from 6.0.0 to 6.1.1 ([#333](https://github.com/carlkidcrypto/ezsnmp/issues/333))

- Bump wheel from 0.45.1 to 0.46.1 ([#334](https://github.com/carlkidcrypto/ezsnmp/issues/334))

- Bump urllib3 from 2.3.0 to 2.4.0 ([#335](https://github.com/carlkidcrypto/ezsnmp/issues/335))

- Bump pycodestyle from 2.12.1 to 2.13.0 ([#327](https://github.com/carlkidcrypto/ezsnmp/issues/327))

- Bump pyflakes from 3.2.0 to 3.3.2 ([#329](https://github.com/carlkidcrypto/ezsnmp/issues/329))

- Bump flake8 from 7.1.2 to 7.2.0 ([#330](https://github.com/carlkidcrypto/ezsnmp/issues/330))

- Bump coverage from 7.7.1 to 7.8.0 ([#331](https://github.com/carlkidcrypto/ezsnmp/issues/331))

- Bump termcolor from 2.5.0 to 3.0.1 ([#332](https://github.com/carlkidcrypto/ezsnmp/issues/332))

- Bump setuptools from 77.0.3 to 78.1.0 ([#324](https://github.com/carlkidcrypto/ezsnmp/issues/324))


#### Features

- Feature/fix py pi ([#343](https://github.com/carlkidcrypto/ezsnmp/issues/343))


#### Macos

- macos-15 ([#340](https://github.com/carlkidcrypto/ezsnmp/issues/340))


#### Release

- Release/prep for v2.0.0 ([#337](https://github.com/carlkidcrypto/ezsnmp/issues/337))


#### Verify

- verify-metadata ([#344](https://github.com/carlkidcrypto/ezsnmp/issues/344))










---

<a name="v2.0.0b3"></a>
## [v2.0.0b3](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0b2...v2.0.0b3) (2025-03-27)


### Changes

#### 297

- 297 bug   fix failing uts for new  o options ([#318](https://github.com/carlkidcrypto/ezsnmp/issues/318))


#### 303

- 303 bug session parameters in v200b2   better compatiblity with v1xx ([#307](https://github.com/carlkidcrypto/ezsnmp/issues/307))


#### Dependency Updates

- Bump pyparsing from 3.2.1 to 3.2.3 ([#323](https://github.com/carlkidcrypto/ezsnmp/issues/323))

- Bump cibuildwheel from 2.23.1 to 2.23.2 ([#320](https://github.com/carlkidcrypto/ezsnmp/issues/320))

- Bump tj-actions/changed-files ([#319](https://github.com/carlkidcrypto/ezsnmp/issues/319))

- Bump setuptools from 75.8.2 to 77.0.3 ([#316](https://github.com/carlkidcrypto/ezsnmp/issues/316))

- Bump coverage from 7.6.12 to 7.7.1 ([#317](https://github.com/carlkidcrypto/ezsnmp/issues/317))

- Bump platformdirs from 4.3.6 to 4.3.7 ([#315](https://github.com/carlkidcrypto/ezsnmp/issues/315))

- Bump cibuildwheel from 2.23.0 to 2.23.1 ([#311](https://github.com/carlkidcrypto/ezsnmp/issues/311))

- Bump attrs from 25.1.0 to 25.3.0 ([#310](https://github.com/carlkidcrypto/ezsnmp/issues/310))

- Bump breathe from 4.35.0 to 4.36.0 ([#300](https://github.com/carlkidcrypto/ezsnmp/issues/300))

- Bump setuptools from 75.8.0 to 75.8.2 ([#302](https://github.com/carlkidcrypto/ezsnmp/issues/302))

- Bump cibuildwheel from 2.22.0 to 2.23.0 ([#304](https://github.com/carlkidcrypto/ezsnmp/issues/304))

- Bump pytest from 8.3.4 to 8.3.5 ([#305](https://github.com/carlkidcrypto/ezsnmp/issues/305))

- Bump sphinx from 8.2.0 to 8.2.3 ([#306](https://github.com/carlkidcrypto/ezsnmp/issues/306))

- Bump pip from 25.0 to 25.0.1 ([#293](https://github.com/carlkidcrypto/ezsnmp/issues/293))

- Bump coverage from 7.6.10 to 7.6.12 ([#294](https://github.com/carlkidcrypto/ezsnmp/issues/294))

- Bump flake8 from 7.1.1 to 7.1.2 ([#295](https://github.com/carlkidcrypto/ezsnmp/issues/295))

- Bump sphinx from 8.1.3 to 8.2.0 ([#296](https://github.com/carlkidcrypto/ezsnmp/issues/296))


#### Updates & Improvements

- Update session.py










---

<a name="v2.0.0b2"></a>
## [v2.0.0b2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0b1...v2.0.0b2) (2025-02-19)


### Changes

#### 289

- 289 bug session parameters are missing in v200b1 ([#298](https://github.com/carlkidcrypto/ezsnmp/issues/298))


#### 290

- 290 bug   all ezsnmp exceptions should inherit from genericerror ([#291](https://github.com/carlkidcrypto/ezsnmp/issues/291))


#### Bugfix

- Bugfix/update auto change log ([#288](https://github.com/carlkidcrypto/ezsnmp/issues/288))

- Bugfix/update auto change log ([#287](https://github.com/carlkidcrypto/ezsnmp/issues/287))


#### Updates & Improvements

- Update auto_change_log.yml ([#286](https://github.com/carlkidcrypto/ezsnmp/issues/286))










---

<a name="v2.0.0b1"></a>
## [v2.0.0b1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0b0...v2.0.0b1) (2025-01-30)


### Changes

#### 281

- 281 bug unable to import ezexceptions with ezsnmp v200b0 ([#285](https://github.com/carlkidcrypto/ezsnmp/issues/285))


#### Cleanup

- Cleanup ([#279](https://github.com/carlkidcrypto/ezsnmp/issues/279))


#### Dependency Updates

- Bump attrs from 24.3.0 to 25.1.0 ([#282](https://github.com/carlkidcrypto/ezsnmp/issues/282))

- Bump pip from 24.3.1 to 25.0 ([#283](https://github.com/carlkidcrypto/ezsnmp/issues/283))

- Bump black from 24.10.0 to 25.1.0 ([#284](https://github.com/carlkidcrypto/ezsnmp/issues/284))

- Bump setuptools from 75.7.0 to 75.8.0 ([#274](https://github.com/carlkidcrypto/ezsnmp/issues/274))


#### Features

- Feature/auto changelog ([#280](https://github.com/carlkidcrypto/ezsnmp/issues/280))










---

<a name="v2.0.0b0"></a>
## [v2.0.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0a5...v2.0.0b0) (2025-01-11)


### Changes

#### Critical Bug Fixes

- Hotfix/fix status buttons in readme ([#277](https://github.com/carlkidcrypto/ezsnmp/issues/277))


#### Features

- Feature/sphinx docs ([#276](https://github.com/carlkidcrypto/ezsnmp/issues/276))


#### PyPi

- PyPi ([#278](https://github.com/carlkidcrypto/ezsnmp/issues/278))










---

<a name="v2.0.0a5"></a>
## [v2.0.0a5](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0a4...v2.0.0a5) (2025-01-08)


### Changes

#### PyPi

- PyPi fix ([#275](https://github.com/carlkidcrypto/ezsnmp/issues/275))










---

<a name="v2.0.0a4"></a>
## [v2.0.0a4](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0a3...v2.0.0a4) (2025-01-08)


### Changes

#### Critical Bug Fixes

- Hotfix/ga macos runners 2 ([#273](https://github.com/carlkidcrypto/ezsnmp/issues/273))


#### Dependency Updates

- Bump click from 8.1.7 to 8.1.8 ([#269](https://github.com/carlkidcrypto/ezsnmp/issues/269))

- Bump coverage from 7.6.9 to 7.6.10 ([#270](https://github.com/carlkidcrypto/ezsnmp/issues/270))

- Bump urllib3 from 2.2.3 to 2.3.0 ([#268](https://github.com/carlkidcrypto/ezsnmp/issues/268))

- Bump pyparsing from 3.2.0 to 3.2.1 ([#271](https://github.com/carlkidcrypto/ezsnmp/issues/271))

- Bump setuptools from 75.6.0 to 75.7.0 ([#272](https://github.com/carlkidcrypto/ezsnmp/issues/272))










---

<a name="v2.0.0a3"></a>
## [v2.0.0a3](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0a2...v2.0.0a3) (2024-12-20)


### Changes

#### 244

- 244 bug v200a2 ([#250](https://github.com/carlkidcrypto/ezsnmp/issues/250))


#### 255

- 255 ga builds ([#258](https://github.com/carlkidcrypto/ezsnmp/issues/258))


#### Dependency Updates

- Bump attrs from 24.2.0 to 24.3.0 ([#264](https://github.com/carlkidcrypto/ezsnmp/issues/264))

- Bump tj-actions/changed-files from 45.0.4 to 45.0.5 ([#261](https://github.com/carlkidcrypto/ezsnmp/issues/261))

- Bump coverage from 7.6.8 to 7.6.9 ([#259](https://github.com/carlkidcrypto/ezsnmp/issues/259))

- Bump wheel from 0.45.0 to 0.45.1 ([#251](https://github.com/carlkidcrypto/ezsnmp/issues/251))

- Bump cibuildwheel from 2.21.3 to 2.22.0 ([#252](https://github.com/carlkidcrypto/ezsnmp/issues/252))

- Bump coverage from 7.6.7 to 7.6.8 ([#253](https://github.com/carlkidcrypto/ezsnmp/issues/253))

- Bump tomli from 2.1.0 to 2.2.1 ([#254](https://github.com/carlkidcrypto/ezsnmp/issues/254))

- Bump tj-actions/changed-files from 45.0.3 to 45.0.4 ([#256](https://github.com/carlkidcrypto/ezsnmp/issues/256))

- Bump pytest from 8.3.3 to 8.3.4 ([#257](https://github.com/carlkidcrypto/ezsnmp/issues/257))

- Bump setuptools from 75.5.0 to 75.6.0 ([#249](https://github.com/carlkidcrypto/ezsnmp/issues/249))

- Bump coverage from 7.6.5 to 7.6.7 ([#246](https://github.com/carlkidcrypto/ezsnmp/issues/246))










---

<a name="v2.0.0a2"></a>
## [v2.0.0a2](https://github.com/carlkidcrypto/ezsnmp/compare/v1.1.0...v2.0.0a2) (2024-11-16)


### Changes

#### 180

- 180 swig ([#241](https://github.com/carlkidcrypto/ezsnmp/issues/241))


#### 240

- 240 bug bulkwalk runs indefinitely when encountering a non increasing oid ([#247](https://github.com/carlkidcrypto/ezsnmp/issues/247))


#### Dependency Updates

- Bump coverage from 7.6.4 to 7.6.5 ([#245](https://github.com/carlkidcrypto/ezsnmp/issues/245))

- Bump sphinx-rtd-theme from 3.0.1 to 3.0.2 ([#243](https://github.com/carlkidcrypto/ezsnmp/issues/243))

- Bump setuptools from 75.3.0 to 75.5.0 ([#242](https://github.com/carlkidcrypto/ezsnmp/issues/242))

- Bump tomli from 2.0.2 to 2.1.0 ([#238](https://github.com/carlkidcrypto/ezsnmp/issues/238))

- Bump tj-actions/changed-files from 45.0.3 to 45.0.4 ([#233](https://github.com/carlkidcrypto/ezsnmp/issues/233))

- Bump packaging from 24.1 to 24.2 ([#234](https://github.com/carlkidcrypto/ezsnmp/issues/234))

- Bump wheel from 0.43.0 to 0.45.0 ([#235](https://github.com/carlkidcrypto/ezsnmp/issues/235))

- Bump setuptools from 72.1.0 to 75.3.0 ([#236](https://github.com/carlkidcrypto/ezsnmp/issues/236))

- Bump setuptools from 75.2.0 to 75.3.0 ([#231](https://github.com/carlkidcrypto/ezsnmp/issues/231))

- Bump pip from 24.2 to 24.3.1 ([#230](https://github.com/carlkidcrypto/ezsnmp/issues/230))

- Bump pytest-cov from 5.0.0 to 6.0.0 ([#232](https://github.com/carlkidcrypto/ezsnmp/issues/232))

- Bump coverage from 7.6.3 to 7.6.4 ([#229](https://github.com/carlkidcrypto/ezsnmp/issues/229))

- Bump pyparsing from 3.1.4 to 3.2.0 ([#226](https://github.com/carlkidcrypto/ezsnmp/issues/226))

- Bump coverage from 7.6.2 to 7.6.3 ([#225](https://github.com/carlkidcrypto/ezsnmp/issues/225))

- Bump sphinx from 8.1.0 to 8.1.3 ([#224](https://github.com/carlkidcrypto/ezsnmp/issues/224))

- Bump setuptools from 75.1.0 to 75.2.0 ([#227](https://github.com/carlkidcrypto/ezsnmp/issues/227))


#### Dev

- Dev/v2.0.0 ([#239](https://github.com/carlkidcrypto/ezsnmp/issues/239))


#### Updates & Improvements

- Update setup.py ([#248](https://github.com/carlkidcrypto/ezsnmp/issues/248))










---

<a name="v1.1.0"></a>
## [v1.1.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.0.0a1...v1.1.0) (2024-10-11)









---

<a name="v2.0.0a1"></a>
## [v2.0.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v1.1.0.a1...v2.0.0a1) (2024-10-11)


### Changes

#### 181

- 181 snmptrapc support ([#210](https://github.com/carlkidcrypto/ezsnmp/issues/210))


#### 182

- 182 snmpsetc support ([#199](https://github.com/carlkidcrypto/ezsnmp/issues/199))


#### Cibuildwheel

- Cibuildwheel/fix for cibuildwheel ([#221](https://github.com/carlkidcrypto/ezsnmp/issues/221))


#### Dependency Updates

- Bump sphinx from 8.0.2 to 8.1.0 ([#220](https://github.com/carlkidcrypto/ezsnmp/issues/220))

- Bump actions/checkout from 3 to 4 ([#219](https://github.com/carlkidcrypto/ezsnmp/issues/219))

- Bump MishaKav/pytest-coverage-comment from 1.1.52 to 1.1.53 ([#218](https://github.com/carlkidcrypto/ezsnmp/issues/218))

- Bump sphinx-rtd-theme from 3.0.0 to 3.0.1 ([#211](https://github.com/carlkidcrypto/ezsnmp/issues/211))

- Bump coverage from 7.6.1 to 7.6.2 ([#212](https://github.com/carlkidcrypto/ezsnmp/issues/212))

- Bump cibuildwheel from 2.21.2 to 2.21.3 ([#213](https://github.com/carlkidcrypto/ezsnmp/issues/213))


#### Experimental

- Experimental/swig ([#193](https://github.com/carlkidcrypto/ezsnmp/issues/193))


#### Merged Pull Requests

- Merge branch 'main' into dev/v2.0.0

- Merge branch 'main' into dev/v2.0.0

- Merge branch 'main' into dev/v2.0.0

- Merge branch 'main' into dev/v2.0.0


#### New

- New Logo ([#217](https://github.com/carlkidcrypto/ezsnmp/issues/217))










---

<a name="v1.1.0.a1"></a>
## [v1.1.0.a1](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0...v1.1.0.a1) (2024-10-09)


### Changes

#### 183

- 183 drop python 38 support ([#197](https://github.com/carlkidcrypto/ezsnmp/issues/197))


#### 186

- 186 enable GitHub codeql for c code ([#215](https://github.com/carlkidcrypto/ezsnmp/issues/215))


#### Adding

- Adding Python Version ([#216](https://github.com/carlkidcrypto/ezsnmp/issues/216))


#### Create

- Create codeql-analysis.yml ([#214](https://github.com/carlkidcrypto/ezsnmp/issues/214))


#### Dependency Updates

- Bump psf/black from 24.8.0 to 24.10.0 ([#207](https://github.com/carlkidcrypto/ezsnmp/issues/207))

- Bump termcolor from 2.4.0 to 2.5.0 ([#204](https://github.com/carlkidcrypto/ezsnmp/issues/204))

- Bump black from 24.8.0 to 24.10.0 ([#206](https://github.com/carlkidcrypto/ezsnmp/issues/206))

- Bump sphinx-rtd-theme from 3.0.0rc3 to 3.0.0 ([#205](https://github.com/carlkidcrypto/ezsnmp/issues/205))

- Bump tj-actions/changed-files from 45.0.2 to 45.0.3 ([#203](https://github.com/carlkidcrypto/ezsnmp/issues/203))

- Bump cibuildwheel from 2.21.1 to 2.21.2 ([#201](https://github.com/carlkidcrypto/ezsnmp/issues/201))

- Bump tomli from 2.0.1 to 2.0.2 ([#200](https://github.com/carlkidcrypto/ezsnmp/issues/200))

- Bump cibuildwheel from 2.21.0 to 2.21.1 ([#191](https://github.com/carlkidcrypto/ezsnmp/issues/191))

- Bump platformdirs from 4.3.3 to 4.3.6 ([#192](https://github.com/carlkidcrypto/ezsnmp/issues/192))

- Bump carlkidcrypto/os-specific-runner from 2.1.0 to 2.1.1 ([#195](https://github.com/carlkidcrypto/ezsnmp/issues/195))

- Bump sphinx-rtd-theme from 3.0.0rc2 to 3.0.0rc3 ([#196](https://github.com/carlkidcrypto/ezsnmp/issues/196))

- Bump sphinx-rtd-theme from 3.0.0rc1 to 3.0.0rc2 ([#194](https://github.com/carlkidcrypto/ezsnmp/issues/194))

- Bump tj-actions/changed-files from 45.0.1 to 45.0.2 ([#189](https://github.com/carlkidcrypto/ezsnmp/issues/189))

- Bump setuptools from 74.1.2 to 75.1.0 ([#190](https://github.com/carlkidcrypto/ezsnmp/issues/190))


#### Python-related Changes

- Python 3.13 ([#198](https://github.com/carlkidcrypto/ezsnmp/issues/198))










---

<a name="v1.0.0"></a>
## [v1.0.0](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0c4...v1.0.0) (2024-09-16)


### Changes

#### 166

- 166 sphinx docs ([#179](https://github.com/carlkidcrypto/ezsnmp/issues/179))


#### 167

- 167 investigate arm64 builds for macos ([#168](https://github.com/carlkidcrypto/ezsnmp/issues/168))


#### Create

- Create FUNDING.yml ([#185](https://github.com/carlkidcrypto/ezsnmp/issues/185))


#### Dependency Updates

- Bump urllib3 from 2.2.2 to 2.2.3 ([#176](https://github.com/carlkidcrypto/ezsnmp/issues/176))

- Bump platformdirs from 4.3.2 to 4.3.3 ([#177](https://github.com/carlkidcrypto/ezsnmp/issues/177))

- Bump cibuildwheel from 2.20.0 to 2.21.0 ([#178](https://github.com/carlkidcrypto/ezsnmp/issues/178))

- Bump platformdirs from 4.2.2 to 4.3.2 ([#174](https://github.com/carlkidcrypto/ezsnmp/issues/174))

- Bump pytest from 8.3.2 to 8.3.3 ([#175](https://github.com/carlkidcrypto/ezsnmp/issues/175))

- Bump build from 1.2.1 to 1.2.2 ([#173](https://github.com/carlkidcrypto/ezsnmp/issues/173))

- Bump setuptools from 74.1.1 to 74.1.2 ([#172](https://github.com/carlkidcrypto/ezsnmp/issues/172))

- Bump tj-actions/changed-files from 45.0.0 to 45.0.1 ([#170](https://github.com/carlkidcrypto/ezsnmp/issues/170))

- Bump setuptools from 74.0.0 to 74.1.1 ([#171](https://github.com/carlkidcrypto/ezsnmp/issues/171))


#### Updates & Improvements

- Update build_and_publish_to_pypi.yml ([#187](https://github.com/carlkidcrypto/ezsnmp/issues/187))










---

<a name="v1.0.0c4"></a>
## [v1.0.0c4](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0c3...v1.0.0c4) (2024-09-01)


### Changes

#### Cibuildwheel

- Cibuildwheel/fix the pipeline for ga ([#165](https://github.com/carlkidcrypto/ezsnmp/issues/165))


#### Dependency Updates

- Bump setuptools from 73.0.1 to 74.0.0 ([#162](https://github.com/carlkidcrypto/ezsnmp/issues/162))

- Bump pyparsing from 3.1.2 to 3.1.4 ([#161](https://github.com/carlkidcrypto/ezsnmp/issues/161))

- Bump setuptools from 72.1.0 to 73.0.1 ([#159](https://github.com/carlkidcrypto/ezsnmp/issues/159))

- Bump tj-actions/changed-files from 44.5.7 to 45.0.0 ([#160](https://github.com/carlkidcrypto/ezsnmp/issues/160))

- Bump sphinx from 8.0.0 to 8.0.2 ([#156](https://github.com/carlkidcrypto/ezsnmp/issues/156))

- Bump wheel from 0.43.0 to 0.44.0 ([#155](https://github.com/carlkidcrypto/ezsnmp/issues/155))

- Bump attrs from 23.2.0 to 24.2.0 ([#154](https://github.com/carlkidcrypto/ezsnmp/issues/154))

- Bump sphinx from 7.4.7 to 8.0.0 ([#142](https://github.com/carlkidcrypto/ezsnmp/issues/142))

- Bump flake8 from 7.1.0 to 7.1.1 ([#152](https://github.com/carlkidcrypto/ezsnmp/issues/152))

- Bump cibuildwheel from 2.19.2 to 2.20.0 ([#151](https://github.com/carlkidcrypto/ezsnmp/issues/151))

- Bump coverage from 7.6.0 to 7.6.1 ([#150](https://github.com/carlkidcrypto/ezsnmp/issues/150))

- Bump pycodestyle from 2.12.0 to 2.12.1 ([#153](https://github.com/carlkidcrypto/ezsnmp/issues/153))

- Bump black from 24.4.2 to 24.8.0 ([#148](https://github.com/carlkidcrypto/ezsnmp/issues/148))

- Bump psf/black from 24.4.2 to 24.8.0 ([#147](https://github.com/carlkidcrypto/ezsnmp/issues/147))

- Bump tj-actions/changed-files from 44.5.6 to 44.5.7 ([#146](https://github.com/carlkidcrypto/ezsnmp/issues/146))


#### Features

- feat: add type annotations for internal code ([#149](https://github.com/carlkidcrypto/ezsnmp/issues/149))


#### Release

- Release/v1.0.0rc4 ([#164](https://github.com/carlkidcrypto/ezsnmp/issues/164))










---

<a name="v1.0.0c3"></a>
## [v1.0.0c3](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0c2...v1.0.0c3) (2024-07-31)


### Changes

#### Dependency Updates

- Bump pip from 24.1.2 to 24.2 ([#143](https://github.com/carlkidcrypto/ezsnmp/issues/143))

- Bump setuptools from 71.1.0 to 72.1.0 ([#144](https://github.com/carlkidcrypto/ezsnmp/issues/144))

- Bump pytest from 8.3.1 to 8.3.2 ([#140](https://github.com/carlkidcrypto/ezsnmp/issues/140))

- Bump setuptools from 71.0.4 to 71.1.0 ([#137](https://github.com/carlkidcrypto/ezsnmp/issues/137))

- Bump pytest from 8.2.2 to 8.3.1 ([#136](https://github.com/carlkidcrypto/ezsnmp/issues/136))

- Bump sphinx from 7.4.6 to 7.4.7 ([#135](https://github.com/carlkidcrypto/ezsnmp/issues/135))

- Bump setuptools from 71.0.3 to 71.0.4 ([#133](https://github.com/carlkidcrypto/ezsnmp/issues/133))

- Bump setuptools from 70.3.0 to 71.0.3 ([#132](https://github.com/carlkidcrypto/ezsnmp/issues/132))

- Bump sphinx from 7.4.4 to 7.4.6 ([#131](https://github.com/carlkidcrypto/ezsnmp/issues/131))

- Bump tj-actions/changed-files from 44.5.5 to 44.5.6 ([#130](https://github.com/carlkidcrypto/ezsnmp/issues/130))

- Bump coverage from 7.5.4 to 7.6.0 ([#126](https://github.com/carlkidcrypto/ezsnmp/issues/126))

- Bump sphinx from 7.3.7 to 7.4.4 ([#127](https://github.com/carlkidcrypto/ezsnmp/issues/127))

- Bump tj-actions/changed-files from 44.5.3 to 44.5.5 ([#117](https://github.com/carlkidcrypto/ezsnmp/issues/117))

- Bump coverage from 7.5.3 to 7.5.4 ([#118](https://github.com/carlkidcrypto/ezsnmp/issues/118))

- Bump MishaKav/pytest-coverage-comment from 1.1.51 to 1.1.52 ([#121](https://github.com/carlkidcrypto/ezsnmp/issues/121))

- Bump cibuildwheel from 2.19.1 to 2.19.2 ([#123](https://github.com/carlkidcrypto/ezsnmp/issues/123))

- Bump pip from 24.1 to 24.1.2 ([#124](https://github.com/carlkidcrypto/ezsnmp/issues/124))

- Bump setuptools from 70.1.0 to 70.3.0 ([#125](https://github.com/carlkidcrypto/ezsnmp/issues/125))

- Bump setuptools from 70.0.0 to 70.1.0 ([#114](https://github.com/carlkidcrypto/ezsnmp/issues/114))

- Bump pip from 24.0 to 24.1 ([#115](https://github.com/carlkidcrypto/ezsnmp/issues/115))

- Bump tj-actions/changed-files from 44.5.2 to 44.5.3 ([#116](https://github.com/carlkidcrypto/ezsnmp/issues/116))

- Bump flake8 from 7.0.0 to 7.1.0 ([#112](https://github.com/carlkidcrypto/ezsnmp/issues/112))

- Bump urllib3 from 2.2.1 to 2.2.2 in the pip group ([#110](https://github.com/carlkidcrypto/ezsnmp/issues/110))

- Bump pycodestyle from 2.11.1 to 2.12.0 ([#111](https://github.com/carlkidcrypto/ezsnmp/issues/111))


#### Features

- Feature/pull in more upstream fixes ([#134](https://github.com/carlkidcrypto/ezsnmp/issues/134))


#### Features

- feat: add type for high level api # 138 ([#139](https://github.com/carlkidcrypto/ezsnmp/issues/139))


#### Prepping

- Prepping For V1.0.0.c3 ([#145](https://github.com/carlkidcrypto/ezsnmp/issues/145))


#### Updates & Improvements

- Update build_and_publish_to_test_pypi.yml ([#113](https://github.com/carlkidcrypto/ezsnmp/issues/113))










---

<a name="v1.0.0c2"></a>
## [v1.0.0c2](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0c1...v1.0.0c2) (2024-06-14)


### Changes

#### 50

- 50 bug ezsnmperror usm unknown security name no such user exists ([#108](https://github.com/carlkidcrypto/ezsnmp/issues/108))


#### Bugfix

- Bugfix/look into [#96](https://github.com/carlkidcrypto/ezsnmp/issues/96) ([#102](https://github.com/carlkidcrypto/ezsnmp/issues/102))


#### Code Refactoring

- Use snprintf ([#104](https://github.com/carlkidcrypto/ezsnmp/issues/104))


#### Dependency Updates

- Bump cibuildwheel from 2.19.0 to 2.19.1 ([#107](https://github.com/carlkidcrypto/ezsnmp/issues/107))

- Bump cibuildwheel from 2.18.1 to 2.19.0 ([#106](https://github.com/carlkidcrypto/ezsnmp/issues/106))

- Bump packaging from 24.0 to 24.1 ([#105](https://github.com/carlkidcrypto/ezsnmp/issues/105))

- Bump tj-actions/changed-files from 44.5.1 to 44.5.2 ([#100](https://github.com/carlkidcrypto/ezsnmp/issues/100))

- Bump pytest from 8.2.1 to 8.2.2 ([#101](https://github.com/carlkidcrypto/ezsnmp/issues/101))

- Bump coverage from 7.5.2 to 7.5.3 ([#99](https://github.com/carlkidcrypto/ezsnmp/issues/99))

- Bump coverage from 7.5.1 to 7.5.2 ([#98](https://github.com/carlkidcrypto/ezsnmp/issues/98))

- Bump tj-actions/changed-files from 44.4.0 to 44.5.1 ([#97](https://github.com/carlkidcrypto/ezsnmp/issues/97))

- Bump platformdirs from 4.2.1 to 4.2.2 ([#91](https://github.com/carlkidcrypto/ezsnmp/issues/91))

- Bump cibuildwheel from 2.17.0 to 2.18.0 ([#90](https://github.com/carlkidcrypto/ezsnmp/issues/90))

- Bump tj-actions/changed-files from 44.3.0 to 44.4.0 ([#89](https://github.com/carlkidcrypto/ezsnmp/issues/89))

- Bump coverage from 7.5.0 to 7.5.1 ([#87](https://github.com/carlkidcrypto/ezsnmp/issues/87))

- Bump carlkidcrypto/os-specific-runner from 2.0.0 to 2.1.0 ([#88](https://github.com/carlkidcrypto/ezsnmp/issues/88))

- Bump psf/black from 24.4.1 to 24.4.2 ([#84](https://github.com/carlkidcrypto/ezsnmp/issues/84))

- Bump pytest from 8.1.1 to 8.2.0 ([#86](https://github.com/carlkidcrypto/ezsnmp/issues/86))

- Bump black from 24.4.0 to 24.4.2 ([#83](https://github.com/carlkidcrypto/ezsnmp/issues/83))

- Bump psf/black from 24.4.0 to 24.4.1 ([#81](https://github.com/carlkidcrypto/ezsnmp/issues/81))

- Bump coverage from 7.4.4 to 7.5.0 ([#80](https://github.com/carlkidcrypto/ezsnmp/issues/80))

- Bump platformdirs from 4.2.0 to 4.2.1 ([#79](https://github.com/carlkidcrypto/ezsnmp/issues/79))

- Bump pluggy from 1.4.0 to 1.5.0 ([#78](https://github.com/carlkidcrypto/ezsnmp/issues/78))

- Bump chuhlomin/render-template from 1.9 to 1.10 ([#77](https://github.com/carlkidcrypto/ezsnmp/issues/77))

- Bump sphinx from 7.3.6 to 7.3.7 ([#76](https://github.com/carlkidcrypto/ezsnmp/issues/76))

- Bump tj-actions/changed-files from 44.1.0 to 44.3.0 ([#75](https://github.com/carlkidcrypto/ezsnmp/issues/75))

- Bump tj-actions/changed-files from 44.0.1 to 44.1.0 ([#74](https://github.com/carlkidcrypto/ezsnmp/issues/74))

- Bump sphinx from 7.3.0 to 7.3.6 ([#73](https://github.com/carlkidcrypto/ezsnmp/issues/73))

- Bump sphinx from 7.2.6 to 7.3.0 ([#72](https://github.com/carlkidcrypto/ezsnmp/issues/72))

- Bump setuptools from 69.2.0 to 69.5.1 ([#71](https://github.com/carlkidcrypto/ezsnmp/issues/71))

- Bump black from 24.3.0 to 24.4.0 ([#70](https://github.com/carlkidcrypto/ezsnmp/issues/70))

- Bump psf/black from 24.3.0 to 24.4.0 ([#69](https://github.com/carlkidcrypto/ezsnmp/issues/69))

- Bump tj-actions/changed-files from 44.0.0 to 44.0.1 ([#68](https://github.com/carlkidcrypto/ezsnmp/issues/68))

- Bump build from 1.1.1 to 1.2.1 ([#66](https://github.com/carlkidcrypto/ezsnmp/issues/66))

- Bump tj-actions/changed-files from 43.0.1 to 44.0.0 ([#65](https://github.com/carlkidcrypto/ezsnmp/issues/65))

- Bump pytest-cov from 4.1.0 to 5.0.0 ([#63](https://github.com/carlkidcrypto/ezsnmp/issues/63))

- Bump tj-actions/changed-files from 43.0.0 to 43.0.1 ([#62](https://github.com/carlkidcrypto/ezsnmp/issues/62))

- Bump black from 24.2.0 to 24.3.0 ([#61](https://github.com/carlkidcrypto/ezsnmp/issues/61))

- Bump psf/black from 24.2.0 to 24.3.0 ([#60](https://github.com/carlkidcrypto/ezsnmp/issues/60))

- Bump coverage from 7.4.3 to 7.4.4 ([#59](https://github.com/carlkidcrypto/ezsnmp/issues/59))

- Bump setuptools from 69.1.1 to 69.2.0 ([#58](https://github.com/carlkidcrypto/ezsnmp/issues/58))

- Bump tj-actions/changed-files from 42.1.0 to 43.0.0 ([#57](https://github.com/carlkidcrypto/ezsnmp/issues/57))

- Bump tj-actions/changed-files from 42.0.7 to 42.1.0 ([#55](https://github.com/carlkidcrypto/ezsnmp/issues/55))

- Bump pytest from 8.0.2 to 8.1.1 ([#54](https://github.com/carlkidcrypto/ezsnmp/issues/54))

- Bump wheel from 0.38.1 to 0.43.0 ([#53](https://github.com/carlkidcrypto/ezsnmp/issues/53))

- Bump cibuildwheel from 2.16.5 to 2.17.0 ([#52](https://github.com/carlkidcrypto/ezsnmp/issues/52))

- Bump packaging from 23.2 to 24.0 ([#51](https://github.com/carlkidcrypto/ezsnmp/issues/51))


#### Features

- Feature/fix pypi deployment ([#103](https://github.com/carlkidcrypto/ezsnmp/issues/103))


#### Manual

- Manual Pull In ([#109](https://github.com/carlkidcrypto/ezsnmp/issues/109))


#### Pulls

- Pulls in Three PRs From upstream easysnmp ([#67](https://github.com/carlkidcrypto/ezsnmp/issues/67))


#### Updates & Improvements

- Update setup.py










---

<a name="v1.0.0c1"></a>
## [v1.0.0c1](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0c...v1.0.0c1) (2024-03-09)


### Changes

#### 44

- 44 bug v3 multi threading fails due to user cache ([#45](https://github.com/carlkidcrypto/ezsnmp/issues/45))


#### Dependency Updates

- Bump wheel from 0.37.1 to 0.38.1 ([#49](https://github.com/carlkidcrypto/ezsnmp/issues/49))

- Bump tj-actions/changed-files from 42.0.5 to 42.0.7 ([#48](https://github.com/carlkidcrypto/ezsnmp/issues/48))

- Bump pyparsing from 3.1.1 to 3.1.2 ([#46](https://github.com/carlkidcrypto/ezsnmp/issues/46))

- Bump build from 1.0.3 to 1.1.1 ([#43](https://github.com/carlkidcrypto/ezsnmp/issues/43))

- Bump pytest from 8.0.1 to 8.0.2 ([#42](https://github.com/carlkidcrypto/ezsnmp/issues/42))

- Bump tj-actions/changed-files from 42.0.4 to 42.0.5 ([#41](https://github.com/carlkidcrypto/ezsnmp/issues/41))










---

<a name="v1.0.0c"></a>
## [v1.0.0c](https://github.com/carlkidcrypto/ezsnmp/compare/v1.0.0b...v1.0.0c) (2024-02-26)


### Changes

#### 19

- 19 cibuildwheel tests ([#40](https://github.com/carlkidcrypto/ezsnmp/issues/40))


#### Dependency Updates

- Bump coverage from 7.4.2 to 7.4.3 ([#38](https://github.com/carlkidcrypto/ezsnmp/issues/38))

- Bump setuptools from 69.1.0 to 69.1.1 ([#39](https://github.com/carlkidcrypto/ezsnmp/issues/39))

- Bump coverage from 7.4.1 to 7.4.2 ([#37](https://github.com/carlkidcrypto/ezsnmp/issues/37))

- Bump urllib3 from 2.2.0 to 2.2.1 ([#35](https://github.com/carlkidcrypto/ezsnmp/issues/35))

- Bump tj-actions/changed-files from 42.0.2 to 42.0.4 ([#36](https://github.com/carlkidcrypto/ezsnmp/issues/36))

- Bump pip from 23.3.2 to 24.0 ([#29](https://github.com/carlkidcrypto/ezsnmp/issues/29))

- Bump setuptools from 69.0.3 to 69.1.0 ([#30](https://github.com/carlkidcrypto/ezsnmp/issues/30))

- Bump black from 24.1.1 to 24.2.0 ([#31](https://github.com/carlkidcrypto/ezsnmp/issues/31))

- Bump psf/black from 24.1.1 to 24.2.0 ([#32](https://github.com/carlkidcrypto/ezsnmp/issues/32))

- Bump MishaKav/pytest-coverage-comment from 1.1.50 to 1.1.51 ([#33](https://github.com/carlkidcrypto/ezsnmp/issues/33))

- Bump pytest from 8.0.0 to 8.0.1 ([#34](https://github.com/carlkidcrypto/ezsnmp/issues/34))

- Bump platformdirs from 2.5.2 to 4.2.0 ([#26](https://github.com/carlkidcrypto/ezsnmp/issues/26))

- Bump setuptools from 69.0.2 to 69.0.3 ([#27](https://github.com/carlkidcrypto/ezsnmp/issues/27))

- Bump pytest-sugar from 0.9.7 to 1.0.0 ([#28](https://github.com/carlkidcrypto/ezsnmp/issues/28))


#### Updates & Improvements

- Update README.rst










---

<a name="v1.0.0b"></a>
## v1.0.0b (2024-01-31)


### Changes

#### 3

- 3 Ensure Sphinx Build Works ([#7](https://github.com/carlkidcrypto/ezsnmp/issues/7))


#### 4

- 4 ensure macos tests work ([#9](https://github.com/carlkidcrypto/ezsnmp/issues/9))


#### 5

- 5 pypi ([#10](https://github.com/carlkidcrypto/ezsnmp/issues/10))


#### 6

- 6 move to c++17 ([#8](https://github.com/carlkidcrypto/ezsnmp/issues/8))


#### Adding

- Adding Docker Support


#### Apk

- apk add


#### Cibuildwheel

- Cibuildwheel ([#20](https://github.com/carlkidcrypto/ezsnmp/issues/20))


#### Create

- Create pyproject.toml


#### Dependency Updates

- Bump psf/black from 24.1.0 to 24.1.1 ([#17](https://github.com/carlkidcrypto/ezsnmp/issues/17))

- Bump cibuildwheel from 2.16.2 to 2.16.5 ([#21](https://github.com/carlkidcrypto/ezsnmp/issues/21))

- Bump pytest from 7.4.4 to 8.0.0 ([#22](https://github.com/carlkidcrypto/ezsnmp/issues/22))

- Bump urllib3 from 2.1.0 to 2.2.0 ([#23](https://github.com/carlkidcrypto/ezsnmp/issues/23))

- Bump black from 24.1.0 to 24.1.1 ([#24](https://github.com/carlkidcrypto/ezsnmp/issues/24))

- Bump pluggy from 1.0.0 to 1.4.0 ([#25](https://github.com/carlkidcrypto/ezsnmp/issues/25))

- Bump tj-actions/changed-files from 42.0.0 to 42.0.2 ([#14](https://github.com/carlkidcrypto/ezsnmp/issues/14))

- Bump peter-evans/create-or-update-comment from 3 to 4 ([#15](https://github.com/carlkidcrypto/ezsnmp/issues/15))

- Bump psf/black from 23.12.1 to 24.1.0 ([#16](https://github.com/carlkidcrypto/ezsnmp/issues/16))

- Bump tj-actions/changed-files from 41.0.1 to 42.0.0 ([#13](https://github.com/carlkidcrypto/ezsnmp/issues/13))


#### Features

- Feature/rename stuff ([#2](https://github.com/carlkidcrypto/ezsnmp/issues/2))


#### Fixing

- Fixing PyPi


#### Initial Setup

- Initial commit


#### Merged Pull Requests

- Merge branch 'main' of https://github.com/carlkidcrypto/ezsnmp

- Merge branch 'main' of https://github.com/carlkidcrypto/ezsnmp

- Merge branch 'main' of https://github.com/carlkidcrypto/ezsnmp


#### PyPI

- PyPI Workflows


#### PyPi

- PyPi Test Worflow

- PyPi 5000

- PyPi Aagain

- PyPi Workflows Again

- PyPi


#### TOML

- TOML 2

- TOML


#### Updates & Improvements

- Update pyproject.toml

- Update pyproject.toml

- Update pyproject.toml

- Update pyproject.toml

- Update pyproject.toml

- Update pyproject.toml

- Update setup.py

- Update README.rst

- Update README.rst


#### YUM

- YUM










---
