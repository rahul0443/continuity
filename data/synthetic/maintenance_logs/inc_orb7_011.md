---
doc_id: INC-ORB7-011
equipment: Orbis CMP-7 Polisher
doc_type: incident_log
title: Removal rate drift traced to retaining ring wear
synthetic: true
---

# INC-ORB7-011: Removal rate drift traced to retaining ring wear

**Date logged:** synthetic record
**Reported by:** Equipment Technician (synthetic)
**Severity:** Medium — gradual yield impact over 2 weeks before detection

## Symptom
Cu removal rate on monitor wafers drifted from target by increasing amounts
over roughly two weeks, eventually reaching -9% (below the ±7% spec). Pad
conditioning and slurry qualification both passed per SOP-ORB7-003 throughout
this period.

## Investigation
Retaining ring wear was not part of the standard daily checklist and is only
inspected at a longer PM interval. Ring wear changes the pressure profile at
the wafer edge, which reduces edge removal rate without an obvious visual
defect — the ring still looked serviceable on visual inspection.

## Resolution
Replaced retaining ring ahead of its scheduled PM interval. Removal rate
returned to within spec immediately.

## Lesson learned
Retaining ring wear produces a gradual, edge-weighted removal rate decline
that is easy to misattribute to slurry or pad issues because those are
checked first and more frequently. When removal rate drifts low over a period
of days-to-weeks despite passing pad and slurry checks, retaining ring wear
should be checked well before its normal PM interval, not after it — this is
now reflected in SOP-ORB7-003 Section 4.
