# 0.9.5 (Fri May 12 2023)

#### 🐛 Bug Fix

- Afni missing dependencies for suma [#512](https://github.com/ReproNim/neurodocker/pull/512) ([@stebo85](https://github.com/stebo85))
- modifying value for entry point to allow -arg or --arg [#515](https://github.com/ReproNim/neurodocker/pull/515) ([@djarecka](https://github.com/djarecka) [@kaczmarj](https://github.com/kaczmarj))
- Mcr missing deb libxp6 [#526](https://github.com/ReproNim/neurodocker/pull/526) ([@stebo85](https://github.com/stebo85))
- NEW: Add support for FSL version 6.0.6 onwards [#527](https://github.com/ReproNim/neurodocker/pull/527) ([@ghisvail](https://github.com/ghisvail))
- Enable build of docs with Sphinx 6 [#525](https://github.com/ReproNim/neurodocker/pull/525) ([@ghisvail](https://github.com/ghisvail))
- Add FSL version 6.0.5.2 [#523](https://github.com/ReproNim/neurodocker/pull/523) ([@ghisvail](https://github.com/ghisvail))
- Update ants.yaml [#521](https://github.com/ReproNim/neurodocker/pull/521) ([@araikes](https://github.com/araikes) [@kaczmarj](https://github.com/kaczmarj))
- [FIX] fix link to build dashboard [#517](https://github.com/ReproNim/neurodocker/pull/517) ([@Remi-Gau](https://github.com/Remi-Gau))
- Update cli.rst [#514](https://github.com/ReproNim/neurodocker/pull/514) ([@sooyounga](https://github.com/sooyounga) [@djarecka](https://github.com/djarecka))
- updated version tags and added latest tag clarification to docs [#516](https://github.com/ReproNim/neurodocker/pull/516) ([@sooyounga](https://github.com/sooyounga))
- Minc install from deb and rpm [#509](https://github.com/ReproNim/neurodocker/pull/509) ([@stebo85](https://github.com/stebo85))
- fix: repo info ([@satra](https://github.com/satra))
- [INFRA] test docker builds in CI [#487](https://github.com/ReproNim/neurodocker/pull/487) ([@Remi-Gau](https://github.com/Remi-Gau) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@satra](https://github.com/satra))
- do not install sphinx 6.x [#505](https://github.com/ReproNim/neurodocker/pull/505) ([@kaczmarj](https://github.com/kaczmarj))
- add bad versions to et file [#502](https://github.com/ReproNim/neurodocker/pull/502) ([@satra](https://github.com/satra))
- [TESTS] check black style in github actions [#501](https://github.com/ReproNim/neurodocker/pull/501) ([@kaczmarj](https://github.com/kaczmarj))

#### ⚠️ Pushed to `master`

- Update README.md ([@djarecka](https://github.com/djarecka))
- add workflow token ([@satra](https://github.com/satra))
- add commit agent ([@satra](https://github.com/satra))
- add all changed files ([@satra](https://github.com/satra))
- Update bootstrap.yml ([@satra](https://github.com/satra))
- simplify git commit ([@satra](https://github.com/satra))
- allow writing actions ([@satra](https://github.com/satra))
- remove on demand ([@satra](https://github.com/satra))
- fix docs build ([@satra](https://github.com/satra))
- fix: syntax ([@satra](https://github.com/satra))
- testing sphinx build ([@satra](https://github.com/satra))

#### 📝 Documentation

- changed base image for AFNI to fedora:35 [#520](https://github.com/ReproNim/neurodocker/pull/520) ([@stebo85](https://github.com/stebo85) [@kaczmarj](https://github.com/kaczmarj))

#### Authors: 9

- [@araikes](https://github.com/araikes)
- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Dorota Jarecka ([@djarecka](https://github.com/djarecka))
- Ghislain Vaillant ([@ghisvail](https://github.com/ghisvail))
- Jakub Kaczmarzyk ([@kaczmarj](https://github.com/kaczmarj))
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Satrajit Ghosh ([@satra](https://github.com/satra))
- Sooyoung Ahn ([@sooyounga](https://github.com/sooyounga))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))

---

# 0.9.4 (Wed Jan 18 2023)

#### 🐛 Bug Fix

- fix the types in --copy and --entrypoint [#500](https://github.com/ReproNim/neurodocker/pull/500) ([@kaczmarj](https://github.com/kaczmarj))
- add long_description to setup.cfg [#465](https://github.com/ReproNim/neurodocker/pull/465) ([@kaczmarj](https://github.com/kaczmarj))
- [FIX] add regression test for 498 [#499](https://github.com/ReproNim/neurodocker/pull/499) ([@Remi-Gau](https://github.com/Remi-Gau))

#### Authors: 2

- Jakub Kaczmarzyk ([@kaczmarj](https://github.com/kaczmarj))
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))

---

# 0.9.3 (Mon Jan 16 2023)

#### 🐛 Bug Fix

- FIX: skip minification tests on M1/M2 macs and run them otherwise [#497](https://github.com/ReproNim/neurodocker/pull/497) ([@kaczmarj](https://github.com/kaczmarj))
- Add/ants24x [#473](https://github.com/ReproNim/neurodocker/pull/473) ([@araikes](https://github.com/araikes) [@kaczmarj](https://github.com/kaczmarj))

#### Authors: 2

- [@araikes](https://github.com/araikes)
- Jakub Kaczmarzyk ([@kaczmarj](https://github.com/kaczmarj))

---

# 0.9.2 (Sat Jan 14 2023)

#### 🐛 Bug Fix

- fix: auto setup [#496](https://github.com/ReproNim/neurodocker/pull/496) ([@satra](https://github.com/satra))
- enh: add release workflow [#495](https://github.com/ReproNim/neurodocker/pull/495) ([@satra](https://github.com/satra))
- remove empty lines [#488](https://github.com/ReproNim/neurodocker/pull/488) ([@satra](https://github.com/satra))
- FIX: --version output in containers [#493](https://github.com/ReproNim/neurodocker/pull/493) ([@kaczmarj](https://github.com/kaczmarj))
- fix: remove py 3.7 and add apptainer 1.1.5 [#490](https://github.com/ReproNim/neurodocker/pull/490) ([@satra](https://github.com/satra))
- fix: adjust optionEatAll for click >= 8 [#492](https://github.com/ReproNim/neurodocker/pull/492) ([@satra](https://github.com/satra))
- update pre-commit [#482](https://github.com/ReproNim/neurodocker/pull/482) ([@Remi-Gau](https://github.com/Remi-Gau))

#### ⚠️ Pushed to `master`

- fix: install mypy stubs ([@satra](https://github.com/satra))
- fix: mypy configuration ([@satra](https://github.com/satra))

#### Authors: 3

- Jakub Kaczmarzyk ([@kaczmarj](https://github.com/kaczmarj))
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Satrajit Ghosh ([@satra](https://github.com/satra))
