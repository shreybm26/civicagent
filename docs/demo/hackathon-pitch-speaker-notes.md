# Civic Sevak — Hackathon Pitch Speaker Notes

**Runtime target:** exactly **2:00**  
**Format:** split presenters (citizen demo → architecture)  
**Record against:** the **deployed public URL** (English UI, desktop two-column)  
**Photo:** the NEXUS FORUM pothole image (mall sign visible in frame)

---

## TITLE

**It Can Suggest. It Cannot Submit.**

---

## CENTRAL IDEA

A citizen should not have to speak bureaucracy. The system should not be allowed to speak for them.

### Punchlines (four — earned, then pause)

1. Opening: *To report a pothole, a citizen still has to speak bureaucracy.*
2. Mid-demo: *I have not picked a department.* / *High. Landmark. I typed none of that.*
3. Architecture: *It can suggest from the photo. It cannot submit.*
4. Close: the central idea — then silence on the tracked record.

---

## PERFORMANCE PRINCIPLE

Presenter 1 is almost documentary — few words, long looks at the screen, silence while Civic Sevak streams and vision runs. Presenter 2 is the Slide-4 voice from the old speaker notes: design question, naive failure, then the insight as if it were inevitable. Lower the voice on punchlines. Never fill a pause. Hold the tracked record at the end. No celebrity impressions. No catchphrases. Sound like people who built the brakes.

---

## TIMED SCRIPT

### 00:00–00:06 — Opening

**WHO:** Presenter 1  
**SPOKEN:**

> To report a pothole, a citizen still has to speak bureaucracy.

`[Look at camera]`  
`[Pause — 0.8s]`  
`[Lower voice]`

**ON SCREEN:**  
Lodge grievance. Welcome already visible: *Namaste, I am Civic Sevak…* Suggestion chips (Pothole, Garbage, Streetlight…). Do **not** click yet. Application summary empty / service not identified.

---

### 00:06–00:14 — One sentence

**WHO:** Presenter 1  
**SPOKEN:**

> Not here.  
> `[Look at screen]`  
> Watch.

`[Pause — 0.3s]` then click.

**ON SCREEN / ACTIONS:**

1. Click **Pothole** (sends: *There is a pothole on my street*).
2. Wait for the agent stream to **finish** (widgets stay hidden until then).
3. Status → **Collecting details**.
4. Application summary → **Road / Pothole Complaint**; Description filled; Location / Severity **Pending**.

Do **not** point at Application ref. (that is the session UUID prefix).

---

### 00:14–00:28 — Location (mostly silence)

**WHO:** Presenter 1  
**SPOKEN:**

> I have not picked a department.

`[Pause — 0.5s]`  
Then silence for the map.

**ON SCREEN / ACTIONS:**

1. Click **Location**.
2. Click map → drop pin (Hyderabad tiles).
3. Click **Confirm location**.
4. Agent: *I've recorded the location: Pinned location (…).* *Do you have a photo…*

Coordinates will differ each take. Do not apologize for `Pinned location (lat, lng)`.

**Emergency (do not narrate):** if map stalls >8s → type `near JNTU metro` → **Use landmark**.

---

### 00:28–00:46 — Photo + vision (the magic)

**WHO:** Presenter 1  
**SPOKEN:**

> One photo.

`[Look at screen]`  
`[Pause — 0.4s]`  
Then **silence** through upload and stream. Do not talk over analysis.

**ON SCREEN / ACTIONS:**

1. Click **Add image** → select the NEXUS FORUM pothole photo.
2. Citizen bubble: thumbnail + *Uploaded an image.*
3. Activity: *Checking the image* (wait).
4. Agent streams (let it finish):  
   *The image clearly shows a large pothole on a road… I recorded what I could from your photo.*
5. **Review and confirmation** appears with:
   - Severity **High** selected  
   - Landmark **NEXUS FORUM**  
   - Additional details (water / depth / vehicle risk)  
   - Photo: Image attached  
6. Cursor hovers **High**, then **NEXUS FORUM**. Do not read the form aloud.

**Emergency (do not narrate):** if **One more detail** appears → tap **high** → **Save**.

---

### 00:46–00:54 — Confirm

**WHO:** Presenter 1  
**SPOKEN:**

> High. Landmark. I typed none of that.  
> `[Pause — 0.4s]`  
> And I still have to say yes.

`[Lower voice on “I typed none of that.”]`  
`[Emphasis on “still”]`

**ON SCREEN / ACTIONS:**

1. After the short line, click **Submit grievance**.
2. Fine print is visible: *This is a demo acknowledgement…* — do not narrate it.
3. Land on **Acknowledgement** / *Grievance registered*.
4. Point (cursor only) at **Service request ID** and **Access key** — never Application ref.

---

### 00:54–01:00 — The key (handoff setup)

**WHO:** Presenter 1  
**SPOKEN:** *(none — or at most a breath)*

**ON SCREEN / ACTIONS:**

1. Click **Copy** on **Access key** (required — Track does **not** prefill it).
2. Click **Track this request**.
3. Land on `/track` with Service request ID filled, access key field empty.
4. Presenter 1 stops. Presenter 2 takes over.

