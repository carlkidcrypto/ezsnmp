Last Updated: 2026-11-25 03:31:16 UTC

# Changelog

<a name="v2026.11.24b0"></a>
## [v2026.11.24b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2026.11.22b0...v2026.11.24b0) (2026-11-24)

### Changes

#### Bug Fixes
- fix(memory): initialize Net-SNMP once per process and RAII-clean netsnmp_session ([#1519](https://github.com/carlkidcrypto/ezsnmp/issues/1519)) ([#1530](https://github.com/carlkidcrypto/ezsnmp/issues/1530))
- fix(docker): add libnl-route-3-dev to debian13_netsnmp_5.10 for mibII/ifTable agent support ([#1535](https://github.com/carlkidcrypto/ezsnmp/issues/1535))
- fix(ci): prevent C++ JUnit XML artifact collision on download ([#1529](https://github.com/carlkidcrypto/ezsnmp/issues/1529))

#### Continuous Integration
- ci: enforce Net-SNMP 5.10, add build caching, and enable debian13_netsnmp_5.10 across workflows ([#1537](https://github.com/carlkidcrypto/ezsnmp/issues/1537))

#### Documentation Updates
- docs(readme): add TestPyPI version badge ([#1528](https://github.com/carlkidcrypto/ezsnmp/issues/1528))
- docs: add versioned documentation for v2026.11.22b0 ([#1526](https://github.com/carlkidcrypto/ezsnmp/issues/1526))

#### Features
- feat(docker): add debian13_netsnmp_5.10 test container environment ([#1531](https://github.com/carlkidcrypto/ezsnmp/issues/1531))

#### Maintenance
- chore(release): prepare beta release v2026.11.24b0 ([#1541](https://github.com/carlkidcrypto/ezsnmp/issues/1541))
- chore(ci): bump shared-workflows to eeefdd5 ([#1540](https://github.com/carlkidcrypto/ezsnmp/issues/1540))
- chore(analysis): update integration-test history with 45 new PR runs (through [#1530](https://github.com/carlkidcrypto/ezsnmp/issues/1530)) and optimize pagination ([#1539](https://github.com/carlkidcrypto/ezsnmp/issues/1539))
- chore(deps): bump coverage ([#1507](https://github.com/carlkidcrypto/ezsnmp/issues/1507))
- chore(build): remove MacPorts detection, setup, and test support ([#1522](https://github.com/carlkidcrypto/ezsnmp/issues/1522))
- chore: update Homebrew formula for v2026.11.22b0 ([#1525](https://github.com/carlkidcrypto/ezsnmp/issues/1525))
- chore(ci): remove MacPorts workflow, version file, and docs references ([#1521](https://github.com/carlkidcrypto/ezsnmp/issues/1521))

#### Updates & Improvements
- [changelog] Update CHANGELOG.md ([#1524](https://github.com/carlkidcrypto/ezsnmp/issues/1524))

---

<a name="v2026.11.22b0"></a>
## [v2026.11.22b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2026.11.15b0...v2026.11.22b0) (2026-11-22)

### Changes

#### Apply
- Apply filtered changes ([#1489](https://github.com/carlkidcrypto/ezsnmp/issues/1489))

#### Bug Fixes
- fix(ci): restore id-token: write on reusable_pypi_publish caller jobs ([#1517](https://github.com/carlkidcrypto/ezsnmp/issues/1517))
- fix(ci): stage Homebrew formula in local tap for brew 7.0.14+ ([#1492](https://github.com/carlkidcrypto/ezsnmp/issues/1492))

#### Documentation Updates
- docs: standardize README status badges to 4-row flat-square layout ([#1494](https://github.com/carlkidcrypto/ezsnmp/issues/1494))
- docs: add versioned documentation for v2026.11.15b0 ([#1479](https://github.com/carlkidcrypto/ezsnmp/issues/1479))

#### Maintenance
- chore(release): prepare beta release v2026.11.22b0 ([#1518](https://github.com/carlkidcrypto/ezsnmp/issues/1518))
- chore(ci): bump shared-workflows to 22f04e2 and add caller-side PyPI OIDC publish ([#1516](https://github.com/carlkidcrypto/ezsnmp/issues/1516))
- chore(ci): adopt shared-workflows Tier 2 & 3 DRY actions and gh-aw fragments ([#1509](https://github.com/carlkidcrypto/ezsnmp/issues/1509))
- chore(ci): adopt shared-workflows Tier 1 DRY actions and reusable workflows ([#1506](https://github.com/carlkidcrypto/ezsnmp/issues/1506))
- chore(deps): bump the github-actions group with 2 updates ([#1508](https://github.com/carlkidcrypto/ezsnmp/issues/1508))
- chore(ci): migrate sphinx_build to reusable_sphinx_build and partially migrate tests_cpp_native ([#1500](https://github.com/carlkidcrypto/ezsnmp/issues/1500))
- chore(ci): migrate PyPI and TestPyPI publish workflows to reusable_pypi_publish ([#1499](https://github.com/carlkidcrypto/ezsnmp/issues/1499))
- chore(ci): migrate lint, verify, and copilot setup workflows to shared-workflows ([#1498](https://github.com/carlkidcrypto/ezsnmp/issues/1498))
- chore(ci): bump shared-workflows SHA to 88de7dd ([#1497](https://github.com/carlkidcrypto/ezsnmp/issues/1497))
- chore(ci): adopt carlkidcrypto/shared-workflows ([#1495](https://github.com/carlkidcrypto/ezsnmp/issues/1495))
- chore(ci): recompile agentic workflows with gh-aw v1.2.2 ([#1491](https://github.com/carlkidcrypto/ezsnmp/issues/1491))
- chore(changelog): standardize git-chglog config, template, and auto-changelog workflow ([#1490](https://github.com/carlkidcrypto/ezsnmp/issues/1490))
- chore: update Homebrew formula for v2026.11.15b0 ([#1478](https://github.com/carlkidcrypto/ezsnmp/issues/1478))
- chore(docs): update changelog ([#1480](https://github.com/carlkidcrypto/ezsnmp/issues/1480))

---

<a name="v2026.11.15b0"></a>
## [v2026.11.15b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2026.11.9b0...v2026.11.15b0) (2026-11-15)

### Changes

#### Bug Fixes
- fix(docker): patch CPython _ssl.c for OpenSSL 4.x compatibility and verify PR builds ([#1473](https://github.com/carlkidcrypto/ezsnmp/issues/1473))
- fix(ci): update apt index in Homebrew workflow and hash both Sphinx manifests ([#1472](https://github.com/carlkidcrypto/ezsnmp/issues/1472))

#### Documentation Updates
- docs: add versioned documentation for v2026.11.9b0 ([#1466](https://github.com/carlkidcrypto/ezsnmp/issues/1466))

#### Maintenance
- chore(release): bump version to 2026.11.15b0 ([#1474](https://github.com/carlkidcrypto/ezsnmp/issues/1474))
- chore(deps): bump net-snmp from 5.10.pre2 to 5.10.rc1 ([#1471](https://github.com/carlkidcrypto/ezsnmp/issues/1471))
- chore(deps): bump coverage ([#1469](https://github.com/carlkidcrypto/ezsnmp/issues/1469))
- chore(deps): bump the github-actions group with 8 updates ([#1470](https://github.com/carlkidcrypto/ezsnmp/issues/1470))
- chore(docs): update changelog ([#1467](https://github.com/carlkidcrypto/ezsnmp/issues/1467))
- chore: update Homebrew formula for v2026.11.9b0 ([#1465](https://github.com/carlkidcrypto/ezsnmp/issues/1465))

---

<a name="v2026.11.9b0"></a>
## [v2026.11.9b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2026.11.4a0...v2026.11.9b0) (2026-11-09)

### Changes

#### Bug Fixes
- fix(sonarcloud): configure analysis scope, test categorization, and resolve security vulnerabilities ([#1464](https://github.com/carlkidcrypto/ezsnmp/issues/1464))
- fix(docs): restore v2.5.0 documentation and prune superseded beta prereleases ([#1460](https://github.com/carlkidcrypto/ezsnmp/issues/1460))

#### Code Refactoring
- refactor(agentics): rename docs continuous improvement workflow to docs_continuous_improvement.md ([#1461](https://github.com/carlkidcrypto/ezsnmp/issues/1461))

#### Documentation Updates
- docs(github): update issue templates with AI-assisted triage notices ([#1462](https://github.com/carlkidcrypto/ezsnmp/issues/1462))
- docs: add versioned documentation for v2026.11.4a0 ([#1456](https://github.com/carlkidcrypto/ezsnmp/issues/1456))

#### Maintenance
- chore: bump version to 2026.11.9b0 ([#1463](https://github.com/carlkidcrypto/ezsnmp/issues/1463))
- chore(docs): update changelog ([#1457](https://github.com/carlkidcrypto/ezsnmp/issues/1457))
- chore(deps): bump the python-dependencies group with 2 updates ([#1458](https://github.com/carlkidcrypto/ezsnmp/issues/1458))
- chore(deps): bump the github-actions group with 2 updates ([#1459](https://github.com/carlkidcrypto/ezsnmp/issues/1459))
- chore: update Homebrew formula for v2026.11.4a0 ([#1455](https://github.com/carlkidcrypto/ezsnmp/issues/1455))

---

<a name="v2026.11.4a0"></a>
## [v2026.11.4a0](https://github.com/carlkidcrypto/ezsnmp/compare/v2026.10.28a0...v2026.11.4a0) (2026-11-05)

### Changes

#### Bug Fixes
- fix(ci): strip blank lines inside pytest coverage summaryReport tables ([#1454](https://github.com/carlkidcrypto/ezsnmp/issues/1454))
- fix(ci): allow all tools and permit protected files in python version watcher workflow ([#1452](https://github.com/carlkidcrypto/ezsnmp/issues/1452))
- fix(ci): restore Valgrind execution across all Python matrix versions and guard against cancelled jobs ([#1447](https://github.com/carlkidcrypto/ezsnmp/issues/1447))

#### Continuous Integration
- ci(sphinx): prepare Net-SNMP 5.10 and enable Sphinx Docs Build on pull requests ([#1450](https://github.com/carlkidcrypto/ezsnmp/issues/1450))

#### Maintenance
- chore: bump version to 2026.11.4a0 ([#1453](https://github.com/carlkidcrypto/ezsnmp/issues/1453))
- chore(docker): update Python patch versions in Dockerfiles ([#1449](https://github.com/carlkidcrypto/ezsnmp/issues/1449))
- chore(docs): update changelog ([#1448](https://github.com/carlkidcrypto/ezsnmp/issues/1448))
- chore: update Homebrew formula for v2026.10.28a0 ([#1446](https://github.com/carlkidcrypto/ezsnmp/issues/1446))
- chore(deps): bump the github-actions group with 3 updates ([#1444](https://github.com/carlkidcrypto/ezsnmp/issues/1444))
- chore(deps): bump the python-dependencies group with 2 updates ([#1443](https://github.com/carlkidcrypto/ezsnmp/issues/1443))

---

<a name="v2026.10.28a0"></a>
## [v2026.10.28a0](https://github.com/carlkidcrypto/ezsnmp/compare/V2.5.0...v2026.10.28a0) (2026-10-29)

### Changes

#### Bug Fixes
- fix(ci): build macOS wheels and sdist against Net-SNMP 5.10 ([#1445](https://github.com/carlkidcrypto/ezsnmp/issues/1445))

#### Bug Fixes
- [docs-improvement] Fix stale class and test names in HOWTOAI.rst ([#1439](https://github.com/carlkidcrypto/ezsnmp/issues/1439))

#### Cover
- [coverage-autofix] Cover thread_safety full-OID and hex-string formatting paths ([#1415](https://github.com/carlkidcrypto/ezsnmp/issues/1415))

#### Documentation Updates
- docs: fix RST inline literals in README ([#1414](https://github.com/carlkidcrypto/ezsnmp/issues/1414))
- docs: add versioned documentation for V2.5.0 ([#1425](https://github.com/carlkidcrypto/ezsnmp/issues/1425))

#### Features
- feat: standalone Python packages for Linux and repository modernization ([#1388](https://github.com/carlkidcrypto/ezsnmp/issues/1388)) ([#1394](https://github.com/carlkidcrypto/ezsnmp/issues/1394))
- feat(docker): migrate test containers to net-snmp 5.10 and prune legacy versions ([#1396](https://github.com/carlkidcrypto/ezsnmp/issues/1396))
- feat(versioning): adopt SemVer-compliant CalVer versioning scheme ([#1369](https://github.com/carlkidcrypto/ezsnmp/issues/1369)) ([#1393](https://github.com/carlkidcrypto/ezsnmp/issues/1393))

#### Maintenance
- chore: bump version to 2026.10.28a0 ([#1442](https://github.com/carlkidcrypto/ezsnmp/issues/1442))
- chore(deps): bump github/codeql-action/init from 4.38.3 to 4.39.0 ([#1417](https://github.com/carlkidcrypto/ezsnmp/issues/1417))
- chore(deps): bump github/codeql-action/analyze from 4.38.3 to 4.39.1 ([#1419](https://github.com/carlkidcrypto/ezsnmp/issues/1419))
- chore(deps): bump setuptools from 84.0.0 to 84.1.0 ([#1438](https://github.com/carlkidcrypto/ezsnmp/issues/1438))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1416](https://github.com/carlkidcrypto/ezsnmp/issues/1416))
- chore(deps): bump the python-dependencies group across 1 directory with 3 updates ([#1429](https://github.com/carlkidcrypto/ezsnmp/issues/1429))
- chore(docker): update Python patch versions in Dockerfiles ([#1423](https://github.com/carlkidcrypto/ezsnmp/issues/1423))
- chore: update Homebrew formula for V2.5.0 ([#1424](https://github.com/carlkidcrypto/ezsnmp/issues/1424))
- chore(docs): update changelog ([#1426](https://github.com/carlkidcrypto/ezsnmp/issues/1426))

#### Performance Improvements
- perf(tests): deduplicate C++ test objects and cache Docker test wheels (3/3) ([#1422](https://github.com/carlkidcrypto/ezsnmp/issues/1422))
- perf(ci): parallelize linux wheel matrix and cache cibuildwheel builds (2/3) ([#1421](https://github.com/carlkidcrypto/ezsnmp/issues/1421))
- perf(build): deduplicate and parallelize C++ extension compilation (1/3) ([#1420](https://github.com/carlkidcrypto/ezsnmp/issues/1420))

#### Provide
- Provide authenticated GitHub CLI access to release notes workflow ([#1428](https://github.com/carlkidcrypto/ezsnmp/issues/1428))

#### Styles
- style: auto-format with clang-format ([#1433](https://github.com/carlkidcrypto/ezsnmp/issues/1433))

#### Tests
- test: cover SessionBase print_hex_strings setter/getter ([#1441](https://github.com/carlkidcrypto/ezsnmp/issues/1441))
- test: cover Session.walk error path ([#1440](https://github.com/carlkidcrypto/ezsnmp/issues/1440))

---

<a name="V2.5.0"></a>
## [V2.5.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.5.0b0...V2.5.0) (2026-10-23)

### Changes

#### Bug Fixes
- fix(aw): ignore restored inline skills and restrict staging in coverage autofix cpp ([#1410](https://github.com/carlkidcrypto/ezsnmp/issues/1410))
- fix(aw): allow all tools and add go network preset for auto change log ([#1409](https://github.com/carlkidcrypto/ezsnmp/issues/1409))
- fix(aw): configure min-integrity none for triage incoming bug reports ([#1403](https://github.com/carlkidcrypto/ezsnmp/issues/1403))

#### Documentation Updates
- docs: add versioned documentation for v2.5.0b0 ([#1406](https://github.com/carlkidcrypto/ezsnmp/issues/1406))

#### Features
- feat(skills): add modular github copilot skills for ezsnmp ([#1412](https://github.com/carlkidcrypto/ezsnmp/issues/1412))

#### Improve
- Improve exception docstrings ([#1401](https://github.com/carlkidcrypto/ezsnmp/issues/1401))

#### Maintenance
- chore: bump version to 2.5.0 ([#1411](https://github.com/carlkidcrypto/ezsnmp/issues/1411))
- chore(sonar): exclude docs from sonarqube analysis and duplication checks ([#1408](https://github.com/carlkidcrypto/ezsnmp/issues/1408))
- chore: update Homebrew formula for v2.5.0b0 ([#1405](https://github.com/carlkidcrypto/ezsnmp/issues/1405))

---

<a name="v2.5.0b0"></a>
## [v2.5.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.5.0a2...v2.5.0b0) (2026-10-18)

### Changes

#### Bug Fixes
- Fix macOS wheel OpenSSL discovery for revisioned Homebrew Net-SNMP ([#1402](https://github.com/carlkidcrypto/ezsnmp/issues/1402))

#### Bug Fixes
- fix(ci): grant network access to GitHub API in update_docker_python_versions ([#1392](https://github.com/carlkidcrypto/ezsnmp/issues/1392))
- fix(codecov): stop C++ coverage from disappearing; give coverage agents line data ([#1387](https://github.com/carlkidcrypto/ezsnmp/issues/1387))

#### Continuous Integration
- ci(docker): hand build cache to matrix jobs via artifact ([#1390](https://github.com/carlkidcrypto/ezsnmp/issues/1390))
- ci: skip heavy CI for gh-aw/agent-tooling-only changes ([#1384](https://github.com/carlkidcrypto/ezsnmp/issues/1384))
- ci(aw): report noop runs to tracking issue and give coverage workflows Codecov data ([#1382](https://github.com/carlkidcrypto/ezsnmp/issues/1382))

#### Documentation Updates
- docs: add versioned documentation for v2.5.0a2 ([#1371](https://github.com/carlkidcrypto/ezsnmp/issues/1371))

#### Eliminate
- Eliminate conflicting SWIG build requirements and prevent dependency drift ([#1389](https://github.com/carlkidcrypto/ezsnmp/issues/1389))

#### Features
- feat: add standardized release_tools for version bumping and verification ([#1397](https://github.com/carlkidcrypto/ezsnmp/issues/1397))
- feat: enhance documentation SEO with metadata, OpenGraph, JSON-LD, and overview ([#1373](https://github.com/carlkidcrypto/ezsnmp/issues/1373))

#### Features
- Add tests for print_hex_strings setter and get_next error path ([#1385](https://github.com/carlkidcrypto/ezsnmp/issues/1385))

#### Maintenance
- chore: bump version to 2.5.0b0 ([#1395](https://github.com/carlkidcrypto/ezsnmp/issues/1395))
- chore(deps): bump actions/download-artifact from 8.0.1 to 8.0.2 ([#1381](https://github.com/carlkidcrypto/ezsnmp/issues/1381))
- chore(deps): bump actions/upload-artifact from 7.0.1 to 7.0.2 ([#1378](https://github.com/carlkidcrypto/ezsnmp/issues/1378))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1377](https://github.com/carlkidcrypto/ezsnmp/issues/1377))
- chore(deps): bump github/codeql-action/analyze from 4.38.2 to 4.38.3 ([#1380](https://github.com/carlkidcrypto/ezsnmp/issues/1380))
- chore(deps): bump github/codeql-action/init from 4.38.2 to 4.38.3 ([#1376](https://github.com/carlkidcrypto/ezsnmp/issues/1376))
- chore(deps): bump EnricoMi/publish-unit-test-result-action ([#1374](https://github.com/carlkidcrypto/ezsnmp/issues/1374))
- chore(deps): bump the python-dependencies group across 1 directory with 4 updates ([#1375](https://github.com/carlkidcrypto/ezsnmp/issues/1375))
- chore(deps): bump carlkidcrypto/os-specific-runner from 2.3.1 to 2.4.0 ([#1379](https://github.com/carlkidcrypto/ezsnmp/issues/1379))
- chore: update Homebrew formula for v2.5.0a2 ([#1370](https://github.com/carlkidcrypto/ezsnmp/issues/1370))

#### Updates & Improvements
- [changelog] Update CHANGELOG.md ([#1372](https://github.com/carlkidcrypto/ezsnmp/issues/1372))

---

<a name="v2.5.0a2"></a>
## [v2.5.0a2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.5.0a1...v2.5.0a2) (2026-10-10)

### Changes

#### Bug Fixes
- fix: revert gh-aw workflow models from gpt-6.1-sol to claude-sonnet-5 ([#1364](https://github.com/carlkidcrypto/ezsnmp/issues/1364))
- fix(ci): invoke pypa/gh-action-pypi-publish directly and extract build-distribution action ([#1341](https://github.com/carlkidcrypto/ezsnmp/issues/1341))
- fix(ci): scope verify_syntax push to main to avoid duplicate concurrent runs on PRs ([#1340](https://github.com/carlkidcrypto/ezsnmp/issues/1340))

#### Code Refactoring
- refactor(ci): extract common build-wheels and publish actions for PyPI/TestPyPI workflows ([#1329](https://github.com/carlkidcrypto/ezsnmp/issues/1329))

#### Documentation Updates
- docs: add versioned documentation for v2.5.0a1 ([#1334](https://github.com/carlkidcrypto/ezsnmp/issues/1334))

#### Features
- feat: use model alias sonnet across all gh-aw workflows ([#1365](https://github.com/carlkidcrypto/ezsnmp/issues/1365))
- feat: Migrate gh-aw workflows from claude-sonnet-5 to gpt-6-sol ([#1357](https://github.com/carlkidcrypto/ezsnmp/issues/1357))

#### Features
- Add unit tests for Session.set() exception-propagation branch ([#1353](https://github.com/carlkidcrypto/ezsnmp/issues/1353))

#### Maintenance
- chore: bump version to 2.5.0a2 ([#1368](https://github.com/carlkidcrypto/ezsnmp/issues/1368))
- chore(deps): bump cibuildwheel ([#1367](https://github.com/carlkidcrypto/ezsnmp/issues/1367))
- chore(deps): update Dependabot schedule to weekly ([#1366](https://github.com/carlkidcrypto/ezsnmp/issues/1366))
- chore(deps): bump the python-dependencies group across 1 directory with 3 updates ([#1363](https://github.com/carlkidcrypto/ezsnmp/issues/1363))
- chore(deps): bump github/codeql-action/analyze from 4.38.1 to 4.38.2 ([#1350](https://github.com/carlkidcrypto/ezsnmp/issues/1350))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1349](https://github.com/carlkidcrypto/ezsnmp/issues/1349))
- chore(deps): bump github/codeql-action/init from 4.38.1 to 4.38.2 ([#1348](https://github.com/carlkidcrypto/ezsnmp/issues/1348))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.12.2 to 1.12.3 ([#1360](https://github.com/carlkidcrypto/ezsnmp/issues/1360))
- chore: update Homebrew formula for v2.5.0a1 ([#1333](https://github.com/carlkidcrypto/ezsnmp/issues/1333))

#### Tests
- test(sessionbase): cover duplicate-port throw for udp6 and bracketed IPv6 hostnames ([#1356](https://github.com/carlkidcrypto/ezsnmp/issues/1356))

---

<a name="v2.5.0a1"></a>
## [v2.5.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.5.0a0...v2.5.0a1) (2026-09-24)

### Changes

#### Bug Fixes
- fix(ci): fix Windows multi-arch wheel builds and OpenSSL discovery ([#1328](https://github.com/carlkidcrypto/ezsnmp/issues/1328))
- [report-tooling] fix: monthly report tooling maintenance & optimize CI triggers for AW files ([#1154](https://github.com/carlkidcrypto/ezsnmp/issues/1154)) ([#1326](https://github.com/carlkidcrypto/ezsnmp/issues/1326))
- fix(aw): restrict allowed-files and consolidate safe outputs in Coverage Autofix C++ ([#1240](https://github.com/carlkidcrypto/ezsnmp/issues/1240)) ([#1325](https://github.com/carlkidcrypto/ezsnmp/issues/1325))
- fix: guard GTEST_SKIP for older GTest in Docker tests & add snmptrap coverage ([#1317](https://github.com/carlkidcrypto/ezsnmp/issues/1317))

#### Bug Fixes
- Fix: Issue 1268 And 1282 ([#1308](https://github.com/carlkidcrypto/ezsnmp/issues/1308))
- [docs-improvement] Fix incorrect file and method name references in docs ([#1294](https://github.com/carlkidcrypto/ezsnmp/issues/1294))

#### Documentation Updates
- docs: add versioned documentation for v2.5.0a0 ([#1292](https://github.com/carlkidcrypto/ezsnmp/issues/1292))

#### Features
- feat: add native Windows support for x86 and ARM64 ([#1255](https://github.com/carlkidcrypto/ezsnmp/issues/1255)) ([#1324](https://github.com/carlkidcrypto/ezsnmp/issues/1324))
- feat(ci): add generate_release_notes helper script to optimize AIC costs ([#1327](https://github.com/carlkidcrypto/ezsnmp/issues/1327))

#### Maintenance
- chore(deps): bump codecov/codecov-action from 7.1.0 to 7.1.1 ([#1315](https://github.com/carlkidcrypto/ezsnmp/issues/1315))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1314](https://github.com/carlkidcrypto/ezsnmp/issues/1314))
- chore(deps): bump github/codeql-action/analyze from 4.38.0 to 4.38.1 ([#1313](https://github.com/carlkidcrypto/ezsnmp/issues/1313))
- chore(deps): bump github/codeql-action/init from 4.38.0 to 4.38.1 ([#1312](https://github.com/carlkidcrypto/ezsnmp/issues/1312))
- chore(deps): bump docker/build-push-action from 7.3.0 to 7.4.0 ([#1302](https://github.com/carlkidcrypto/ezsnmp/issues/1302))
- chore(deps): bump urllib3 in the python-dependencies group ([#1301](https://github.com/carlkidcrypto/ezsnmp/issues/1301))
- chore(deps): bump docker/setup-buildx-action from 4.3.0 to 4.4.0 ([#1300](https://github.com/carlkidcrypto/ezsnmp/issues/1300))
- chore(deps): bump codecov/codecov-action from 7.0.0 to 7.1.0 ([#1299](https://github.com/carlkidcrypto/ezsnmp/issues/1299))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1289](https://github.com/carlkidcrypto/ezsnmp/issues/1289))
- chore(deps): bump github/codeql-action/analyze from 4.37.9 to 4.38.0 ([#1287](https://github.com/carlkidcrypto/ezsnmp/issues/1287))
- chore(deps): bump github/codeql-action/init from 4.37.9 to 4.38.0 ([#1286](https://github.com/carlkidcrypto/ezsnmp/issues/1286))
- chore(deps): bump the python-dependencies group across 1 directory with 2 updates ([#1298](https://github.com/carlkidcrypto/ezsnmp/issues/1298))
- chore(docs): update changelog ([#1293](https://github.com/carlkidcrypto/ezsnmp/issues/1293))

#### Performance Improvements
- perf(session): restore multi-threaded concurrency with fine-grained formatting lock ([#1322](https://github.com/carlkidcrypto/ezsnmp/issues/1322))
- perf(ci): optimize token consumption and add budget caps across all agentic workflows ([#1318](https://github.com/carlkidcrypto/ezsnmp/issues/1318))

---

<a name="v2.5.0a0"></a>
## [v2.5.0a0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.4.0...v2.5.0a0) (2026-09-15)

### Changes

#### Align
- Align Homebrew Python CI and shim tests ([#1284](https://github.com/carlkidcrypto/ezsnmp/issues/1284))

#### Documentation Updates
- docs: fix minor typos and awkward phrasing in docs ([#1280](https://github.com/carlkidcrypto/ezsnmp/issues/1280))
- docs: link HOWTOAI guide from README and clarify builtin-shadowing exceptions ([#1274](https://github.com/carlkidcrypto/ezsnmp/issues/1274))

#### Features
- [coverage-autofix-py] Add unit tests for Session exception and None-normalisation branches ([#1263](https://github.com/carlkidcrypto/ezsnmp/issues/1263))

#### Features
- Feature/update some things ([#1272](https://github.com/carlkidcrypto/ezsnmp/issues/1272))

#### GH
- GH Upgrade and Compile ([#1290](https://github.com/carlkidcrypto/ezsnmp/issues/1290))

#### Maintenance
- chore(docker): update Python patch versions in Dockerfiles ([#1278](https://github.com/carlkidcrypto/ezsnmp/issues/1278))
- chore(deps): bump cibuildwheel in the python-dependencies group ([#1273](https://github.com/carlkidcrypto/ezsnmp/issues/1273))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1271](https://github.com/carlkidcrypto/ezsnmp/issues/1271))
- chore(deps): bump github/codeql-action/analyze from 4.37.8 to 4.37.9 ([#1235](https://github.com/carlkidcrypto/ezsnmp/issues/1235))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1234](https://github.com/carlkidcrypto/ezsnmp/issues/1234))
- chore(deps): bump github/codeql-action/init from 4.37.8 to 4.37.9 ([#1233](https://github.com/carlkidcrypto/ezsnmp/issues/1233))
- chore(deps): bump coverage from 7.15.4 to 7.16.0 ([#1232](https://github.com/carlkidcrypto/ezsnmp/issues/1232))
- chore(deps): bump build from 1.5.1 to 1.6.0 ([#1231](https://github.com/carlkidcrypto/ezsnmp/issues/1231))
- chore(deps-dev): bump swig from 4.4.1 to 4.5.0 ([#1206](https://github.com/carlkidcrypto/ezsnmp/issues/1206))
- chore(deps): bump docker/setup-buildx-action from 4.2.0 to 4.3.0 ([#1198](https://github.com/carlkidcrypto/ezsnmp/issues/1198))
- chore(deps-dev): bump wheel from 0.47.0 to 0.48.0 ([#1178](https://github.com/carlkidcrypto/ezsnmp/issues/1178))
- chore(deps): bump actions/deploy-pages from 5.0.0 to 5.0.1 ([#1248](https://github.com/carlkidcrypto/ezsnmp/issues/1248))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.11.0 to 1.12.2 ([#1249](https://github.com/carlkidcrypto/ezsnmp/issues/1249))
- chore: sync supported Python versions to devguide.python.org ([#1217](https://github.com/carlkidcrypto/ezsnmp/issues/1217))
- chore: update Homebrew formula for v2.4.0 ([#1267](https://github.com/carlkidcrypto/ezsnmp/issues/1267))
- chore(docs): update changelog ([#1269](https://github.com/carlkidcrypto/ezsnmp/issues/1269))

#### Preserve
- Preserve per-session OID formatting across concurrent SNMP operations ([#1279](https://github.com/carlkidcrypto/ezsnmp/issues/1279))

#### Tests
- test(cpp): add coverage for numeric conversion empty/overflow branches ([#1281](https://github.com/carlkidcrypto/ezsnmp/issues/1281))

---

<a name="v2.4.0"></a>
## [v2.4.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.4.0b0...v2.4.0) (2026-09-06)

### Changes

#### Bug Fixes
- fix: align report tooling docs and workflow exit-code handling ([#1253](https://github.com/carlkidcrypto/ezsnmp/issues/1253))

#### Critical Bug Fixes
- Hotfix/fixing windows builds again v2 ([#1258](https://github.com/carlkidcrypto/ezsnmp/issues/1258))
- Hotfix/gh aw updates ([#1251](https://github.com/carlkidcrypto/ezsnmp/issues/1251))

#### Dependency Updates
- Bump 2.4.0 ([#1245](https://github.com/carlkidcrypto/ezsnmp/issues/1245))

#### Documentation Updates
- docs: fix method name typo and broken line-continuation in SWIG example ([#1260](https://github.com/carlkidcrypto/ezsnmp/issues/1260))
- docs: Add feature-grouped Software Requirements document to Sphinx ([#1181](https://github.com/carlkidcrypto/ezsnmp/issues/1181))
- docs: add versioned documentation for v2.4.0b0 ([#1216](https://github.com/carlkidcrypto/ezsnmp/issues/1216))

#### Maintenance
- chore(docs): update changelog ([#1222](https://github.com/carlkidcrypto/ezsnmp/issues/1222))
- chore: update Homebrew formula for v2.4.0b0 ([#1215](https://github.com/carlkidcrypto/ezsnmp/issues/1215))

#### Python-related Changes
- Python Version Watcher ([#1254](https://github.com/carlkidcrypto/ezsnmp/issues/1254))

#### Switch
- Switch to sonnet 5 ([#1252](https://github.com/carlkidcrypto/ezsnmp/issues/1252))

#### Updates & Improvements
- Update action.yml ([#1257](https://github.com/carlkidcrypto/ezsnmp/issues/1257))

#### Windows
- Windows Build Fix ([#1256](https://github.com/carlkidcrypto/ezsnmp/issues/1256))

---

<a name="v2.4.0b0"></a>
## [v2.4.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.4.0a9...v2.4.0b0) (2026-08-24)

### Changes

#### Apply
- [changelog] Apply v2.4.0a9 changelog update from protected-file fallback artifact ([#1113](https://github.com/carlkidcrypto/ezsnmp/issues/1113))

#### Documentation Updates
- docs: improve Session.bulk_get and Session.set docstrings ([#1168](https://github.com/carlkidcrypto/ezsnmp/issues/1168))
- docs: fix duplicate -y flag, double space, and capitalisation in development.rst ([#1152](https://github.com/carlkidcrypto/ezsnmp/issues/1152))
- docs: add -std=c++17 SWIG flag note, clarify get() tuple return, note use_enums semantic reversal ([#1132](https://github.com/carlkidcrypto/ezsnmp/issues/1132))
- docs: clarify bulk_get/bulk_walk v2c/v3 requirement and fix GETBULK terminology ([#1127](https://github.com/carlkidcrypto/ezsnmp/issues/1127))
- docs: fix typos, grammar, and formatting in RST and docstrings ([#1116](https://github.com/carlkidcrypto/ezsnmp/issues/1116))
- docs: add versioned documentation for v2.4.0a9 ([#1111](https://github.com/carlkidcrypto/ezsnmp/issues/1111))

#### Features
- [coverage-autofix-py] Add unit tests for netsnmp and session exception-handling branches ([#1124](https://github.com/carlkidcrypto/ezsnmp/issues/1124))
- Add snmptrap null and stat_error shim tests for coverage ([#1164](https://github.com/carlkidcrypto/ezsnmp/issues/1164))

#### Features
- feat: update coverage autofix workflows to use Codecov polling and hu… ([#1123](https://github.com/carlkidcrypto/ezsnmp/issues/1123))

#### GW
- GW AW ([#1176](https://github.com/carlkidcrypto/ezsnmp/issues/1176))

#### Maintenance
- chore(deps): bump github/codeql-action/analyze from 4.37.6 to 4.37.8 ([#1209](https://github.com/carlkidcrypto/ezsnmp/issues/1209))
- chore(deps): bump github/codeql-action/init from 4.37.6 to 4.37.8 ([#1210](https://github.com/carlkidcrypto/ezsnmp/issues/1210))
- chore(deps): bump actions/setup-python from 6.3.0 to 7.0.0 ([#1134](https://github.com/carlkidcrypto/ezsnmp/issues/1134))
- chore(deps): bump actions/checkout from 7.0.0 to 7.0.1 ([#1135](https://github.com/carlkidcrypto/ezsnmp/issues/1135))
- chore(deps): bump github/codeql-action/init from 4.37.4 to 4.37.6 ([#1165](https://github.com/carlkidcrypto/ezsnmp/issues/1165))
- chore(deps): bump github/codeql-action/analyze from 4.37.4 to 4.37.6 ([#1166](https://github.com/carlkidcrypto/ezsnmp/issues/1166))
- chore(deps): bump coverage from 7.15.3 to 7.15.4 ([#1169](https://github.com/carlkidcrypto/ezsnmp/issues/1169))
- chore(deps): bump cibuildwheel from 4.1.0 to 4.2.0 ([#1170](https://github.com/carlkidcrypto/ezsnmp/issues/1170))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1171](https://github.com/carlkidcrypto/ezsnmp/issues/1171))
- chore(deps-dev): bump setuptools from 83.0.0 to 84.0.0 ([#1172](https://github.com/carlkidcrypto/ezsnmp/issues/1172))
- chore(docker): update Python patch versions in Dockerfiles ([#1167](https://github.com/carlkidcrypto/ezsnmp/issues/1167))
- chore(deps): bump docker/login-action from 4.4.0 to 4.6.0 ([#1149](https://github.com/carlkidcrypto/ezsnmp/issues/1149))
- chore(deps): bump github/codeql-action/init from 4.37.0 to 4.37.4 ([#1155](https://github.com/carlkidcrypto/ezsnmp/issues/1155))
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1156](https://github.com/carlkidcrypto/ezsnmp/issues/1156))
- chore(deps): bump github/codeql-action/analyze from 4.37.0 to 4.37.4 ([#1157](https://github.com/carlkidcrypto/ezsnmp/issues/1157))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.10.0 to 1.11.0 ([#1159](https://github.com/carlkidcrypto/ezsnmp/issues/1159))
- chore(deps): bump coverage from 7.15.0 to 7.15.3 ([#1160](https://github.com/carlkidcrypto/ezsnmp/issues/1160))
- chore(deps): bump build from 1.5.0 to 1.5.1 ([#1099](https://github.com/carlkidcrypto/ezsnmp/issues/1099))
- chore: update Homebrew formula for v2.4.0a9 ([#1110](https://github.com/carlkidcrypto/ezsnmp/issues/1110))

#### Move
- Move integration test results into analysis/ folder with data/ sub-folder for CSVs ([#1114](https://github.com/carlkidcrypto/ezsnmp/issues/1114))

#### Releases
- Release Prep ([#1187](https://github.com/carlkidcrypto/ezsnmp/issues/1187))

#### Serialize
- Serialize SNMPv3 setters and strengthen EngineID regression coverage ([#1117](https://github.com/carlkidcrypto/ezsnmp/issues/1117))

#### Styles
- style: auto-format with clang-format ([#1177](https://github.com/carlkidcrypto/ezsnmp/issues/1177))

#### Tests
- test: add coverage tests for uncovered C++ branches ([#1174](https://github.com/carlkidcrypto/ezsnmp/issues/1174))
- test(cpp): add shim tests for snmp_perror_exception and connection error variants ([#1125](https://github.com/carlkidcrypto/ezsnmp/issues/1125))

#### Updates & Improvements
- Update dependabot.yml ([#1213](https://github.com/carlkidcrypto/ezsnmp/issues/1213))

---

<a name="v2.4.0a9"></a>
## [v2.4.0a9](https://github.com/carlkidcrypto/ezsnmp/compare/v2.4.0a8...v2.4.0a9) (2026-07-12)

### Changes

#### Bug Fixes
- fix: graceful fallback for coverage_autofix_cpp when build tools unavailable ([#1109](https://github.com/carlkidcrypto/ezsnmp/issues/1109))

#### Bug Fixes
- Fix Coverage Autofix Python: run in Docker to get net-snmp libraries ([#1108](https://github.com/carlkidcrypto/ezsnmp/issues/1108))
- Fix macOS Homebrew CI: always build from local source ([#1092](https://github.com/carlkidcrypto/ezsnmp/issues/1092))
- Fix invalid actions/cache SHA in build_and_publish_docker_images.yml ([#1104](https://github.com/carlkidcrypto/ezsnmp/issues/1104))
- Fix: Add copilot-requests permission for Agentic Workflows ([#1091](https://github.com/carlkidcrypto/ezsnmp/issues/1091))
- Fix Session.get/get_next crash on empty OIDs and ensure coverage comments post on test failures ([#1067](https://github.com/carlkidcrypto/ezsnmp/issues/1067))

#### Documentation Updates
- docs: fix RST heading, unify docstring style, clarify param wording ([#1101](https://github.com/carlkidcrypto/ezsnmp/issues/1101))
- docs: add versioned documentation for v2.4.0a8 ([#1070](https://github.com/carlkidcrypto/ezsnmp/issues/1070))

#### Features
- Add `-Ox`-backed hex string output option for OCTET STRING values ([#1100](https://github.com/carlkidcrypto/ezsnmp/issues/1100))

#### Maintenance
- chore(deps): bump Homebrew/actions/setup-homebrew ([#1106](https://github.com/carlkidcrypto/ezsnmp/issues/1106))
- chore(deps): bump github/codeql-action/init from 4.36.3 to 4.37.0 ([#1098](https://github.com/carlkidcrypto/ezsnmp/issues/1098))
- chore(deps): bump github/codeql-action/analyze from 4.36.3 to 4.37.0 ([#1097](https://github.com/carlkidcrypto/ezsnmp/issues/1097))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.8.0 to 1.10.0 ([#1074](https://github.com/carlkidcrypto/ezsnmp/issues/1074))
- chore(deps-dev): bump setuptools from 82.0.1 to 83.0.0 ([#1073](https://github.com/carlkidcrypto/ezsnmp/issues/1073))
- chore(deps): bump actions/cache/save from 5.0.5 to 6.1.0 ([#1055](https://github.com/carlkidcrypto/ezsnmp/issues/1055))
- chore(deps): bump docker/login-action from 4.2.0 to 4.4.0 ([#1054](https://github.com/carlkidcrypto/ezsnmp/issues/1054))
- chore(deps): bump github/codeql-action/init from 4.36.2 to 4.36.3 ([#1037](https://github.com/carlkidcrypto/ezsnmp/issues/1037))
- chore(deps): bump github/codeql-action/analyze from 4.36.2 to 4.36.3 ([#1036](https://github.com/carlkidcrypto/ezsnmp/issues/1036))
- chore(deps): bump docker/setup-buildx-action from 4.1.0 to 4.2.0 ([#1034](https://github.com/carlkidcrypto/ezsnmp/issues/1034))
- chore(deps): bump coverage from 7.14.1 to 7.15.0 ([#1033](https://github.com/carlkidcrypto/ezsnmp/issues/1033))
- chore: update Homebrew formula for v2.4.0a8 ([#1071](https://github.com/carlkidcrypto/ezsnmp/issues/1071))

#### Scope
- Scope Dependabot away from agentic workflow artifacts using path exclusions ([#1105](https://github.com/carlkidcrypto/ezsnmp/issues/1105))

#### Split
- Split test_session.py into focused files; expand Docker CI to 10 test groups ([#1107](https://github.com/carlkidcrypto/ezsnmp/issues/1107))

#### Stabilize
- Stabilize Docker image workflow by serializing tarball cache population ([#1094](https://github.com/carlkidcrypto/ezsnmp/issues/1094))

#### Updates & Improvements
- Update setup.cfg: expand keywords and add Windows platform support ([#1093](https://github.com/carlkidcrypto/ezsnmp/issues/1093))

---

<a name="v2.4.0a8"></a>
## [v2.4.0a8](https://github.com/carlkidcrypto/ezsnmp/compare/2.4.0a7...v2.4.0a8) (2026-07-05)

### Changes

#### Documentation Updates
- docs: add versioned documentation for 2.4.0a7 ([#1061](https://github.com/carlkidcrypto/ezsnmp/issues/1061))

#### Handle
- Handle new macOS runner versions in wheel builds ([#1064](https://github.com/carlkidcrypto/ezsnmp/issues/1064)) inch

#### Maintenance
- chore(deps): bump docker/build-push-action from 7.2.0 to 7.3.0 ([#1032](https://github.com/carlkidcrypto/ezsnmp/issues/1032))
- chore(deps): bump actions/cache/restore from 5.0.5 to 6.1.0 ([#1023](https://github.com/carlkidcrypto/ezsnmp/issues/1023))
- chore(deps): bump actions/cache from 5.0.5 to 6.1.0 ([#1017](https://github.com/carlkidcrypto/ezsnmp/issues/1017))
- chore(deps): bump actions/setup-python from 6.2.0 to 6.3.0 ([#1014](https://github.com/carlkidcrypto/ezsnmp/issues/1014))
- chore(deps): bump pytest from 9.1.0 to 9.1.1 ([#1008](https://github.com/carlkidcrypto/ezsnmp/issues/1008))
- chore: update Homebrew formula for 2.4.0a7 ([#1060](https://github.com/carlkidcrypto/ezsnmp/issues/1060))

#### Styles
- style: auto-format with black ([#1066](https://github.com/carlkidcrypto/ezsnmp/issues/1066))

---

<a name="2.4.0a7"></a>
## [2.4.0a7](https://github.com/carlkidcrypto/ezsnmp/compare/v2.4.0a1...2.4.0a7) (2026-07-03)

### Changes

#### Bug Fixes
- fix(windows): detect OpenSSL lib dir by libcrypto.lib presence; bump version to 2.4.0a7 ([#1053](https://github.com/carlkidcrypto/ezsnmp/issues/1053))
- fix: correct Net-SNMP win32 header copy paths in Windows wheel action ([#1047](https://github.com/carlkidcrypto/ezsnmp/issues/1047))

#### Bug Fixes
- Fix Windows wheel build: patch Net-SNMP snmp_openssl.c for OpenSSL 3.x; bump to 2.4.0a6 ([#1052](https://github.com/carlkidcrypto/ezsnmp/issues/1052))
- Fix Windows wheel build: use 8.3 short paths for OpenSSL; bump version to 2.4.0a5 ([#1051](https://github.com/carlkidcrypto/ezsnmp/issues/1051))
- Fix Windows wheel prep by aligning Net-SNMP artifact copy paths with actual win32 layout ([#1050](https://github.com/carlkidcrypto/ezsnmp/issues/1050))
- Fix Windows wheel build toolchain setup and bump package version to 2.4.0a2 ([#1041](https://github.com/carlkidcrypto/ezsnmp/issues/1041))

#### Continuous Integration
- ci: update all agentic workflows to use claude-sonnet-4.6 ([#1049](https://github.com/carlkidcrypto/ezsnmp/issues/1049))
- ci: implement auto-PR for formatting fixes in black and clang-format … ([#1030](https://github.com/carlkidcrypto/ezsnmp/issues/1030))

#### Documentation Updates
- docs: add versioned documentation for v2.4.0a1 ([#1039](https://github.com/carlkidcrypto/ezsnmp/issues/1039))

#### Maintenance
- chore(docs): update changelog ([#1048](https://github.com/carlkidcrypto/ezsnmp/issues/1048))
- chore: update Homebrew formula for v2.4.0a1 ([#1038](https://github.com/carlkidcrypto/ezsnmp/issues/1038))

#### Styles
- style: auto-format with black ([#1046](https://github.com/carlkidcrypto/ezsnmp/issues/1046))
- style: auto-format with black ([#1045](https://github.com/carlkidcrypto/ezsnmp/issues/1045))
- style: auto-format with black ([#1043](https://github.com/carlkidcrypto/ezsnmp/issues/1043))
- style: auto-format with black ([#1044](https://github.com/carlkidcrypto/ezsnmp/issues/1044))
- style: auto-format with black ([#1042](https://github.com/carlkidcrypto/ezsnmp/issues/1042))

---

<a name="v2.4.0a1"></a>
## [v2.4.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0...v2.4.0a1) (2026-07-01)

### Changes

#### Black
- Black ([#1000](https://github.com/carlkidcrypto/ezsnmp/issues/1000))

#### Bug Fixes
- Fix `Session.get_next` string OID dispatch to prevent character-splitting and invalid OID parsing ([#991](https://github.com/carlkidcrypto/ezsnmp/issues/991))
- Fix ModuleNotFoundError by running pytest from python_tests directory ([#1022](https://github.com/carlkidcrypto/ezsnmp/issues/1022))
- Fix/fixing yaml workflows ([#1021](https://github.com/carlkidcrypto/ezsnmp/issues/1021))
- [docs-improvement] Fix docstrings, typos, and inaccuracies across documentation ([#994](https://github.com/carlkidcrypto/ezsnmp/issues/994))
- Fix failing GitHub Actions job 'Build wheels on windows-latest' ([#999](https://github.com/carlkidcrypto/ezsnmp/issues/999))
- Fix Windows wheel build by recognizing Chocolatey OpenSSL install path ([#998](https://github.com/carlkidcrypto/ezsnmp/issues/998))
- Fix isolated wheel builds failing to import `build_utils` ([#997](https://github.com/carlkidcrypto/ezsnmp/issues/997))

#### Documentation Updates
- docs: fix capitalization, wording, and docstring clarity ([#1026](https://github.com/carlkidcrypto/ezsnmp/issues/1026))
- docs: fix typos, image URLs, and code block language ([#1019](https://github.com/carlkidcrypto/ezsnmp/issues/1019))
- docs: fix example bugs, typos, and improve Session docstring ([#1015](https://github.com/carlkidcrypto/ezsnmp/issues/1015))
- docs: fix C++ test commands, missing headers, docstring style, and get() tuple note ([#1009](https://github.com/carlkidcrypto/ezsnmp/issues/1009))
- docs: fix typos, grammar, and link issues across documentation ([#1006](https://github.com/carlkidcrypto/ezsnmp/issues/1006))
- docs: fix type annotations, net-snmp version, and parameter table ([#987](https://github.com/carlkidcrypto/ezsnmp/issues/987))
- docs: add versioned documentation for v2.3.0

#### Features
- Add build_utils.py: extract build helpers from setup.py for cleaner test imports ([#992](https://github.com/carlkidcrypto/ezsnmp/issues/992))

#### Fedora
- Fedora 42 ([#982](https://github.com/carlkidcrypto/ezsnmp/issues/982))

#### Harden
- Harden Docker cache download for OpenSSL 1.0.2u in CI ([#976](https://github.com/carlkidcrypto/ezsnmp/issues/976))

#### Maintenance
- chore(deps): bump actions/cache/save from 5.0.5 to 6.1.0 ([#1024](https://github.com/carlkidcrypto/ezsnmp/issues/1024))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.7.2 to 1.8.0 ([#1025](https://github.com/carlkidcrypto/ezsnmp/issues/1025))
- chore(deps): bump carlkidcrypto/os-specific-runner from 2.3.0 to 2.3.1 ([#1011](https://github.com/carlkidcrypto/ezsnmp/issues/1011))
- chore(deps): bump actions/checkout from 6 to 7 ([#1005](https://github.com/carlkidcrypto/ezsnmp/issues/1005))
- chore(deps): bump pytest from 9.0.3 to 9.1.0 ([#1001](https://github.com/carlkidcrypto/ezsnmp/issues/1001))
- chore(deps): bump EnricoMi/publish-unit-test-result-action ([#1002](https://github.com/carlkidcrypto/ezsnmp/issues/1002))
- chore(deps): bump cibuildwheel from 4.0.0 to 4.1.0 ([#993](https://github.com/carlkidcrypto/ezsnmp/issues/993))
- chore(docker): update Python patch versions in Dockerfiles ([#996](https://github.com/carlkidcrypto/ezsnmp/issues/996))
- chore(deps): bump cibuildwheel from 3.4.1 to 4.0.0 ([#983](https://github.com/carlkidcrypto/ezsnmp/issues/983))
- chore(deps): bump codecov/codecov-action from 6.0.1 to 7.0.0 ([#984](https://github.com/carlkidcrypto/ezsnmp/issues/984))
- chore: update Homebrew formula for v2.3.0

#### Merged Pull Requests
- Merge branch 'main' into docs/add-versioned-docs-v2.3.0

#### Sphinx
- Sphinx ([#981](https://github.com/carlkidcrypto/ezsnmp/issues/981))

#### Split
- Split coverage autofix workflow into separate Python and C++ focused … ([#1018](https://github.com/carlkidcrypto/ezsnmp/issues/1018))

#### Updates & Improvements
- Update dependabot.yml ([#986](https://github.com/carlkidcrypto/ezsnmp/issues/986))
- [changelog] Update CHANGELOG.md ([#979](https://github.com/carlkidcrypto/ezsnmp/issues/979))

### Merged Pull Requests
- Merge pull request [#978](https://github.com/carlkidcrypto/ezsnmp/issues/978) from carlkidcrypto/docs/add-versioned-docs-v2.3.0
- Merge pull request [#977](https://github.com/carlkidcrypto/ezsnmp/issues/977) from carlkidcrypto/chore/update-homebrew-formula-v2.3.0

---

<a name="v2.3.0"></a>
## [v2.3.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0b0...v2.3.0) (2026-06-06)

### Changes

#### Bug Fixes
- fix: snmpv3 usmStatsNotInTimeWindows  ([#526](https://github.com/carlkidcrypto/ezsnmp/issues/526))
- fix: allow pypi.org in auto_release_notes agentic workflow firewall ([#915](https://github.com/carlkidcrypto/ezsnmp/issues/915))
- fix: change agentic workflow model from gpt-4o to claude-sonnet-4.6 ([#913](https://github.com/carlkidcrypto/ezsnmp/issues/913))
- fix: use explicit gpt-4o model in all agentic workflows (Copilot Pro compatibility) ([#912](https://github.com/carlkidcrypto/ezsnmp/issues/912))

#### Docker
- Docker ([#975](https://github.com/carlkidcrypto/ezsnmp/issues/975))

#### Documentation Updates
- docs: fix typos, grammar, and docstring improvements ([#974](https://github.com/carlkidcrypto/ezsnmp/issues/974))
- docs: add versioned documentation for v2.3.0b0

#### Features
- [coverage-autofix] Add missing test coverage for snmpgetnext, property setters, and None oids paths ([#916](https://github.com/carlkidcrypto/ezsnmp/issues/916))

#### Features
- feat: add additional_context input to auto_release_notes workflow ([#918](https://github.com/carlkidcrypto/ezsnmp/issues/918))

#### Maintenance
- chore(docker): update Python patch versions in Dockerfiles ([#972](https://github.com/carlkidcrypto/ezsnmp/issues/972))
- chore(deps): bump github/gh-aw-actions from 0.77.5 to 0.78.2 ([#971](https://github.com/carlkidcrypto/ezsnmp/issues/971))
- chore(deps): bump coverage from 7.14.0 to 7.14.1 ([#957](https://github.com/carlkidcrypto/ezsnmp/issues/957))
- chore(deps): bump docker/login-action from 4.1.0 to 4.2.0 ([#953](https://github.com/carlkidcrypto/ezsnmp/issues/953))
- chore(deps): bump docker/setup-buildx-action from 4.0.0 to 4.1.0 ([#952](https://github.com/carlkidcrypto/ezsnmp/issues/952))
- chore(deps): bump docker/build-push-action from 7.1.0 to 7.2.0 ([#948](https://github.com/carlkidcrypto/ezsnmp/issues/948))
- chore(deps): bump codecov/codecov-action from 6.0.0 to 6.0.1 ([#944](https://github.com/carlkidcrypto/ezsnmp/issues/944))
- chore(deps): bump black from 26.3.1 to 26.5.1 ([#943](https://github.com/carlkidcrypto/ezsnmp/issues/943))
- chore(deps): bump psf/black from 26.3.1 to 26.5.1 ([#942](https://github.com/carlkidcrypto/ezsnmp/issues/942))
- chore: update models to claude-sonnet-4.6 and recompile AW ([#967](https://github.com/carlkidcrypto/ezsnmp/issues/967))
- chore(deps): bump github/codeql-action from 4.35.4 to 4.36.2 ([#965](https://github.com/carlkidcrypto/ezsnmp/issues/965))
- chore(deps): bump github/gh-aw-actions from 0.74.1 to 0.78.2 ([#966](https://github.com/carlkidcrypto/ezsnmp/issues/966))
- chore(deps): bump github/codeql-action from 4.35.2 to 4.35.4 ([#925](https://github.com/carlkidcrypto/ezsnmp/issues/925))
- chore(deps): bump urllib3 from 2.6.3 to 2.7.0 ([#924](https://github.com/carlkidcrypto/ezsnmp/issues/924))
- chore(deps): bump coverage from 7.13.5 to 7.14.0 ([#930](https://github.com/carlkidcrypto/ezsnmp/issues/930))
- chore(deps): bump github/gh-aw-actions from 0.71.1 to 0.74.1 ([#932](https://github.com/carlkidcrypto/ezsnmp/issues/932))
- chore: update Homebrew formula for v2.3.0b0

#### Merged Pull Requests
- Merge branch 'main' into docs/add-versioned-docs-v2.3.0b0
- Merge branch 'main' into chore/update-homebrew-formula-v2.3.0b0

#### Regenerate
- Regenerate all agentic workflow lock files ([#914](https://github.com/carlkidcrypto/ezsnmp/issues/914))

### Merged Pull Requests
- Merge pull request [#910](https://github.com/carlkidcrypto/ezsnmp/issues/910) from carlkidcrypto/docs/add-versioned-docs-v2.3.0b0
- Merge pull request [#909](https://github.com/carlkidcrypto/ezsnmp/issues/909) from carlkidcrypto/chore/update-homebrew-formula-v2.3.0b0

---

<a name="v2.3.0b0"></a>
## [v2.3.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0a2...v2.3.0b0) (2026-05-03)

### Changes

#### Bug Fixes
- Fix agentic workflows: replace inaccessible `gpt-5.3-codex` model with `auto` ([#908](https://github.com/carlkidcrypto/ezsnmp/issues/908))
- Fix configuration for Coverage Autofix every 3 days ([#899](https://github.com/carlkidcrypto/ezsnmp/issues/899))
- [docs-improvement] Fix incorrect Quick Start examples and deprecated build command ([#863](https://github.com/carlkidcrypto/ezsnmp/issues/863))

#### Bug Fixes
- fix: recompile agentic workflow lock files to resolve copilot_driver.cjs missing module error ([#896](https://github.com/carlkidcrypto/ezsnmp/issues/896))
- fix: free outer char** array in Deleter to eliminate create_argv memory leak ([#887](https://github.com/carlkidcrypto/ezsnmp/issues/887))
- fix(workflow): configure base-branch for Update Changelog safe-outputs ([#879](https://github.com/carlkidcrypto/ezsnmp/issues/879))

#### Bump
- bump version from 2.3.0a2 to 2.3.0b0 ([#894](https://github.com/carlkidcrypto/ezsnmp/issues/894))

#### Coverage
- [coverage-autofix] coverage: add C++ and Python tests for snmptrap (zero-coverage gap) ([#872](https://github.com/carlkidcrypto/ezsnmp/issues/872))

#### Documentation Updates
- docs: add versioned documentation for v2.3.0a2

#### Features
- feat: add Python Version Watcher agentic workflow ([#906](https://github.com/carlkidcrypto/ezsnmp/issues/906))

#### Maintenance
- chore(deps): bump github/gh-aw-actions from 0.71.1 to 0.71.3 ([#893](https://github.com/carlkidcrypto/ezsnmp/issues/893))
- chore(deps): bump build from 1.4.4 to 1.5.0 ([#892](https://github.com/carlkidcrypto/ezsnmp/issues/892))
- chore(deps): bump github/gh-aw-actions from 0.70.0 to 0.71.1 ([#882](https://github.com/carlkidcrypto/ezsnmp/issues/882))
- chore(deps): bump carlkidcrypto/os-specific-runner from 2.2.0 to 2.3.0 ([#883](https://github.com/carlkidcrypto/ezsnmp/issues/883))
- chore(deps): bump github/gh-aw-actions from 0.69.3 to 0.70.0 ([#880](https://github.com/carlkidcrypto/ezsnmp/issues/880))
- chore: update Homebrew formula for v2.3.0a2

#### Merged Pull Requests
- Merge branch 'main' into docs/add-versioned-docs-v2.3.0a2

#### Tests
- [coverage-autofix] tests: add branch coverage for Session.__del__ and to_dict() edge cases ([#885](https://github.com/carlkidcrypto/ezsnmp/issues/885))

### Merged Pull Requests
- Merge pull request [#875](https://github.com/carlkidcrypto/ezsnmp/issues/875) from carlkidcrypto/docs/add-versioned-docs-v2.3.0a2
- Merge pull request [#876](https://github.com/carlkidcrypto/ezsnmp/issues/876) from carlkidcrypto/chore/update-homebrew-formula-v2.3.0a2

---

<a name="v2.3.0a2"></a>
## [v2.3.0a2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0a1...v2.3.0a2) (2026-04-22)

### Changes

#### Bug Fixes
- fix: use correct ENTRY_SCRIPT path /usr/local/bin/DockerEntry.sh in docker python tests workflow ([#865](https://github.com/carlkidcrypto/ezsnmp/issues/865))
- fix: use Net-SNMP single-session API to eliminate multi-thread SEGFAULT ([#860](https://github.com/carlkidcrypto/ezsnmp/issues/860))
- fix: handle push_to_pull_request_branch tool failures gracefully in sync workflow ([#856](https://github.com/carlkidcrypto/ezsnmp/issues/856))

#### Bug Fixes
- Fix pypi workflow warnings: skip selectors, deprecated inputs, brew stderr ([#855](https://github.com/carlkidcrypto/ezsnmp/issues/855))

#### Documentation Updates
- [docs-improvement] docs: fix Session version examples and duplicate dev guide example ([#854](https://github.com/carlkidcrypto/ezsnmp/issues/854))
- docs: fix outdated Docker distro list and modernize build commands ([#847](https://github.com/carlkidcrypto/ezsnmp/issues/847))
- docs: add versioned documentation for v2.3.0a1

#### Maintenance
- chore(deps): bump pytest-timeout from 2.3.1 to 2.4.0 ([#866](https://github.com/carlkidcrypto/ezsnmp/issues/866))
- chore(deps): bump tj-actions/changed-files from 47.0.5 to 47.0.6 ([#868](https://github.com/carlkidcrypto/ezsnmp/issues/868))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.7.1 to 1.7.2 ([#869](https://github.com/carlkidcrypto/ezsnmp/issues/869))
- chore(deps): bump github/gh-aw-actions from 0.68.2 to 0.69.3 ([#871](https://github.com/carlkidcrypto/ezsnmp/issues/871))
- chore(deps-dev): bump wheel from 0.46.3 to 0.47.0 ([#873](https://github.com/carlkidcrypto/ezsnmp/issues/873))
- chore(deps): bump build from 1.4.3 to 1.4.4 ([#874](https://github.com/carlkidcrypto/ezsnmp/issues/874))
- chore: bump version from 2.3.0a1 to 2.3.0a2 ([#870](https://github.com/carlkidcrypto/ezsnmp/issues/870))
- chore(deps): bump github/gh-aw-actions from 0.68.1 to 0.68.2 ([#849](https://github.com/carlkidcrypto/ezsnmp/issues/849))
- chore: remove tox, run pytest directly ([#858](https://github.com/carlkidcrypto/ezsnmp/issues/858))
- chore(deps): bump actions/cache from 5.0.4 to 5.0.5 ([#848](https://github.com/carlkidcrypto/ezsnmp/issues/848))
- chore(deps): bump github/codeql-action from 4.35.1 to 4.35.2 ([#853](https://github.com/carlkidcrypto/ezsnmp/issues/853))
- chore(deps): bump chuhlomin/render-template from 1.10 to 1.12 ([#861](https://github.com/carlkidcrypto/ezsnmp/issues/861))
- chore(docker): update Python patch versions in Dockerfiles ([#862](https://github.com/carlkidcrypto/ezsnmp/issues/862))
- chore: remove duplicate homebrew/ezsnmp.rb formula ([#846](https://github.com/carlkidcrypto/ezsnmp/issues/846))
- chore(docs): update changelog ([#845](https://github.com/carlkidcrypto/ezsnmp/issues/845))
- chore: update Homebrew formula for v2.3.0a1

#### Merged Pull Requests
- Merge branch 'main' into chore/update-homebrew-formula-v2.3.0a1

#### Tests
- test(cpp): add shim test for snmp_single_sess_perror_exception ([#864](https://github.com/carlkidcrypto/ezsnmp/issues/864))

### Merged Pull Requests
- Merge pull request [#844](https://github.com/carlkidcrypto/ezsnmp/issues/844) from carlkidcrypto/chore/update-homebrew-formula-v2.3.0a1
- Merge pull request [#843](https://github.com/carlkidcrypto/ezsnmp/issues/843) from carlkidcrypto/docs/add-versioned-docs-v2.3.0a1

---

<a name="v2.3.0a1"></a>
## [v2.3.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0a0...v2.3.0a1) (2026-04-12)

### Changes

#### Bug Fixes
- fix(aw): call noop explicitly when no PRs need syncing ([#839](https://github.com/carlkidcrypto/ezsnmp/issues/839))
- fix: recompile all agentic workflows to gh-aw v0.68.1 to fix missing safe-output tools ([#840](https://github.com/carlkidcrypto/ezsnmp/issues/840))
- fix: explicitly call `noop` safe output tool when no Net-SNMP updates are needed ([#838](https://github.com/carlkidcrypto/ezsnmp/issues/838))

#### Bug Fixes
- Fix attribute names, broken link, grammar, and formatting ([#825](https://github.com/carlkidcrypto/ezsnmp/issues/825))

#### Continuous Integration
- ci: cache pip downloads and tox envs to eliminate cold-cache overhead in Docker test runs ([#834](https://github.com/carlkidcrypto/ezsnmp/issues/834))

#### Documentation Updates
- docs: add versioned documentation for v2.3.0a0

#### Features
- Add NOSUCHNAME shim test for snmpbulkget coverage gap ([#827](https://github.com/carlkidcrypto/ezsnmp/issues/827))

#### Features
- feat: make all PR workflow comments collapsible ([#816](https://github.com/carlkidcrypto/ezsnmp/issues/816))
- feat: add Homebrew formula deploy workflow ([#826](https://github.com/carlkidcrypto/ezsnmp/issues/826))

#### Maintenance
- chore: bump version from 2.3.0a0 to 2.3.0a1 ([#842](https://github.com/carlkidcrypto/ezsnmp/issues/842))
- chore(deps): bump tox from 4.52.0 to 4.52.1 ([#822](https://github.com/carlkidcrypto/ezsnmp/issues/822))
- chore(deps): bump peter-evans/create-pull-request from 8.1.0 to 8.1.1 ([#828](https://github.com/carlkidcrypto/ezsnmp/issues/828))
- chore(deps): bump build from 1.4.2 to 1.4.3 ([#829](https://github.com/carlkidcrypto/ezsnmp/issues/829))
- chore(deps): bump actions/upload-artifact from 7.0.0 to 7.0.1 ([#831](https://github.com/carlkidcrypto/ezsnmp/issues/831))
- chore(deps): bump actions/upload-pages-artifact from 4.0.0 to 5.0.0 ([#832](https://github.com/carlkidcrypto/ezsnmp/issues/832))
- chore(deps): bump actions/github-script from 8.0.0 to 9.0.0 ([#823](https://github.com/carlkidcrypto/ezsnmp/issues/823))
- chore(deps): bump docker/build-push-action from 7.0.0 to 7.1.0 ([#833](https://github.com/carlkidcrypto/ezsnmp/issues/833))
- chore(deps): bump github/gh-aw-actions from 0.67.3 to 0.68.1 ([#830](https://github.com/carlkidcrypto/ezsnmp/issues/830))
- chore(docs): update CHANGELOG.md for v2.3.0a0 release ([#821](https://github.com/carlkidcrypto/ezsnmp/issues/821))
- chore(deps): bump pytest from 9.0.2 to 9.0.3 ([#811](https://github.com/carlkidcrypto/ezsnmp/issues/811))
- chore(deps): bump pypa/gh-action-pypi-publish[@release](https://github.com/release)/v1.13 ([#812](https://github.com/carlkidcrypto/ezsnmp/issues/812))
- chore(deps): bump github/gh-aw-actions from 0.67.2 to 0.67.3 ([#818](https://github.com/carlkidcrypto/ezsnmp/issues/818))

### Merged Pull Requests
- Merge pull request [#819](https://github.com/carlkidcrypto/ezsnmp/issues/819) from carlkidcrypto/docs/add-versioned-docs-v2.3.0a0

---

<a name="v2.3.0a0"></a>
## [v2.3.0a0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0...v2.3.0a0) (2026-04-08)

### Changes

#### Address
- Address Gemini AI review comments on PR [#776](https://github.com/carlkidcrypto/ezsnmp/issues/776)

#### Bug Fixes
- fix(docker/fedora41): strip -L/-I prefix from net-snmp-config libdir/includedir ([#813](https://github.com/carlkidcrypto/ezsnmp/issues/813))
- fix: Preserve multi-line string values in SNMP parse_result (TDD)

#### Documentation Updates
- docs: fix Python 2 print syntax and incorrect property type annotations ([#803](https://github.com/carlkidcrypto/ezsnmp/issues/803))
- docs: fix typos, improve docstrings, and update http links to https ([#795](https://github.com/carlkidcrypto/ezsnmp/issues/795))
- docs: fix typos, grammar, and clarify docstrings
- docs: fix typos, broken examples, and inaccurate framework reference
- docs: add versioned documentation for v2.2.0

#### Drop
- Drop macOS x86_64 wheels from PyPI/TestPyPI builds ([#761](https://github.com/carlkidcrypto/ezsnmp/issues/761))
- Drop macOS x86_64 wheels from PyPI/TestPyPI builds ([#808](https://github.com/carlkidcrypto/ezsnmp/issues/808))
- Drop Net-SNMP 5.6.x support ([#719](https://github.com/carlkidcrypto/ezsnmp/issues/719))

#### Features
- Add Docker images badge and make all badges uniform with flat-square style ([#814](https://github.com/carlkidcrypto/ezsnmp/issues/814))
- Add Homebrew formula so `brew install ezsnmp` works with Homebrew Python (3.10–3.14) ([#718](https://github.com/carlkidcrypto/ezsnmp/issues/718))
- [Docker] Add Fedora 41 containers for net-snmp 5.7, 5.8, and 5.9 ([#734](https://github.com/carlkidcrypto/ezsnmp/issues/734))
- Add net-snmp v5.10.pre2 support ([#720](https://github.com/carlkidcrypto/ezsnmp/issues/720))
- Add Valgrind PR history analysis and workflow
- Add Valgrind PR history analysis and workflow

#### Improve
- Improve changelog and release note workflows

#### Maintenance
- chore: bump version from 2.2.0 to 2.3.0a0 ([#817](https://github.com/carlkidcrypto/ezsnmp/issues/817))
- chore(deps): bump cibuildwheel from 3.4.0 to 3.4.1 ([#799](https://github.com/carlkidcrypto/ezsnmp/issues/799))
- chore(deps): bump docker/login-action from 4.0.0 to 4.1.0 ([#801](https://github.com/carlkidcrypto/ezsnmp/issues/801))
- chore(deps): bump github/gh-aw-actions from 0.65.4 to 0.67.2 ([#807](https://github.com/carlkidcrypto/ezsnmp/issues/807))
- chore(deps): bump tox from 4.51.0 to 4.52.0 ([#791](https://github.com/carlkidcrypto/ezsnmp/issues/791))
- chore(deps): bump github/gh-aw-actions from 0.64.2 to 0.65.4 ([#797](https://github.com/carlkidcrypto/ezsnmp/issues/797))
- chore(deps): bump codecov/codecov-action from 5.5.3 to 6.0.0 ([#781](https://github.com/carlkidcrypto/ezsnmp/issues/781))
- chore(deps): bump tox from 4.50.3 to 4.51.0
- chore(deps): bump github/codeql-action from 4.34.1 to 4.35.1
- chore(deps): bump github/gh-aw-actions from 0.64.0 to 0.64.2
- chore(docker): update Net-SNMP patch versions in Docker assets
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.7.0 to 1.7.1
- chore(deps): bump coverage from 7.13.4 to 7.13.5
- chore(deps): bump actions/cache from 5.0.3 to 5.0.4
- chore(deps): bump codecov/codecov-action from 5.5.2 to 5.5.3
- chore(deps): bump tox from 4.49.1 to 4.50.3
- chore(docs): update changelog
- chore(deps): bump github/codeql-action from 4.32.6 to 4.34.1 ([#747](https://github.com/carlkidcrypto/ezsnmp/issues/747))
- chore(deps): bump pytest-cov from 7.0.0 to 7.1.0 ([#765](https://github.com/carlkidcrypto/ezsnmp/issues/765))
- chore(deps): bump github/gh-aw-actions from 0.62.5 to 0.64.0 ([#772](https://github.com/carlkidcrypto/ezsnmp/issues/772))
- chore(deps): bump tomli from 2.4.0 to 2.4.1 ([#773](https://github.com/carlkidcrypto/ezsnmp/issues/773))
- chore(deps): bump actions/deploy-pages from 4.0.5 to 5.0.0 ([#774](https://github.com/carlkidcrypto/ezsnmp/issues/774))
- chore(deps): bump build from 1.4.0 to 1.4.2 ([#775](https://github.com/carlkidcrypto/ezsnmp/issues/775))

#### Remove
- Remove dead method overloads and fix mutable defaults in session.py ([#815](https://github.com/carlkidcrypto/ezsnmp/issues/815))

#### Tests
- [coverage-autofix] tests: add unit-level session and snmptrap coverage ([#787](https://github.com/carlkidcrypto/ezsnmp/issues/787))

#### Tests
- test(exceptions): add direct coverage for _handle_error() all branches

### Merged Pull Requests
- Merge pull request [#778](https://github.com/carlkidcrypto/ezsnmp/issues/778) from carlkidcrypto/docs/add-versioned-docs-v2.2.0

---

<a name="v2.2.0"></a>
## [v2.2.0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0b1...v2.2.0) (2026-03-25)

### Changes

#### Bug Fixes
- fix: sphinx_build workflow to create PR instead of pushing directly to main ([#762](https://github.com/carlkidcrypto/ezsnmp/issues/762))

#### Features
- Add Auto Release Notes workflow; update changelog ([#766](https://github.com/carlkidcrypto/ezsnmp/issues/766))

#### Features
- Feature/gh aw 3 ([#763](https://github.com/carlkidcrypto/ezsnmp/issues/763))

#### Maintenance
- chore(docs): update changelog ([#764](https://github.com/carlkidcrypto/ezsnmp/issues/764))
- chore: update CHANGELOG.md

#### Releases
- Release/prep for v2.2.0 ([#767](https://github.com/carlkidcrypto/ezsnmp/issues/767))

### Merged Pull Requests
- Merge pull request [#759](https://github.com/carlkidcrypto/ezsnmp/issues/759) from carlkidcrypto/update-changelog-23409474942

---

<a name="v2.2.0b1"></a>
## [v2.2.0b1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0b0...v2.2.0b1) (2026-03-22)

### Changes

#### Bug Fixes
- Fix 3 concurrency bugs causing CI timeouts: spin-wait livelock, O(N²) mutex contention, flag read race ([#740](https://github.com/carlkidcrypto/ezsnmp/issues/740))

#### Bug Fixes
- fix: use GitHub API (api.github.com) instead of www.python.org for CPython version lookup ([#753](https://github.com/carlkidcrypto/ezsnmp/issues/753))
- fix(ci): avoid duplicate changelog PR on release ([#731](https://github.com/carlkidcrypto/ezsnmp/issues/731))

#### Docker
- Docker: Fix Cpp Tests in Workflow ([#732](https://github.com/carlkidcrypto/ezsnmp/issues/732))

#### Documentation Updates
- docs: fix typos, grammar, incorrect API examples, and vague docstrings ([#756](https://github.com/carlkidcrypto/ezsnmp/issues/756))

#### Features
- Add docs CI workflows and update bug template ([#755](https://github.com/carlkidcrypto/ezsnmp/issues/755))
- Add Docker Hub → GHCR fallback in workflows and shell scripts ([#749](https://github.com/carlkidcrypto/ezsnmp/issues/749))

#### Features
- Feature/gh aw ([#750](https://github.com/carlkidcrypto/ezsnmp/issues/750))
- Feature/v2.2.0b1 release prep ([#737](https://github.com/carlkidcrypto/ezsnmp/issues/737))
- Feature/docker auto update py vers ([#729](https://github.com/carlkidcrypto/ezsnmp/issues/729))

#### Features
- feat(cpp_tests): add shim tests targeting uncovered lines in net-snmp… ([#730](https://github.com/carlkidcrypto/ezsnmp/issues/730))

#### Maintenance
- chore(docker): update Python patch versions in Dockerfiles ([#754](https://github.com/carlkidcrypto/ezsnmp/issues/754))
- chore(deps): bump tox from 4.49.0 to 4.49.1 ([#716](https://github.com/carlkidcrypto/ezsnmp/issues/716))
- chore(deps-dev): bump setuptools from 82.0.0 to 82.0.1 ([#715](https://github.com/carlkidcrypto/ezsnmp/issues/715))
- chore(deps): bump actions/download-artifact from 8.0.0 to 8.0.1 ([#721](https://github.com/carlkidcrypto/ezsnmp/issues/721))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.6.0 to 1.7.0 ([#728](https://github.com/carlkidcrypto/ezsnmp/issues/728))
- chore(deps): bump black in the pip group across 1 directory ([#724](https://github.com/carlkidcrypto/ezsnmp/issues/724))
- chore(deps): bump psf/black from 26.3.0 to 26.3.1 ([#725](https://github.com/carlkidcrypto/ezsnmp/issues/725))
- chore: update CHANGELOG.md
- chore: update CHANGELOG.md

#### Merged Pull Requests
- Merge branch 'main' into update-changelog-23069856902
- Merge branch 'main' into update-changelog-23069856913

#### Rewrite
- Rewrite sphinx_build.yml to match os-specific-runner reference workflow ([#744](https://github.com/carlkidcrypto/ezsnmp/issues/744))

### Merged Pull Requests
- Merge pull request [#727](https://github.com/carlkidcrypto/ezsnmp/issues/727) from carlkidcrypto/update-changelog-23069856902
- Merge pull request [#726](https://github.com/carlkidcrypto/ezsnmp/issues/726) from carlkidcrypto/update-changelog-23069856913

---

<a name="v2.2.0b0"></a>
## [v2.2.0b0](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0a2...v2.2.0b0) (2026-03-13)

### Changes

#### Bug Fixes
- Fix NULL dereference in snmpwalk/snmpbulkwalk early-call helper + add missing shim tests + bump to v2.2.0b0  ([#722](https://github.com/carlkidcrypto/ezsnmp/issues/722))

#### Common
- Common Snmpd Conf ([#658](https://github.com/carlkidcrypto/ezsnmp/issues/658))

#### Features
- Add NULL-response shim tests for all SNMP ops + fix Python coverage reporting ([#710](https://github.com/carlkidcrypto/ezsnmp/issues/710))

#### Maintenance
- chore: update CHANGELOG.md
- chore: update CHANGELOG.md

#### Merged Pull Requests
- Merge branch 'main' into update-changelog-22826428091

### Merged Pull Requests
- Merge pull request [#709](https://github.com/carlkidcrypto/ezsnmp/issues/709) from carlkidcrypto/update-changelog-22826428091
- Merge pull request [#708](https://github.com/carlkidcrypto/ezsnmp/issues/708) from carlkidcrypto/update-changelog-22826428081

---

<a name="v2.2.0a2"></a>
## [v2.2.0a2](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0a1...v2.2.0a2) (2026-03-07)

### Changes

#### Bug Fixes
- Fix MacOS native/Homebrew test failures and thread safety issues ([#666](https://github.com/carlkidcrypto/ezsnmp/issues/666))

#### Bug Fixes
- fix: recover from corrupt cached Docker image tar instead of failing CI job ([#687](https://github.com/carlkidcrypto/ezsnmp/issues/687))

#### Close
- Close SNMP session before cleanup ([#674](https://github.com/carlkidcrypto/ezsnmp/issues/674))

#### Compact
- Compact integration-test PR comment summaries ([#689](https://github.com/carlkidcrypto/ezsnmp/issues/689))

#### Features
- Add deploy_pages job for GitHub Pages ([#673](https://github.com/carlkidcrypto/ezsnmp/issues/673))

#### Maintenance
- chore: bump alpha version to v2.2.0a2 ([#707](https://github.com/carlkidcrypto/ezsnmp/issues/707))
- chore(deps): bump tj-actions/changed-files from 47.0.4 to 47.0.5 ([#694](https://github.com/carlkidcrypto/ezsnmp/issues/694))
- chore(deps): bump docker/login-action from 3.7.0 to 4.0.0 ([#696](https://github.com/carlkidcrypto/ezsnmp/issues/696))
- chore(deps): bump docker/build-push-action from 6.19.2 to 7.0.0 ([#697](https://github.com/carlkidcrypto/ezsnmp/issues/697))
- chore(deps): bump github/codeql-action from 4.32.4 to 4.32.6 ([#699](https://github.com/carlkidcrypto/ezsnmp/issues/699))
- chore(deps): bump cibuildwheel from 3.3.1 to 3.4.0 ([#701](https://github.com/carlkidcrypto/ezsnmp/issues/701))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.4.0 to 1.6.0 ([#702](https://github.com/carlkidcrypto/ezsnmp/issues/702))
- chore(deps): bump tox from 4.46.3 to 4.49.0 ([#703](https://github.com/carlkidcrypto/ezsnmp/issues/703))
- chore(deps): bump black from 26.1.0 to 26.3.0 ([#704](https://github.com/carlkidcrypto/ezsnmp/issues/704))
- chore(deps): bump psf/black from 26.1.0 to 26.3.0 ([#705](https://github.com/carlkidcrypto/ezsnmp/issues/705))
- chore(deps): bump psf/black ([#706](https://github.com/carlkidcrypto/ezsnmp/issues/706))
- chore(deps): bump docker/setup-buildx-action from 3.12.0 to 4.0.0 ([#700](https://github.com/carlkidcrypto/ezsnmp/issues/700))
- chore(deps): bump carlkidcrypto/os-specific-runner from 2.1.3 to 2.2.0 ([#698](https://github.com/carlkidcrypto/ezsnmp/issues/698))
- chore(deps-dev): bump setuptools from 80.10.2 to 82.0.0 ([#661](https://github.com/carlkidcrypto/ezsnmp/issues/661))
- chore(deps): bump github/codeql-action from 4.32.3 to 4.32.4 ([#678](https://github.com/carlkidcrypto/ezsnmp/issues/678))
- chore(deps): bump EnricoMi/publish-unit-test-result-action ([#681](https://github.com/carlkidcrypto/ezsnmp/issues/681))
- chore(deps): bump MishaKav/pytest-coverage-comment from 1.2.0 to 1.4.0 ([#682](https://github.com/carlkidcrypto/ezsnmp/issues/682))
- chore(deps): bump tox from 4.46.0 to 4.46.3 ([#684](https://github.com/carlkidcrypto/ezsnmp/issues/684))
- chore(deps): bump actions/download-artifact from 7.0.0 to 8.0.0 ([#685](https://github.com/carlkidcrypto/ezsnmp/issues/685))
- chore(deps): bump actions/upload-artifact from 6.0.0 to 7.0.0 ([#686](https://github.com/carlkidcrypto/ezsnmp/issues/686))
- chore(deps): bump tox from 4.35.0 to 4.46.0 ([#683](https://github.com/carlkidcrypto/ezsnmp/issues/683))
- chore(deps): bump docker/build-push-action from 6.18.0 to 6.19.2 ([#671](https://github.com/carlkidcrypto/ezsnmp/issues/671))
- chore(deps): bump coverage from 7.13.3 to 7.13.4 ([#662](https://github.com/carlkidcrypto/ezsnmp/issues/662))
- chore(deps): bump tox from 4.34.1 to 4.35.0 ([#672](https://github.com/carlkidcrypto/ezsnmp/issues/672))
- chore(deps): bump tj-actions/changed-files from 47.0.1 to 47.0.4 ([#676](https://github.com/carlkidcrypto/ezsnmp/issues/676))
- chore(deps): bump github/codeql-action from 4.32.2 to 4.32.3 ([#675](https://github.com/carlkidcrypto/ezsnmp/issues/675))
- chore: update CHANGELOG.md
- chore: update CHANGELOG.md

#### Merged Pull Requests
- Merge branch 'main' into update-changelog-21951921360

#### Remove
- Remove release asset upload from sphinx_build workflow ([#680](https://github.com/carlkidcrypto/ezsnmp/issues/680))

### Merged Pull Requests
- Merge pull request [#670](https://github.com/carlkidcrypto/ezsnmp/issues/670) from carlkidcrypto/update-changelog-21951921360
- Merge pull request [#669](https://github.com/carlkidcrypto/ezsnmp/issues/669) from carlkidcrypto/update-changelog-21951920671

---

<a name="v2.2.0a1"></a>
## [v2.2.0a1](https://github.com/carlkidcrypto/ezsnmp/compare/v2.2.0a0...v2.2.0a1) (2026-02-11)

### Changes

#### Bug Fixes
- Fix/issue 655 exit in optproc ([#667](https://github.com/carlkidcrypto/ezsnmp/issues/667))
- Fix OID/Index parsing for tables with quoted strings in indexes ([#525](https://github.com/carlkidcrypto/ezsnmp/issues/525))
- Fix workflow decode errors and black formatting violations ([#649](https://github.com/carlkidcrypto/ezsnmp/issues/649))

#### Bugfix
- Bugfix/fix broken gh workflows ([#632](https://github.com/carlkidcrypto/ezsnmp/issues/632))

#### Code Refactoring
- Use super() for SessionBase methods ([#664](https://github.com/carlkidcrypto/ezsnmp/issues/664))

#### Create
- Create build_and_publish_docker_images.yml ([#657](https://github.com/carlkidcrypto/ezsnmp/issues/657))

#### Delete
- Delete _codeql_detected_source_root ([#660](https://github.com/carlkidcrypto/ezsnmp/issues/660))

#### Features
- Feature/docker builds py14 3 ([#652](https://github.com/carlkidcrypto/ezsnmp/issues/652))

#### Maintenance
- chore(deps): bump github/codeql-action from 4.32.1 to 4.32.2 ([#651](https://github.com/carlkidcrypto/ezsnmp/issues/651))
- chore(deps): bump coverage from 7.13.2 to 7.13.3 ([#650](https://github.com/carlkidcrypto/ezsnmp/issues/650))
- chore(deps-dev): bump setuptools from 80.9.0 to 80.10.2 ([#646](https://github.com/carlkidcrypto/ezsnmp/issues/646))
- chore(deps): bump peter-evans/create-pull-request from 8.0.0 to 8.1.0 ([#639](https://github.com/carlkidcrypto/ezsnmp/issues/639))
- chore(deps-dev): bump wheel from 0.46.1 to 0.46.3 ([#640](https://github.com/carlkidcrypto/ezsnmp/issues/640))
- chore(deps): bump github/codeql-action from 4.32.0 to 4.32.1 ([#648](https://github.com/carlkidcrypto/ezsnmp/issues/648))
- chore(deps): bump github/codeql-action from 4.31.11 to 4.32.0 ([#644](https://github.com/carlkidcrypto/ezsnmp/issues/644))
- chore(deps): bump actions/setup-python from 6.1.0 to 6.2.0 ([#641](https://github.com/carlkidcrypto/ezsnmp/issues/641))
- chore(deps): bump actions/checkout from 6.0.1 to 6.0.2 ([#642](https://github.com/carlkidcrypto/ezsnmp/issues/642))
- chore(deps): bump actions/cache from 5.0.2 to 5.0.3 ([#647](https://github.com/carlkidcrypto/ezsnmp/issues/647))
- chore(deps): bump coverage from 7.13.1 to 7.13.2 ([#645](https://github.com/carlkidcrypto/ezsnmp/issues/645))
- chore(deps): bump github/codeql-action from 4.31.10 to 4.31.11 ([#643](https://github.com/carlkidcrypto/ezsnmp/issues/643))
- chore(deps): bump psf/black from 25.12.0 to 26.1.0 ([#636](https://github.com/carlkidcrypto/ezsnmp/issues/636))
- chore(deps): bump black from 25.12.0 to 26.1.0 ([#635](https://github.com/carlkidcrypto/ezsnmp/issues/635))
- chore(deps): bump actions/download-artifact from 4 to 7 ([#634](https://github.com/carlkidcrypto/ezsnmp/issues/634))
- chore(deps): bump peter-evans/create-or-update-comment from 4 to 5 ([#637](https://github.com/carlkidcrypto/ezsnmp/issues/637))
- chore(deps): bump tomli from 2.3.0 to 2.4.0 ([#626](https://github.com/carlkidcrypto/ezsnmp/issues/626))
- chore(deps): bump codecov/codecov-action from 5.5.1 to 5.5.2 ([#627](https://github.com/carlkidcrypto/ezsnmp/issues/627))
- chore(deps): bump actions/cache from 5.0.1 to 5.0.2 ([#628](https://github.com/carlkidcrypto/ezsnmp/issues/628))
- chore(deps): bump github/codeql-action from 4.31.9 to 4.31.10 ([#625](https://github.com/carlkidcrypto/ezsnmp/issues/625))
- chore: update CHANGELOG.md
- chore: update CHANGELOG.md

#### Merged Pull Requests
- Merge main and integrate threading-vs-multiprocessing docs into Sphinx ([#619](https://github.com/carlkidcrypto/ezsnmp/issues/619))
- Merge branch 'main' into update-changelog-21123398480

#### Remove
- Remove generated documentation from repository and automate deployment ([#622](https://github.com/carlkidcrypto/ezsnmp/issues/622))

### Merged Pull Requests
- Merge pull request [#631](https://github.com/carlkidcrypto/ezsnmp/issues/631) from carlkidcrypto/update-changelog-21123398480
- Merge pull request [#630](https://github.com/carlkidcrypto/ezsnmp/issues/630) from carlkidcrypto/update-changelog-21123398484

---

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
- chore(deps): bump build from 1.3.0 to 1.4.0 ([#615](https://github.com/carlkidcrypto/ezsnmp/issues/615))
- chore(deps): bump tox from 4.33.0 to 4.34.1 ([#617](https://github.com/carlkidcrypto/ezsnmp/issues/617))
- chore(deps): bump cibuildwheel from 3.3.0 to 3.3.1 ([#612](https://github.com/carlkidcrypto/ezsnmp/issues/612))
- chore(deps): bump urllib3 from 2.6.2 to 2.6.3 ([#613](https://github.com/carlkidcrypto/ezsnmp/issues/613))
- chore(deps): bump tox from 4.32.0 to 4.33.0 ([#611](https://github.com/carlkidcrypto/ezsnmp/issues/611))
- chore(deps): bump EnricoMi/publish-unit-test-result-action ([#606](https://github.com/carlkidcrypto/ezsnmp/issues/606))
- chore(deps): bump peter-evans/find-comment from 3 to 4 ([#607](https://github.com/carlkidcrypto/ezsnmp/issues/607))
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

#### Releases
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

#### V2
- V2.0.1 Docs ([#372](https://github.com/carlkidcrypto/ezsnmp/issues/372))

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

#### Releases
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

### Changes

#### 1
- 1.1.0a1 ([#222](https://github.com/carlkidcrypto/ezsnmp/issues/222))

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

#### Releases
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

