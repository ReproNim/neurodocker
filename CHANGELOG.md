# 2.1.1 (Fri Feb 13 2026)

#### 🏠 Internal

- Add auto-version query step and push Docker master tag on every build [#701](https://github.com/ReproNim/neurodocker/pull/701) ([@yarikoptic](https://github.com/yarikoptic))

#### Authors: 1

- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

# 2.1.0 (Fri Feb 13 2026)

#### 🚀 Enhancement

- Drop Python 3.9 support, require Python 3.10+ [#698](https://github.com/ReproNim/neurodocker/pull/698) ([@yarikoptic](https://github.com/yarikoptic))

#### 🐛 Bug Fix

- add publish container to github registry [#697](https://github.com/ReproNim/neurodocker/pull/697) ([@stebo85](https://github.com/stebo85))

#### 🏠 Internal

- Add mypy and types-PyYAML to dev dependencies [#700](https://github.com/ReproNim/neurodocker/pull/700) ([@yarikoptic](https://github.com/yarikoptic))
- Add quick build/upload of docker images based on what we have in heudiconv [#638](https://github.com/ReproNim/neurodocker/pull/638) ([@yarikoptic](https://github.com/yarikoptic) [@satra](https://github.com/satra))

#### Authors: 3

- Satrajit Ghosh ([@satra](https://github.com/satra))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))
- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

# 2.0.2 (Tue Aug 05 2025)

#### 🐛 Bug Fix

- Fixes bug in determining whether to unzip or untar ANTs download [#680](https://github.com/ReproNim/neurodocker/pull/680) ([@tclose](https://github.com/tclose))
- add new FSL version and update libopenblas name for ubuntu 24.04 [#682](https://github.com/ReproNim/neurodocker/pull/682) ([@stebo85](https://github.com/stebo85))
- [BOT] update pre-commit hooks [#681](https://github.com/ReproNim/neurodocker/pull/681) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))

#### Authors: 4

- [@github-actions[bot]](https://github.com/github-actions[bot])
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))
- Tom Close ([@tclose](https://github.com/tclose))

---

# 2.0.1 (Fri Aug 01 2025)

#### 🐛 Bug Fix

- adds latest ANTs versions [#679](https://github.com/ReproNim/neurodocker/pull/679) ([@tclose](https://github.com/tclose))
- Updated copyright period to be inclusive of 2025 [#678](https://github.com/ReproNim/neurodocker/pull/678) ([@tclose](https://github.com/tclose))
- [BOT] update pre-commit hooks [#674](https://github.com/ReproNim/neurodocker/pull/674) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- adds the latest dcm2niix versions to neurodocker [#675](https://github.com/ReproNim/neurodocker/pull/675) ([@tclose](https://github.com/tclose))
- Accept conda TOS [#676](https://github.com/ReproNim/neurodocker/pull/676) ([@tclose](https://github.com/tclose))
- [BOT] update pre-commit hooks [#672](https://github.com/ReproNim/neurodocker/pull/672) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- removed broken cat12 build and updated with new build [#671](https://github.com/ReproNim/neurodocker/pull/671) ([@stebo85](https://github.com/stebo85))
- Update cat12.yaml - cat12 changed versioning scheme [#670](https://github.com/ReproNim/neurodocker/pull/670) ([@stebo85](https://github.com/stebo85))
- Update cat12.yaml to add new version 12.9 [#669](https://github.com/ReproNim/neurodocker/pull/669) ([@stebo85](https://github.com/stebo85))

#### Authors: 4

- [@github-actions[bot]](https://github.com/github-actions[bot])
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))
- Tom Close ([@tclose](https://github.com/tclose))

---

# 2.0.0 (Mon Mar 03 2025)

#### 💥 Breaking Change

- Bump peter-evans/create-pull-request from 6 to 7 [#641](https://github.com/ReproNim/neurodocker/pull/641) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### 🚀 Enhancement

- reorder readme [#668](https://github.com/ReproNim/neurodocker/pull/668) ([@satra](https://github.com/satra))
- [BOT] update pre-commit hooks [#667](https://github.com/ReproNim/neurodocker/pull/667) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- Create release [#666](https://github.com/ReproNim/neurodocker/pull/666) ([@satra](https://github.com/satra))

#### 🐛 Bug Fix

- Fix/builds [#665](https://github.com/ReproNim/neurodocker/pull/665) ([@satra](https://github.com/satra))
- Fix/builds [#664](https://github.com/ReproNim/neurodocker/pull/664) ([@satra](https://github.com/satra))
- fix: jq from source needs dependencies [#663](https://github.com/ReproNim/neurodocker/pull/663) ([@satra](https://github.com/satra))
- ref: use org secret and bump base images and toolkits [#651](https://github.com/ReproNim/neurodocker/pull/651) ([@satra](https://github.com/satra) [@iishiishii](https://github.com/iishiishii))
- [BOT] update pre-commit hooks [#658](https://github.com/ReproNim/neurodocker/pull/658) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- reverting ' ' around nii.gz because it wasn't working [#661](https://github.com/ReproNim/neurodocker/pull/661) ([@stebo85](https://github.com/stebo85))
- Update freesurfer.yaml [#660](https://github.com/ReproNim/neurodocker/pull/660) ([@stebo85](https://github.com/stebo85))
- add fsl 6.0.7.16 [#659](https://github.com/ReproNim/neurodocker/pull/659) ([@stebo85](https://github.com/stebo85))
- [BOT] update pre-commit hooks [#650](https://github.com/ReproNim/neurodocker/pull/650) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [BOT] update pre-commit hooks [#649](https://github.com/ReproNim/neurodocker/pull/649) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- add fsl 6.0.7.14 [#648](https://github.com/ReproNim/neurodocker/pull/648) ([@stebo85](https://github.com/stebo85))
- [BOT] update pre-commit hooks [#647](https://github.com/ReproNim/neurodocker/pull/647) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [MAINT] Drop python 3.8 and support 3.13 [#646](https://github.com/ReproNim/neurodocker/pull/646) ([@Remi-Gau](https://github.com/Remi-Gau))
- [BOT] update pre-commit hooks [#644](https://github.com/ReproNim/neurodocker/pull/644) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- Update matlabmcr.yaml R2023b to Update 9 [#643](https://github.com/ReproNim/neurodocker/pull/643) ([@stebo85](https://github.com/stebo85))
- add new FSL version [#642](https://github.com/ReproNim/neurodocker/pull/642) ([@stebo85](https://github.com/stebo85))
- [BOT] update pre-commit hooks [#639](https://github.com/ReproNim/neurodocker/pull/639) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [BOT] update pre-commit hooks [#637](https://github.com/ReproNim/neurodocker/pull/637) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [MAINT] drop types all from pre-commit config [#636](https://github.com/ReproNim/neurodocker/pull/636) ([@Remi-Gau](https://github.com/Remi-Gau))
- [BOT] update pre-commit hooks [#634](https://github.com/ReproNim/neurodocker/pull/634) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- Fix typo in CHANGELOG.md to pacify codespell [#631](https://github.com/ReproNim/neurodocker/pull/631) ([@Remi-Gau](https://github.com/Remi-Gau))
- [BOT] update pre-commit hooks [#633](https://github.com/ReproNim/neurodocker/pull/633) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [BOT] update pre-commit hooks [#630](https://github.com/ReproNim/neurodocker/pull/630) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))

#### ⚠️ Pushed to `master`

- Update release.yml ([@satra](https://github.com/satra))

#### Authors: 6

- [@dependabot[bot]](https://github.com/dependabot[bot])
- [@github-actions[bot]](https://github.com/github-actions[bot])
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Satrajit Ghosh ([@satra](https://github.com/satra))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))
- Thuy Dao ([@iishiishii](https://github.com/iishiishii))

---

# 1.0.1 (Sat Jul 06 2024)

#### 🐛 Bug Fix

- FIX use --transform in freesurfer's template to generalize across freesurfer versions to strip leading `freesurfer/` folder [#626](https://github.com/ReproNim/neurodocker/pull/626) ([@mvdoc](https://github.com/mvdoc))
- FIX remove comment from freesurfer env line [#622](https://github.com/ReproNim/neurodocker/pull/622) ([@mvdoc](https://github.com/mvdoc))
- FIX add default header and entrypoint to docker and singularity files [#623](https://github.com/ReproNim/neurodocker/pull/623) ([@mvdoc](https://github.com/mvdoc))
- [BOT] update pre-commit hooks [#627](https://github.com/ReproNim/neurodocker/pull/627) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- Fix typo of "software" [#624](https://github.com/ReproNim/neurodocker/pull/624) ([@yarikoptic](https://github.com/yarikoptic))
- [BOT] update pre-commit hooks [#621](https://github.com/ReproNim/neurodocker/pull/621) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))

#### Authors: 4

- [@github-actions[bot]](https://github.com/github-actions[bot])
- Matteo Visconti di Oleggio Castello ([@mvdoc](https://github.com/mvdoc))
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

# 1.0.0 (Tue Jun 11 2024)

#### 💥 Breaking Change

- Bump actions/checkout from 3 to 4 [#582](https://github.com/ReproNim/neurodocker/pull/582) ([@dependabot[bot]](https://github.com/dependabot[bot]))
- Bump actions/checkout from 3 to 4 [#573](https://github.com/ReproNim/neurodocker/pull/573) ([@dependabot[bot]](https://github.com/dependabot[bot]))
- Bump actions/stale from 5 to 8 [#560](https://github.com/ReproNim/neurodocker/pull/560) ([@dependabot[bot]](https://github.com/dependabot[bot]))
- Bump actions/checkout from 2 to 3 [#557](https://github.com/ReproNim/neurodocker/pull/557) ([@dependabot[bot]](https://github.com/dependabot[bot]))
- Bump actions/setup-python from 2 to 4 [#556](https://github.com/ReproNim/neurodocker/pull/556) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### 🐛 Bug Fix

- [BOT] update pre-commit hooks [#616](https://github.com/ReproNim/neurodocker/pull/616) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [BOT] update pre-commit hooks [#614](https://github.com/ReproNim/neurodocker/pull/614) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- make scripts executable after build [#615](https://github.com/ReproNim/neurodocker/pull/615) ([@stebo85](https://github.com/stebo85))
- [BOT] update pre-commit hooks [#613](https://github.com/ReproNim/neurodocker/pull/613) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- Use HTTPS for NeuroDebian APT listing urls [#612](https://github.com/ReproNim/neurodocker/pull/612) ([@TheChymera](https://github.com/TheChymera))
- [BOT] update pre-commit hooks [#610](https://github.com/ReproNim/neurodocker/pull/610) ([@Remi-Gau](https://github.com/Remi-Gau) [@github-actions[bot]](https://github.com/github-actions[bot]))
- [FIX] Update branch in update_precommit_hooks.yml [#609](https://github.com/ReproNim/neurodocker/pull/609) ([@Remi-Gau](https://github.com/Remi-Gau))
- [ENH] package with hatchling and switch to pyproject.toml [#607](https://github.com/ReproNim/neurodocker/pull/607) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] update linting config and CI [#604](https://github.com/ReproNim/neurodocker/pull/604) ([@Remi-Gau](https://github.com/Remi-Gau))
- fixed flake8 errors from #597 [#598](https://github.com/ReproNim/neurodocker/pull/598) ([@Vbitz](https://github.com/Vbitz))
- Added "--add" command line option to add tar files as docker layers. [#597](https://github.com/ReproNim/neurodocker/pull/597) ([@Vbitz](https://github.com/Vbitz))
- added versions to Library PATH [#593](https://github.com/ReproNim/neurodocker/pull/593) ([@stebo85](https://github.com/stebo85))
- update matlabmcr [#592](https://github.com/ReproNim/neurodocker/pull/592) ([@stebo85](https://github.com/stebo85))
- [FIX] add url bids validator [#591](https://github.com/ReproNim/neurodocker/pull/591) ([@Remi-Gau](https://github.com/Remi-Gau))
- [DOC] add list of supported software [#587](https://github.com/ReproNim/neurodocker/pull/587) ([@Remi-Gau](https://github.com/Remi-Gau))
- [ENH] add templates bids_validator [#586](https://github.com/ReproNim/neurodocker/pull/586) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] test build jq [#589](https://github.com/ReproNim/neurodocker/pull/589) ([@Remi-Gau](https://github.com/Remi-Gau))
- [ENH] test on python 3.12 [#588](https://github.com/ReproNim/neurodocker/pull/588) ([@Remi-Gau](https://github.com/Remi-Gau))
- Update fsl.yaml [#583](https://github.com/ReproNim/neurodocker/pull/583) ([@stebo85](https://github.com/stebo85))
- [DOC] update doc [#569](https://github.com/ReproNim/neurodocker/pull/569) ([@Remi-Gau](https://github.com/Remi-Gau))
- [ENH] implement more recent mrtrix version [#579](https://github.com/ReproNim/neurodocker/pull/579) ([@Remi-Gau](https://github.com/Remi-Gau))
- Update examples.rst [#578](https://github.com/ReproNim/neurodocker/pull/578) ([@stebo85](https://github.com/stebo85))
- added FSL interactivity note [#576](https://github.com/ReproNim/neurodocker/pull/576) ([@stebo85](https://github.com/stebo85))
- Include FSL license auto-yes example [#575](https://github.com/ReproNim/neurodocker/pull/575) ([@stebo85](https://github.com/stebo85))
- [MAINT] Update stale.yml [#577](https://github.com/ReproNim/neurodocker/pull/577) ([@Remi-Gau](https://github.com/Remi-Gau))
- [FIX] install the proper dependencies for doc build [#574](https://github.com/ReproNim/neurodocker/pull/574) ([@Remi-Gau](https://github.com/Remi-Gau))
- [DOC] auto doc main CLI [#463](https://github.com/ReproNim/neurodocker/pull/463) ([@Remi-Gau](https://github.com/Remi-Gau))
- [FIX] use local var for software name in bootstrap workflow [#572](https://github.com/ReproNim/neurodocker/pull/572) ([@Remi-Gau](https://github.com/Remi-Gau))
- [FIX] use env variable in bootstrap workflow [#571](https://github.com/ReproNim/neurodocker/pull/571) ([@Remi-Gau](https://github.com/Remi-Gau))
- [INFRA] add possibility to only build a single workflow [#570](https://github.com/ReproNim/neurodocker/pull/570) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] test build of conda as part of the bootstrap workflow [#566](https://github.com/ReproNim/neurodocker/pull/566) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] minimize file changes that can trigger the bootstrap workflow [#564](https://github.com/ReproNim/neurodocker/pull/564) ([@Remi-Gau](https://github.com/Remi-Gau))
- set python version for format job [#563](https://github.com/ReproNim/neurodocker/pull/563) ([@stebo85](https://github.com/stebo85))
- Add mamba option to miniconda [#562](https://github.com/ReproNim/neurodocker/pull/562) ([@Shotgunosine](https://github.com/Shotgunosine))
- [MAINT] remove oldest distro in automated build testing [#559](https://github.com/ReproNim/neurodocker/pull/559) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] split format checking and testing in CI [#554](https://github.com/ReproNim/neurodocker/pull/554) ([@Remi-Gau](https://github.com/Remi-Gau))
- [MAINT] Simplify type annotations [#551](https://github.com/ReproNim/neurodocker/pull/551) ([@Remi-Gau](https://github.com/Remi-Gau))
- apply isort and all pre-commit hooks [#549](https://github.com/ReproNim/neurodocker/pull/549) ([@Remi-Gau](https://github.com/Remi-Gau))
- Mcr bug [#471](https://github.com/ReproNim/neurodocker/pull/471) ([@stebo85](https://github.com/stebo85))
- Add codespell: config, pre-commit, workflow + 1 typo fixed [#544](https://github.com/ReproNim/neurodocker/pull/544) ([@yarikoptic](https://github.com/yarikoptic) [@stebo85](https://github.com/stebo85))
- added freesurfer 7.3.2 [#547](https://github.com/ReproNim/neurodocker/pull/547) ([@stebo85](https://github.com/stebo85))
- add fsl 6.0.7.1 [#543](https://github.com/ReproNim/neurodocker/pull/543) ([@stebo85](https://github.com/stebo85))
- added freesurfer 7.4.1 [#542](https://github.com/ReproNim/neurodocker/pull/542) ([@hjbockholt](https://github.com/hjbockholt))
- Fixing my update for mcr2023a [#540](https://github.com/ReproNim/neurodocker/pull/540) ([@dnkennedy](https://github.com/dnkennedy))
- Update matlabmcr.yaml [#539](https://github.com/ReproNim/neurodocker/pull/539) ([@dnkennedy](https://github.com/dnkennedy))
- Update years to have full range of years of the project [#534](https://github.com/ReproNim/neurodocker/pull/534) ([@yarikoptic](https://github.com/yarikoptic))
- Update cat [#533](https://github.com/ReproNim/neurodocker/pull/533) ([@stebo85](https://github.com/stebo85))

#### ⚠️ Pushed to `master`

- Change name of parent directory ([@kaczmarj](https://github.com/kaczmarj))

#### 🏠 Internal

- Upgrade intuit auto to 11.1.6 (most recent) [#617](https://github.com/ReproNim/neurodocker/pull/617) ([@yarikoptic](https://github.com/yarikoptic))

#### 🔩 Dependency Updates

- Bump actions/setup-python from 4 to 5 [#594](https://github.com/ReproNim/neurodocker/pull/594) ([@dependabot[bot]](https://github.com/dependabot[bot]))
- Bump actions/stale from 8 to 9 [#595](https://github.com/ReproNim/neurodocker/pull/595) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### Authors: 11

- [@dependabot[bot]](https://github.com/dependabot[bot])
- [@github-actions[bot]](https://github.com/github-actions[bot])
- David Kennedy ([@dnkennedy](https://github.com/dnkennedy))
- Dylan Nielson ([@Shotgunosine](https://github.com/Shotgunosine))
- H. Jeremy Bockholt ([@hjbockholt](https://github.com/hjbockholt))
- Horea Christian ([@TheChymera](https://github.com/TheChymera))
- Jakub Kaczmarzyk ([@kaczmarj](https://github.com/kaczmarj))
- Joshua Scarsbrook ([@Vbitz](https://github.com/Vbitz))
- Remi Gau ([@Remi-Gau](https://github.com/Remi-Gau))
- Steffen Bollmann ([@stebo85](https://github.com/stebo85))
- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

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