Never click **Lodge another grievance** (wipes the session). Never retype the key (copy only — one bad take showed EXHN vs EXHW).

---

### 01:00–01:10 — Proof it persisted

**WHO:** Presenter 2  
**SPOKEN:**

> This is not a toast.  
> Same record. Same landmark.

`[Look at screen]`  
`[Pause — 0.5s after “toast”]`

**ON SCREEN / ACTIONS:**

1. Paste access key.
2. Click **View status**.
3. Status card: **Received** · **Roads & Infrastructure** · filed fields including **NEXUS FORUM**.
4. Timeline: Received done; Department review — *Not connected to a live department…*
5. Hold 1–2 seconds. Let them see it.

---

### 01:10–01:42 — Why we built it this way

**WHO:** Presenter 2  
**SPOKEN:**

> A naive chatbot would look at that photo, invent a department, and file.  
> That is how a wrong complaint enters a real queue.  
> `[Pause — 0.6s]`  
> We did not build that.  
> `[Slow down]`  
> The conversation proposes. The schema decides what is required. The state machine decides what is legal next. The citizen is the only one who can confirm. Done means a receipt — and a key that can fetch the record.

`[Look at camera on “We did not build that.”]`  
`[Look at screen on the inventory of brakes]`

**ON SCREEN:** Stay on the tracked status card (or cut back briefly to a freeze of Review / Submit if you need visual contrast). Do not open code.

---

### 01:42–01:52 — Honesty + scale

**WHO:** Presenter 2  
**SPOKEN:**

> Image analysis is live. Municipal submission is mocked. The contract is real.  
> `[Pause — 0.4s]`  
> Five services. One graph. A live municipal API replaces the adapter — not the workflow.

`[Lower voice on “The contract is real.”]`

**ON SCREEN:** Tracked record still visible. Disclaimer on page already says demo — do not recite it.

**Optional (only if both teammates confirm Codex was a real build tool):** after “The contract is real,” add one clause — *We built this with Codex.* — then continue. If unsure, **omit**. Never say the product is “powered by OpenAI.”

---

### 01:52–02:00 — Close

**WHO:** Presenter 2  
**SPOKEN:**

> It can suggest from the photo.  
> It cannot submit.  
> `[Pause — 0.5s]`  
> `[Lower voice]` `[Slow down]`  
> A citizen should not have to speak bureaucracy.  
> The system should not be allowed to speak for them.

`[Hold]` on the tracked status card.  
Do **not** say thank you over the last frame.  
Silence until **2:00**. Cut.

---

## DELIVERY NOTES

### Split handoff

| Window | Owner | Energy |
| --- | --- | --- |
| 0:00–1:00 | Presenter 1 | Quiet, citizen, screen-first |
| 1:00–2:00 | Presenter 2 | Controlled, engineer, failure-mode → insight |

Handoff happens the instant `/track` loads with the SR ID filled. Presenter 2 should already have the clipboard or paste ready.

### Where to look

- **Camera:** opening line; “We did not build that.”; both closing sentences.
- **Screen:** every click; vision wait; hover on High / NEXUS FORUM; acknowledgement credentials; track result.

### Where to slow down

- “We did not build that.”
- The five-brake inventory (propose / schema / state machine / citizen / receipt+key).
- Final two sentences.

### Where to pause (mandatory)

- After the opening bureaucracy line.
- After “One photo.” (vision must own the next ~15s).
- After “I typed none of that.”
- After “This is not a toast.”
- After “We did not build that.”
- After “It cannot submit.”
- Final hold — no speech.

### What to emphasize

- **not** in “Not here.”
- **none** in “I typed none of that.”
- **still** in “I still have to say yes.”
- **cannot** in “It cannot submit.”
- **not be allowed** in the closing thesis.

### What not to overact

- Do not celebrate when High fills — understatement.
- Do not sell the map.
- Do not apologize for pinned coordinates or the prototype banner.
- Do not explain buttons the viewer can read.
- No upward inflection on declaratives.

### Pre-roll checklist

- [ ] Deployed URL open, English, desktop width (≥760px so summary stays beside chat)
- [ ] **Reset application** or fresh session
- [ ] NEXUS FORUM pothole photo ready in the file picker
- [ ] OSM tiles pre-warmed (open Location once before recording if needed)
- [ ] Clipboard empty; practice Copy → Track → paste once
- [ ] Both mics; Presenter 2 standing by at 0:54

---

## DEMO CUE SHEET

