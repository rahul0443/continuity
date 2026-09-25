---
doc_id: INC-ORB7-022
equipment: Orbis CMP-7 Polisher
doc_type: incident_log
title: Slurry flow restriction invisible at tank-side sensor
synthetic: true
---

# INC-ORB7-022: Slurry flow restriction invisible at tank-side sensor

**Date logged:** synthetic record
**Reported by:** Shift Engineer (synthetic)
**Severity:** Low — caught before lot impact

## Symptom
Removal rate on the first wafer of shift trended low. Tank-side slurry flow
sensor read within spec.

## Investigation
Point-of-use flow sensor (at the polishing head) showed flow approximately
12% below setpoint, despite the tank-side reading being normal. A partial
restriction had developed in the supply line between the tank and the
point-of-use sensor, likely from settled particle buildup after a longer
than usual idle period over the weekend.

## Resolution
Extended slurry line purge from the standard 5 minutes to 15 minutes cleared
the restriction. Point-of-use flow returned to setpoint.

## Lesson learned
The tank-side sensor cannot detect line restrictions that develop downstream
of it — this is exactly why SOP-ORB7-003 requires checking flow at the
point-of-use sensor, not the tank sensor. After any extended idle period
(weekend, holiday, unplanned downtime), consider an extended purge before
the standard 5-minute purge, since settled particle buildup scales with idle
time.
