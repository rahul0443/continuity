---
doc_id: SOP-VNT300-002
equipment: Vantage PECVD 300 Deposition System
doc_type: SOP
title: Weekly Preventive Maintenance and Showerhead Inspection
synthetic: true
---

# SOP-VNT300-002: Weekly Preventive Maintenance and Showerhead Inspection

**Equipment:** Vantage PECVD 300 Deposition System (SiN / SiO2 dielectric films)
**Applies to:** Equipment technicians
**Revision:** 3.0

## 1. Purpose
Defines the weekly preventive maintenance (PM) sequence for the Vantage PECVD 300,
including showerhead inspection and film uniformity verification.

## 2. Showerhead Inspection
1. Vent chamber per standard vent procedure and allow 30-minute cooldown before
   opening.
2. Visually inspect the gas distribution showerhead for hole blockage. Blockage
   is most commonly found in the outer ring of holes due to edge deposition
   effects.
3. If more than 3% of showerhead holes show visible blockage, schedule a
   showerhead swap. Do not attempt to clear blockage in-situ with a probe; this
   has previously caused hole diameter distortion and downstream uniformity
   drift (see incident log INC-VNT300-009).

## 3. RF Electrode Gap Verification
1. Confirm electrode spacing is within 0.05mm of the recipe-specified gap using
   the calibrated gap gauge.
2. Gap drift beyond tolerance is the leading cause of center-to-edge thickness
   non-uniformity on this tool family.

## 4. Film Uniformity Verification
1. Run a standard monitor wafer at the primary production recipe (SiN, 500Å
   target).
2. Measure 49-point thickness map. Uniformity (1-sigma) must be below 1.5%
   before the chamber is released.
3. If uniformity fails and the showerhead and electrode gap have both passed
   inspection, check susceptor temperature uniformity next — see
   SOP-VNT300-002 Section 5.

## 5. Susceptor Temperature Check
1. Verify susceptor temperature zones are within 2°C of setpoint using the
   calibrated thermocouple probe kit.
2. A common failure mode on this tool is a single degraded heater zone that
   still reads correctly on the primary control thermocouple but drifts on the
   physical wafer surface — cross-check with the secondary probe if uniformity
   issues persist despite a passing showerhead and gap check.

## 6. Sign-off and PM Log Entry
Record all measurements in the PM log with technician ID. Any deviation
outside spec must be documented with corrective action taken before chamber
release.