| Time | Action |
| --- | --- |
| 00:00 | Start recording. Full Lodge grievance page visible. Do not click. |
| 00:06 | Presenter 1: “Not here. Watch.” |
| 00:07 | Click **Pothole**. Wait for stream to finish. |
| 00:10 | Confirm Application summary shows **Road / Pothole Complaint** + description. |
| 00:14 | “I have not picked a department.” Click **Location**. |
| 00:16 | Pin map. Click **Confirm location**. Wait for photo prompt. |
| 00:28 | “One photo.” Click **Add image**. Select NEXUS FORUM photo. |
| 00:30–00:45 | Silence. Wait for *I recorded what I could from your photo.* Review card: **High** + **NEXUS FORUM**. Hover both. |
| 00:46 | “High. Landmark. I typed none of that.” Pause. “And I still have to say yes.” |
| 00:50 | Click **Submit grievance**. |
| 00:52 | Acknowledgement visible. Cursor on Service request ID + Access key. |
| 00:54 | **Copy** Access key. Click **Track this request**. |
| 01:00 | Presenter 2: “This is not a toast…” Paste key. **View status**. |
| 01:08 | Hold tracked record (Received / Roads & Infrastructure / NEXUS FORUM). |
| 01:10 | Architecture: naive chatbot → brakes → honesty → scale. |
| 01:52 | Punchline: suggest / cannot submit. Thesis. |
| 02:00 | Hold. Cut. Silence. |

### Emergency cuts (silent — never narrate)

| Failure | Fix |
| --- | --- |
| Map / Nominatim stall | **Use landmark** → `near JNTU metro` |
| Vision misses severity | **high** → **Save** |
| Vision too slow | Submit the instant Review enables; shorten P2 by cutting the “Five services…” line if needed |
| Copy button fails | Select key text → Ctrl+C |
| Wrong key / 401 | Stop take; never guess characters |
| Accidental **Lodge another grievance** | Abort take |

---

## TIMING AUDIT

| Bucket | Duration | Notes |
| --- | --- | --- |
| Spoken (Presenter 1) | ~22–24s | ~40 words at deliberate pace |
| Spoken (Presenter 2) | ~38–40s | ~128 words at deliberate pace |
| Marked pauses | ~7s | opening, toast, typed-none, “did not build,” “cannot submit,” holds |
| Demo silence / UI wait | ~49–53s | stream, map, vision, submit, nav, paste |
| **Total** | **120s** | Do not “speak faster.” Cut words if vision runs long. |

### Spoken word count (final script)

**Presenter 1 (~40 words):**

> To report a pothole, a citizen still has to speak bureaucracy. Not here. Watch. I have not picked a department. One photo. High. Landmark. I typed none of that. And I still have to say yes.

**Presenter 2 (~128 words):**

> This is not a toast. Same record. Same landmark. A naive chatbot would look at that photo, invent a department, and file. That is how a wrong complaint enters a real queue. We did not build that. The conversation proposes. The schema decides what is required. The state machine decides what is legal next. The citizen is the only one who can confirm. Done means a receipt — and a key that can fetch the record. Image analysis is live. Municipal submission is mocked. The contract is real. Five services. One graph. A live municipal API replaces the adapter — not the workflow. It can suggest from the photo. It cannot submit. A citizen should not have to speak bureaucracy. The system should not be allowed to speak for them.

**Total spoken words:** ~168  
**Estimated speaking duration:** ~52–55s (deliberate pitch pace with emphasis)  
**Total pause duration:** ~7s marked + micro-pauses ≈ 9s  
**Demo silence / interaction:** ≈ 56–59s  
**Total runtime:** **2:00**

Word count is intentionally below a “full talk” 240 — map + vision + track must own the clock. If vision regularly exceeds ~15s in rehearsal, cut Presenter 1’s “Watch.” and Presenter 2’s “Five services. One graph…” line first — keep “I typed none of that,” the punchline, and the thesis intact.

---

## WHY THIS NARRATIVE (vs the alternatives)

Five concepts were evaluated. This one won.

| Concept | Why not (or why only as support) |
| --- | --- |
| Bureaucracy → conversation | True, but generic across ~2,000 civic-AI entries |
| One pothole → complete action | Strong demo spine; thin as a thesis alone |
| Chatbot vs civic agent | Excellent for minute 2; weak as the cold open |
| Human language → government structure | Accurate; too abstract without the confirm brake |
| Trustworthy public-service AI | Sounds like the slop this pitch forbids |

**Selected:** *A citizen should not have to speak bureaucracy. The system should not be allowed to speak for them.*

Minute 1 proves the first sentence on camera (plain speech, no department pick, photo fills High + NEXUS FORUM, citizen still confirms, real key, track lookup). Minute 2 proves the second (naive chatbot failure mode → schema / state / confirm / receipt). Together they mark Civic Sevak as a civic intake system with brakes — not a chat wrapper — while staying honest that municipal submission is mocked and image analysis is live.

---

## FACTS LOCK (do not drift in the take)

| Claim | Status |
| --- | --- |
| Live image analysis on deploy | Yes — show it |
| Severity / landmark / details from photo | Yes — High + NEXUS FORUM |
| Citizen must click Submit | Yes — no auto-submit |
| Real CIV id + one-time access key | Yes — copy, don’t retype |
| `/track` returns the filed record | Yes — status Received |
| Live government / GHMC / Open311 | **No** — mocked adapter |
| Application ref. = ticket | **No** — ignore it |
| Codex as runtime | **No** — optional build-tool mention only |
| Conflict-resolution engine | **No** — not wired |

Record on the **public deploy**. Desktop. English. Same photo every take.
