---
doc_id: SOP-HLX2100-004
equipment: Helios NXP-2100 Lithography Scanner
doc_type: SOP
title: Overlay Calibration and Reticle Handling Procedure
synthetic: true
---

# SOP-HLX2100-004: Overlay Calibration and Reticle Handling Procedure

**Equipment:** Helios NXP-2100 Lithography Scanner
**Applies to:** Shift engineers, litho technicians
**Revision:** 5.0

## 1. Purpose
Defines the daily overlay calibration sequence and reticle handling
requirements for the Helios NXP-2100 scanner.

## 2. Overlay Calibration
1. Run the standard overlay calibration reticle at the start of each shift
   before processing production reticles.
2. Confirm overlay error is within ±3nm (mean + 3-sigma) across the field.
3. If overlay drifts outside spec, first check wafer stage temperature
   stability logs before assuming a lens or alignment system fault — thermal
   drift in the stage chuck is a more frequent root cause than optical
   misalignment on this tool family, but produces a very similar overlay
   signature.

## 3. Reticle Handling
1. Inspect reticle pods for particle contamination before load; a contaminated
   pod is the leading cause of hard-to-reproduce, reticle-specific overlay and
   CD (critical dimension) excursions.
2. Confirm reticle ID against the job traveler before load; a reticle mismatch
   will not always trigger an automatic interlock if the reticle barcode is
   damaged or partially unreadable.
3. Log reticle exposure count. Pellicle replacement is required at the
   qualified exposure count limit regardless of visual condition.

## 4. Dose and Focus Verification
1. Run focus-exposure matrix (FEM) monitor wafer weekly, or after any lens
   maintenance event.
2. Confirm best focus and best dose are within the qualified process window
   before releasing the tool.

## 5. Escalation
If overlay or CD excursions recur across multiple reticles and multiple lots
in the same shift, treat this as a tool-level systematic issue, not a
reticle-level issue, and escalate to litho equipment engineering immediately —
do not continue processing lots while root-causing.

## 6. Sign-off
Record calibration results, reticle exposure counts, and any excursions in the
scanner shift log.
