---
doc_id: KI-ORB7-001
equipment: Orbis CMP-7 Polisher
doc_type: knowledge_capture_interview
title: Exit knowledge-capture interview — Senior Process Engineer, CMP (rotation ending)
synthetic: true
---

# KI-ORB7-001: Exit Knowledge-Capture Interview — CMP

**Interviewer:** What's something about the CMP process here that a new
engineer wouldn't know from the procedures alone?

**Engineer:** Slurry lot variability tied to shipping season. Our slurry
supplier ships from a facility that isn't climate-controlled in transit, and
during the hottest summer shipping weeks, we've seen a slightly higher
lot-to-lot particle concentration variability than the rest of the year, even
though every lot still passes the incoming QC certificate. It's within spec
on paper, lot by lot, but the tails are a bit fatter in summer.

**Interviewer:** How does that show up on the tool?

**Engineer:** Mostly as slightly higher day-to-day variability in adder
counts at the post-CMP clean check, without a clear single cause. It's easy
to chase that as a tool issue — pad conditioning, slurry line purge, brush
box performance — and rule all of those out one by one, when the actual
driver is just which slurry lot happened to be in use that day. I don't have
this formally connected to the supplier's shipping records; it's a pattern I
noticed by cross-referencing our own lot change log against our particle
trend charts over about eighteen months.

**Interviewer:** Is there anything practical a new engineer should do with
that, or is it more just useful context?

**Engineer:** Practically: if adder counts are trending noisy in summer
without an obvious tool-side cause, it's worth checking which slurry lot is
in use and whether the noisy days correlate with a lot change, before
spending a lot of time re-checking pad conditioning and slurry line
qualification that were probably fine to begin with. That's the main time
cost — people re-verify things that already passed, because the actual
variable isn't visible from the tool side at all.

**Interviewer:** Anything about retaining ring wear, since that's come up in
the incident logs?

**Engineer:** Just that I'd treat INC-ORB7-011 as the more important lesson
of the two things I've mentioned, if you can only pass one along. Retaining
ring wear is a real, direct root cause with a fix. The slurry seasonality
thing is more of a "don't waste time chasing the wrong variable" heuristic —
useful, but softer. I wanted both on the record, but the ring wear one is the
one I'd make sure isn't lost.
