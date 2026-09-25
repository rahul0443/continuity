---
doc_id: SOP-AMX5200-001
equipment: AMX-5200 Plasma Etch System
doc_type: SOP
title: Daily Startup and RF Match Verification Procedure
synthetic: true
---

# SOP-AMX5200-001: Daily Startup and RF Match Verification Procedure

**Equipment:** AMX-5200 Plasma Etch System (fluorine-based dielectric etch)
**Applies to:** Shift engineers, equipment technicians
**Revision:** 4.2

## 1. Purpose
This procedure defines the required daily startup sequence for the AMX-5200 plasma
etch chamber, including RF match network verification, prior to releasing the tool
for production lots.

## 2. Pre-Startup Checks
1. Confirm chamber pressure is at idle base pressure (< 5 mTorr) on the process
   gauge before initiating RF strike.
2. Verify process gas cabinet interlocks are green (CF4, O2, Ar supply lines).
3. Inspect chamber viewport for visible deposition buildup. If buildup exceeds
   Level 2 on the visual reference chart, log a wet-clean request before proceeding.

## 3. RF Match Network Verification
1. Strike a plasma at standard recipe conditions (1200W source, 300W bias, 40 mTorr).
2. Confirm the RF match network tunes to < 2% reflected power within 8 seconds of
   strike. If tuning exceeds 15 seconds or reflected power remains above 5%, abort
   and flag an RF match fault (see Section 4).
3. Record match capacitor positions (C1, C2) in the equipment log. Positions
   drifting more than 10% from the rolling 30-day average should be flagged for
   preventive maintenance, even if the match currently tunes successfully.

## 4. RF Match Fault Response
1. If the match fails to tune, first re-seat the RF cable connection at the
   match box input (a loose N-type connector is the most common cause).
2. If reseating does not resolve the fault, inspect the match box air cooling
   fan; overheating of the match network electronics can cause tuning instability.
3. Escalate to equipment engineering if the fault recurs more than twice in one
   shift. Do not run production lots on a chamber with an unresolved RF match
   fault, even if it eventually tunes — see incident log INC-AMX5200-014 for the
   scrap event associated with running lots through an intermittently unstable
   match.

## 5. Chamber Conditioning
1. Run a 15-minute seasoning recipe (bare silicon monitor wafer) after any
   wet-clean or chamber vent, before processing production lots.
2. Confirm particle count on the seasoning wafer is below 15 adders (>0.16 µm)
   before release.

## 6. Sign-off
Shift engineer initials and timestamp required in the equipment logbook before
the chamber is released to the production schedule.
