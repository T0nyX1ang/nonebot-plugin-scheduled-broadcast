# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.1.2](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/compare/v0.1.1...v0.1.2) (2023-10-27)

### Features

* slightly change some replies ([f3c0337](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/f3c03378d4638bfb9b0ae45f83e7e03455666a58))
* support [#5](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/issues/5) by extracting the broadcast id ([219d54d](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/219d54d5df6a4c8cd33e51136ce01442cac0ab6e))

### Bug Fixes

* **ci:** coverage test doesn't upload to codecov ([09838e8](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/09838e85d5c0894d289ef2b69c61dd380dc2420a))
* **lint:** use type hint more precisely ([c7095a7](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/c7095a75f4854cbab6fc78635b1ed3c53019981b))
* the scheduler will not be able to pause or resume if extra keys are set in the `config` and fix [#3](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/issues/3) ([fb0da4b](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/fb0da4ba3249ed1c56a24f70a7c178b1f01d91f1))

## [0.1.1](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/compare/v0.1.0...v0.1.1) (2023-10-24)

### Bug Fixes

* **plugin-check:** use `require` grammar ([3c05856](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/3c058566f7b0498b421c60909cb13766cf50ac64))

## 0.1.0 (2023-10-24)

### ⚠ BREAKING CHANGES

* **optimize:** policy data reuse enhancements
* change to user-defined broadcast ID

### Features

* `disablebc` will not delete the config ([83d208d](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/83d208d6e7bf998135413910246cf7b3efa52340))
* `enablebc` and `disablebc` will not require bot rebooting ([34727d3](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/34727d3661927e2b454d49ab0b6ca60dc7a8e59a))
* add an anchor event for messages ([8782454](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/8782454a2beceb0c25a8510c8a3e3465818a3720))
* add commands for anchor message inside init ([76ba709](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/76ba709ce48478ba290d7afde56dc0b4fe6cad97))
* change to user-defined broadcast ID ([2c6dc7b](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/2c6dc7b5d35ca15f85f3b16b710c8606a3122645))
* **optimize:** policy data reuse enhancements ([8aab5a9](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/8aab5a9de138193f87e74d7741745dc263e53f70))
* support basic schedulers ([6423b01](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/6423b012e5c35060f1dd6bd87156bd589258161a))

### Bug Fixes

* **#1:** fetch self_id by bot ([e154b12](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/e154b128f9469029e538001f161b8a1f302f8863)), closes [#1](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/issues/1)
* **doc:** a logical mistake ([539750b](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/539750b013d0f4b22181b017b135af07691e0723))
* **doc:** the title and description are not centered ([21d0a4d](https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast/commit/21d0a4d3010997ed05e47f6a0719b719945ea8b4))
