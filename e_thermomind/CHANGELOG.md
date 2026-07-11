# Changelog

## 0.8.53

- Hardened configuration persistence: saves a mirror copy under `/config`, keeps a previous-good copy before overwrites, and can recover from a near-default `/data` config after update/reinstall.
- Persisted the new `resistance.pv_min_w` safety parameter so setpoint saves no longer drop it.

## 0.8.52

- Solar valve failsafe now reopens the configured safe path using the normal day/night selector instead of forcing the night path during all-closed recovery.
- Keeps the hydraulic safety invariant: outside ACS solar priority, at least one base solar path remains open.

## 0.8.51

- Hardened Resistenze Volano safety: below export ON threshold, battery discharge block, or mapped PV production near zero now force all resistance outputs OFF and clear manual overrides.
- Added a PV-production guard for mapped PV sensors to avoid battery drain if an import/export sensor reports a misleading positive value at night.
- Added a backend live-control loop so safety/off commands run even when the dashboard is closed.
- Made the Volano transfer watchdog active: R6/R7/R13/R14 are forced OFF immediately when no transfer path is requested.
- Fixed resistance diagnostics when manual overrides block automatic ON commands.

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
