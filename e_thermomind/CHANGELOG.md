# Changelog

## 0.8.50

- Fixed Resistenze Volano start logic: `export_on_min_w` no longer acts as the required residual export after enabling a new step, so high real export can start the resistances as expected.
- Added faster step-0 shutdown below threshold and clearer diagnostics when manual overrides block automatic resistance ON commands.
- Added initial draw.io/SVG design assets for the central heating dashboard components.

## 0.8.49

- Added a Home Assistant add-on changelog so Supervisor can show release notes instead of leaving the update dialog without changelog metadata.
- Keeps the 0.8.48 Resistenze Volano fix: resistances can start from FV/export surplus even when `Dest=OFF`, while still respecting `VOLANO_MAX`, export thresholds, and battery block.

## 0.8.48

- Fixed Resistenze Volano logic: removed the false `Dest=OFF` blocker.
- With useful FV/export surplus, the resistances can charge the volano even when ACS and puffer do not request a destination.

## 0.8.47

- Fixed Home Assistant Ingress/sidebar blank page.
- Vite assets, favicon, API calls, and WebSocket now use paths relative to the add-on ingress prefix.
