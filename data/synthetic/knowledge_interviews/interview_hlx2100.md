---
doc_id: KI-HLX2100-001
equipment: Helios NXP-2100 Lithography Scanner
doc_type: knowledge_capture_interview
title: Exit knowledge-capture interview — Senior Litho Equipment Engineer (rotation ending)
synthetic: true
---

# KI-HLX2100-001: Exit Knowledge-Capture Interview — Litho

**Interviewer:** Is there anything about the scanner's overlay stability that
isn't captured in the calibration procedure?

**Engineer:** There's a cross-tool interaction that took me a long time to
figure out, and it's specific to our sub-fab layout here, not something
that's in any vendor documentation because it depends on which tools happen
to share power distribution with the scanner's facilities feed. When the
etch bay runs a high RF-power recipe on multiple chambers simultaneously —
several AMX-5200 chambers striking high-power plasma close together in time —
there's a small, brief voltage sag on a shared facility circuit that
correlates with a small stage temperature transient on the scanner. It's
usually too small to fail overlay calibration outright, but it adds noise
that can push a marginal calibration over the edge, especially if the stage
is already drifting for an unrelated reason like the chiller setpoint issue
in INC-HLX2100-006.

**Interviewer:** Did anyone else know about this connection?

**Engineer:** A couple of us on the day shift had noticed overlay calibration
seemed to fail slightly more often during certain hours, and eventually one
of the etch engineers and I compared notes and found the correlation with
etch bay activity. It's never been raised with facilities formally, and it's
not written into either tool's SOP, because it's not really an AMX-5200 issue
or a Helios issue on its own — it only shows up as an interaction between the
two, which isn't anyone's single area of ownership on paper.

**Interviewer:** What would you want a new engineer to do with that?

**Engineer:** Mainly, when overlay calibration fails marginally rather than
badly, and stage temperature logs look only slightly off rather than clearly
wrong, it's worth checking whether it coincided with heavy etch bay activity
before spending time on a deeper scanner-side investigation. On its own this
is a minor effect, but it's exactly the kind of thing that gets
re-discovered from scratch every time the people who know it rotate out,
because it doesn't belong cleanly to one team's documentation.

**Interviewer:** Anything else?

**Engineer:** Just that the reticle pod contamination issue from
INC-HLX2100-013 is a much more common cause of a single bad reticle than
people initially assume — I'd want a new engineer to check the pod before
assuming anything is wrong with the reticle itself or the scanner, if the
issue is isolated to one reticle.
