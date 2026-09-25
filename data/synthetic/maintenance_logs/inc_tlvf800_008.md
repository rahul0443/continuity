---
doc_id: INC-TLVF800-008
equipment: ThermaLine VF-800 Vertical Diffusion Furnace
doc_type: incident_log
title: Gradual top-to-bottom non-uniformity from gas injector drift
synthetic: true
---

# INC-TLVF800-008: Gradual top-to-bottom non-uniformity from gas injector drift

**Date logged:** synthetic record
**Reported by:** Furnace Technician (synthetic)
**Severity:** Medium — gradual drift over several weeks

## Symptom
Top-to-bottom thickness non-uniformity on monitor wafers increased slowly
over approximately four weeks, from a healthy 1.8% to 4.5% (spec: below 3%).
No single run showed a sudden excursion.

## Investigation
Because the drift was gradual rather than sudden, initial assumption was a
slowly failing heater zone. All zone temperatures were confirmed within
±1°C of setpoint per SOP-TLVF800-005. Gas injector flow calibration check
found the injector flow distribution had drifted approximately 8% from
qualified baseline, consistent with slow orifice wear.

## Resolution
Injector was recalibrated and orifice inspected; minor wear was within
serviceable limits after recalibration. Uniformity returned to 2.0% within
one week of recalibration.

## Lesson learned
A gradual, multi-week non-uniformity drift on this furnace family points
toward gas injector flow drift, not heater degradation, even though heater
issues are the more intuitive first suspect. Checking injector calibration
before scheduling heater diagnostics would have shortened this
investigation by roughly two weeks.
