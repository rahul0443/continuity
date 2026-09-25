---
doc_id: KI-TLVF800-001
equipment: ThermaLine VF-800 Vertical Diffusion Furnace
doc_type: knowledge_capture_interview
title: Exit knowledge-capture interview — Senior Furnace Engineer (rotation ending)
synthetic: true
---

# KI-TLVF800-001: Exit Knowledge-Capture Interview — Furnace

**Interviewer:** Is there anything about the furnace alarms that a new
engineer wouldn't pick up just from training materials?

**Engineer:** The nitrogen supply pressure cycling pattern. Facility N2
supply pressure on our line has a mild, regular cycling pattern tied to
demand elsewhere in the fab, and it's more pronounced during the overnight
shift when other systems are drawing from the same header in a different
pattern. The furnace has a "quiet alarm" — a low-priority pressure deviation
alert — that fires more often overnight, and new engineers sometimes treat
every occurrence the same way, investigating it as a potential furnace-side
issue each time.

**Interviewer:** Is it ever a real furnace issue?

**Engineer:** Occasionally, yes, which is exactly what makes it tricky — you
can't just ignore it. But most overnight occurrences of that specific alarm
correlate with the known facility N2 cycling pattern rather than an actual
furnace problem. What experienced engineers do, without it being written
anywhere, is check whether the timing lines up with the facility cycling
pattern first, and only escalate to a furnace-side check if the alarm timing
or duration looks different from that normal pattern. New engineers who
don't know the pattern exists end up escalating every occurrence, which is a
reasonable thing to do without this context, but it uses up response time
that could go to a real issue.

**Interviewer:** Has that pattern ever been documented with facilities?

**Engineer:** Not formally — it's been an informal, tribal thing passed
between whoever's currently working overnight shift on the furnace bay. I
don't think facilities engineering even knows we've been distinguishing
these two cases informally. It really should be a documented distinction
rather than something every new overnight engineer has to rediscover on
their own after a few false-alarm investigations.

**Interviewer:** Anything on the injector drift or boat cracking issues from
the incident logs?

**Engineer:** Only that I'd reinforce the injector drift lesson from
INC-TLVF800-008 specifically — the instinct to suspect a heater first for any
gradual uniformity drift is strong, and understandable, but on this platform
the injector is the more common slow-drift cause. That one is documented now,
but it's the kind of instinct that's easy to fall back into even after
reading it once, if you're not the person who lived through the two weeks it
took to find it the first time.
