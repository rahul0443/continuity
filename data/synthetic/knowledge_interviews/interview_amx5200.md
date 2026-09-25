---
doc_id: KI-AMX5200-001
equipment: AMX-5200 Plasma Etch System
doc_type: knowledge_capture_interview
title: Exit knowledge-capture interview — Senior Process Engineer, Etch (rotation ending)
synthetic: true
---

# KI-AMX5200-001: Exit Knowledge-Capture Interview — Etch

**Context:** Structured knowledge-capture interview conducted with a senior
process engineer prior to the end of a fixed-term rotational assignment, to
document tacit operating knowledge not already reflected in written
procedures.

**Interviewer:** Before you rotate out, is there anything about the AMX-5200
etch chambers that you rely on day-to-day that isn't written down anywhere?

**Engineer:** Yes, actually — the dry pump. The SOP has you watching chamber
pressure and RF match behavior, which is right, but by the time a failing
foreline pump shows up as a pressure or match problem, you're already close
to a real fault. There's an earlier signal that isn't in any procedure: pump
bearing wear has a distinct change in pitch during the chamber purge cycle,
before idle pumpdown. It's subtle — a slight increase in a higher-frequency
whine during purge, specifically, not during normal pumpdown. Engineers who
have spent a lot of time on the floor next to these chambers pick up on it
without really thinking about it, but nobody ever wrote it down because it's
not something you can put a number on easily.

**Interviewer:** How much lead time does that give you compared to waiting
for a pressure or match signature?

**Engineer:** In my experience, two to three weeks, sometimes more. The
pressure and match signatures the SOP watches for don't show up until the
bearing wear has progressed a lot further. If someone flags that purge-cycle
sound change and schedules a pump inspection proactively, you can usually
catch it before it ever becomes an RF match issue at all — which matters,
because once it does show up as a match issue, it can look exactly like the
match box cooling fan problem from INC-AMX5200-014, and people spend time
ruling that out first before they get to the actual pump.

**Interviewer:** Is there a way to make that less dependent on someone's ear?

**Engineer:** Not really, not with the current instrumentation on this tool
family — there's no vibration or acoustic sensor on the foreline pump that
would catch this automatically. Until there is, the only way this knowledge
transfers is if someone tells the next person, or if it's written down
somewhere a new engineer would actually go looking. That's really the whole
reason I'm mentioning it now — it's exactly the kind of thing that's easy to
forget to pass on in the handover documentation, because it feels too
informal to write in a procedure, but it's one of the most useful things I
know about this chamber.

**Interviewer:** Anything else along those lines?

**Engineer:** One smaller thing — the Level 2 visual buildup threshold in the
SOP viewport check is calibrated for buildup you can see straight-on. Buildup
on the wall opposite the gas injector is harder to see at that viewing angle,
which is exactly what caused INC-AMX5200-021. After a week of heavy
fluorocarbon recipes, it's worth a borescope look at that specific spot even
if the straight-on viewport check looks fine. That one's at least written up
in the incident log now, but the pump sound thing has never been documented
anywhere until this conversation.
