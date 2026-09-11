# Communication technology review, 11 September 2026

This review covers the overview’s eye trackers, head trackers, free software, mobile apps and BCI profiles, plus the BCI profiles on the research page. The remaining research catalogue was not comprehensively re-audited in this pass. Verified Solutions, the separate setup guides, embedded setup modals, low-tech content and spatial alphabet system were preserved against a pre-edit snapshot.

Follow-up on 11 September: at the user's explicit request, the original Tobii Eye Tracker 4C and Eye Tracker 5 records were restored from the repository's pre-review content, including caregiver notes, reference prices, availability and setup information. The current cards identify those prices as community references to confirm with the seller, rather than newly verified quotations. This supersedes the initial audit's changes to those two cards below; the other device data and protected setup content are unchanged. Four rendering tests pass, including coverage of the restored price fields and original compatibility wording.

## Material corrections

- Tobii Eye Tracker 5: US$339 published standard price; the site also displayed a US$271 promotion on the review date. Removed the claim that a beta driver makes it a supported Windows Eye Control device. [Tobii](https://gaming.tobii.com/product/eye-tracker-5/)
- OptiKey: current v4 excludes Tobii 4C and Eye Tracker 5; Classic v3 remains the relevant branch. The overview no longer describes OptiKey itself as a webcam tracker. [Version guide](https://optikey.org/help/versions)
- Used 4C and specialist AAC systems: removed unverified fixed USD/INR estimates. Display variable used pricing or request a quote. Clarified current TD I-16 naming and individual assessment for Eyegaze Edge.
- Head trackers: retained GlassOuse V1.4 (manufacturer lists US$599) and HeadMouse Nano as two different access methods. Reviewed GlassOuse PRO but omitted it to simplify the shortlist, not because it was shown to be unreliable. [GlassOuse](https://glassouse.com/product/glassouse-v1-4-assistive-device/), [HeadMouse](https://www.orin.com/access/headmouse/), [PRO](https://glassouse.com/product/glassouse-pro/)
- Camera Mouse: a real historical project, but its official download site timed out during review. Removed it from the current shortlist rather than sending users to unofficial installer mirrors. No claim that the project never existed.
- eViacam: retained because the official project, documentation and Linux packaging exist; explicitly labelled the Windows release as legacy. GazePointer is also labelled legacy and non-commercial rather than unrestricted open source. [eViacam](https://eviacam.crea-si.com/), [GazePointer](https://sourceforge.net/projects/gazepointer/)
- Project Relate: Google currently says no new sign-ups, while existing users can retain access. Replaced obsolete Assistant claims with the currently described transcription, repetition and keyboard functions. [Google](https://sites.research.google/relate/)
- Avaz: official India plans are ₹299/month, ₹2,999/year or ₹11,999 lifetime, with a 14-day trial. Corrected the combined iOS app arrangement. [Avaz pricing](https://avazapp.freshdesk.com/support/solutions/articles/1000213047-what-is-the-price-of-avaz-india-)
- Look to Speak: added the actual Play Store link and dated its last listed update. Added Apple Live Speech as a separate text-to-speech option, and clarified that Apple Eye Tracking is an input method. Each card links its official requirements.
- BCI: replaced commercial availability/cost forecasts with dated sponsor information, added VOICE and Connect-One developments, and separated Precision’s component clearance from approval of a complete BCI. Cognixion Axon-R is labelled research-use only. The overview and research page now use the same underlying BCI records. [Neuralink VOICE](https://neuralink.com/trials/speech-restoration/), [Paradromics updates](https://paradromics.com/news/), [Synchron](https://synchron.com/), [BrainGate](https://www.braingate.org/research-areas/speech-restoration/), [Precision](https://www.precisionneuro.io/), [Cognixion](https://www.cognixion.com/)

## Presentation and behaviour

Scoped communication styles introduce an editorial hero, a more visible translucent 3D signal sphere, quieter navigation, refined card typography, full compatibility notes, price qualifications and source links. The section order and protected content stay intact. Unsupported community rating dots were removed from the reviewed comparisons.

The animation remains decorative and independent of the content. It pauses offscreen, in hidden tabs and on user request, honours reduced motion and Save-Data, and disposes its graphics on exit or WebGL failure. It does not depict actual anatomy or device performance.

## Validation and limits

- Eleven targeted JavaScript tests passed for complete data rendering, source escaping, API failure handling, scene geometry, camera framing and animation lifecycle.
- Both changed pages rendered through Flask; local navigation and referenced local assets returned HTTP 200. The research page rendered all six BCI profiles.
- Protected template sections and low-tech data matched the pre-edit snapshot exactly.
- Checked 36 distinct external source URLs directly: 33 returned HTTP 200 with no challenge redirect, Debian returned a challenge page, and the two Tobii Dynavox US URLs failed DNS resolution from this machine. Tobii Dynavox product content and the Debian package were independently retrieved through web research. These are verification limits, not proof that the websites are unavailable to visitors.
- No physical devices or app installations were tested. Published features, store availability and study eligibility can change. Quote-only prices intentionally avoid an invented India landed cost.
- No browser visual inspection was performed in this pass.
