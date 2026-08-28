/** Backend English → conversational English → Hindi */
const PHRASES: [string, string, string][] = [
  [
    "Namaste, I am Civic Sevak. What issue would you like to report?",
    "Namaste, I am Civic Sevak. What issue would you like to report?",
    "नमस्ते, मैं सिविक सेवक हूँ। आप किस समस्या की शिकायत दर्ज करना चाहते हैं?",
  ],
  [
    "Sorry about the pothole on your street — where exactly is it?",
    "Sorry about the pothole on your street — where exactly is it?",
    "आपकी सड़क पर गड्ढे के लिए खेद है — ठीक कहाँ है?",
  ],
  [
    "Sorry you got hurt — please share the exact spot or a nearby landmark.",
    "Sorry you got hurt — please share the exact spot or a nearby landmark.",
    "आपको चोट लगी — खेद है। ठीक स्थान या पास का स्थलचिह्न बताएँ।",
  ],
  [
    "Sorry you got hurt on that pothole — where exactly is it?",
    "Sorry you got hurt on that pothole — where exactly is it?",
    "गड्ढे पर चोट लगी — खेद है। ठीक कहाँ है?",
  ],
  [
    "Sorry you got hurt — where exactly did this happen?",
    "Sorry you got hurt — where exactly did this happen?",
    "आपको चोट लगी — खेद है। यह ठीक कहाँ हुआ?",
  ],
  [
    "Sorry about the pothole — please share the exact spot or a nearby landmark.",
    "Sorry about the pothole — please share the exact spot or a nearby landmark.",
    "गड्ढे के लिए खेद है — ठीक स्थान या पास का स्थलचिह्न बताएँ।",
  ],
  [
    "Sorry about the pothole — where is it?",
    "Sorry about the pothole — where is it?",
    "गड्ढे के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry about the road damage — where is it?",
    "Sorry about the road damage — where is it?",
    "सड़क के नुकसान के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry about the road issue — where is it happening?",
    "Sorry about the road issue — where is it happening?",
    "सड़क की समस्या के लिए खेद है — यह कहाँ हो रही है?",
  ],
  [
    "Sorry your garbage hasn't been collected — which area is this?",
    "Sorry your garbage hasn't been collected — which area is this?",
    "कचरा नहीं उठा — खेद है। यह कौन-सा क्षेत्र है?",
  ],
  [
    "Sorry about the garbage in your area — where exactly?",
    "Sorry about the garbage in your area — where exactly?",
    "आपके इलाके में कचरे के लिए खेद है — ठीक कहाँ?",
  ],
  [
    "Sorry about the garbage pile — where is it?",
    "Sorry about the garbage pile — where is it?",
    "कचरे के ढेर के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry about the garbage issue — where is it?",
    "Sorry about the garbage issue — where is it?",
    "कचरे की समस्या के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry the streetlight outside your home has been out — where is it?",
    "Sorry the streetlight outside your home has been out — where is it?",
    "आपके घर के बाहर स्ट्रीटलाइट बंद है — खेद है। यह कहाँ है?",
  ],
  [
    "Sorry about the streetlight outside your home — where is it?",
    "Sorry about the streetlight outside your home — where is it?",
    "आपके घर के बाहर स्ट्रीटलाइट की समस्या — यह कहाँ है?",
  ],
  [
    "Sorry the streetlight has been off — where is it?",
    "Sorry the streetlight has been off — where is it?",
    "स्ट्रीटलाइट बंद है — खेद है। यह कहाँ है?",
  ],
  [
    "Sorry about the streetlight — where is it?",
    "Sorry about the streetlight — where is it?",
    "स्ट्रीटलाइट की समस्या के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry about the leak near your building — where exactly?",
    "Sorry about the leak near your building — where exactly?",
    "आपकी इमारत के पास रिसाव — खेद है। ठीक कहाँ?",
  ],
  [
    "Sorry about the leak on your street — where exactly?",
    "Sorry about the leak on your street — where exactly?",
    "आपकी सड़क पर रिसाव — खेद है। ठीक कहाँ?",
  ],
  [
    "Sorry about the water leak — where is it?",
    "Sorry about the water leak — where is it?",
    "पानी रिसाव — खेद है। यह कहाँ है?",
  ],
  [
    "Sorry about the sanitation issue in your neighbourhood — where is it?",
    "Sorry about the sanitation issue in your neighbourhood — where is it?",
    "आपके मोहल्ले में स्वच्छता की समस्या — यह कहाँ है?",
  ],
  [
    "Sorry about that — where is the sanitation issue?",
    "Sorry about that — where is the sanitation issue?",
    "स्वच्छता की समस्या — यह कहाँ है?",
  ],
  [
    "Sorry about the sanitation issue — where is it?",
    "Sorry about the sanitation issue — where is it?",
    "स्वच्छता की समस्या के लिए खेद है — यह कहाँ है?",
  ],
  [
    "Sorry about that — where is it happening?",
    "Sorry about that — where is it happening?",
    "खेद है — यह कहाँ हो रहा है?",
  ],
  [
    "I can take road, garbage, streetlight, water, or sanitation complaints. Which one is this?",
    "I can take road, garbage, streetlight, water, or sanitation complaints. Which one is this?",
    "सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता — किसकी शिकायत है?",
  ],
  [
    "I can currently help with road, garbage, streetlight, water, or sanitation issues. Which issue would you like to report?",
    "I can take road, garbage, streetlight, water, or sanitation complaints. Which one is this?",
    "सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता — किसकी शिकायत है?",
  ],
  [
    "I can help with potholes, garbage, streetlights, water leaks, or sanitation issues. Which one would you like to report?",
    "I can take road, garbage, streetlight, water, or sanitation complaints. Which one is this?",
    "सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता — किसकी शिकायत है?",
  ],
  [
    "I'm not sure which service fits. Describe it briefly?",
    "I'm not sure which service fits. Describe it briefly?",
    "सही सेवा स्पष्ट नहीं है। थोड़ा और बताएँ?",
  ],
  [
    "I'm not sure which civic service fits. Could you describe the issue a little more?",
    "I'm not sure which service fits. Describe it briefly?",
    "सही सेवा स्पष्ट नहीं है। थोड़ा और बताएँ?",
  ],
  [
    "Got it — routed to the right service.",
    "Got it — routed to the right service.",
    "ठीक है — सही सेवा पर भेज रहा हूँ।",
  ],
  [
    "I've matched this to the right civic service.",
    "Got it — routed to the right service.",
    "ठीक है — सही सेवा पर भेज रहा हूँ।",
  ],
  [
    "Got it — a road / pothole complaint issue.",
    "Got it — a road issue.",
    "समझ गया — सड़क की समस्या।",
  ],
  [
    "Got it — a garbage accumulation complaint issue.",
    "Got it — a garbage issue.",
    "समझ गया — कचरे की समस्या।",
  ],
  [
    "Got it — a streetlight complaint issue.",
    "Got it — a streetlight issue.",
    "समझ गया — स्ट्रीटलाइट की समस्या।",
  ],
  [
    "Got it — a water leak complaint issue.",
    "Got it — a water leak issue.",
    "समझ गया — पानी रिसाव की समस्या।",
  ],
  [
    "Got it — a sanitation complaint issue.",
    "Got it — a sanitation issue.",
    "समझ गया — स्वच्छता की समस्या।",
  ],
  [
    "I identified this as a",
    "Got it — a",
    "समझ गया —",
  ],
  [
    "Could you share a bit more about the issue?",
    "Could you share a bit more about the issue?",
    "थोड़ा और बताएँ — क्या समस्या है?",
  ],
  [
    "I need a little more detail about the civic issue you want to report.",
    "Could you share a bit more about the issue?",
    "थोड़ा और बताएँ — क्या समस्या है?",
  ],
  [
    "Please check the summary on the right and confirm when ready.",
    "Please check the summary on the right and confirm when ready.",
    "दाईं ओर सार जाँचें और तैयार होने पर पुष्टि करें।",
  ],
  [
    "Please review the details below and confirm submission.",
    "Please check the summary on the right and confirm when ready.",
    "दाईं ओर सार जाँचें और तैयार होने पर पुष्टि करें।",
  ],
  [
    "Please review the completed details below.",
    "Please check the summary and confirm — you can edit any field.",
    "सार जाँचें और पुष्टि करें — कोई भी विवरण बदल सकते हैं।",
  ],
  [
    "Please complete the remaining details.",
    "A few details still needed.",
    "कुछ विवरण अभी बाकी हैं।",
  ],
  [
    "A few details still needed.",
    "A few details still needed.",
    "कुछ विवरण अभी बाकी हैं।",
  ],
  [
    "No form fields were filled from this image. Please complete the remaining details.",
    "Couldn't read details from that photo. Please share what's missing below.",
    "तस्वीर से विवरण नहीं मिले। बाकी जानकारी नीचे दें।",
  ],
  [
    "Have a photo? You can skip.",
    "Have a photo? (Optional)",
    "तस्वीर है? (वैकल्पिक)",
  ],
  [
    "Do you have a photo of this issue?",
    "Have a photo? (Optional)",
    "तस्वीर है? (वैकल्पिक)",
  ],
  [
    "Got it — ",
    "Got it — ",
    "ठीक है — ",
  ],
  [
    "Location selected:",
    "Got it — ",
    "ठीक है — ",
  ],
  [
    "Where is it happening?",
    "Where is it happening?",
    "यह कहाँ हो रहा है?",
  ],
  [
    "Where exactly is the issue?",
    "Where is it happening?",
    "यह कहाँ हो रहा है?",
  ],
  [
    "What happened?",
    "What happened?",
    "क्या हुआ है?",
  ],
  [
    "Please describe the issue.",
    "What happened?",
    "क्या हुआ है?",
  ],
  [
    "How bad is it — low, medium, or high?",
    "How bad is it — low, medium, or high?",
    "कितनी गंभीर है — कम, मध्यम या अधिक?",
  ],
  [
    "How severe is the issue: low, medium, or high?",
    "How bad is it — low, medium, or high?",
    "कितनी गंभीर है — कम, मध्यम या अधिक?",
  ],
  [
    "How long has this been going on?",
    "How long has this been going on?",
    "यह कब से है?",
  ],
  [
    "How long has this been happening?",
    "How long has this been going on?",
    "यह कब से है?",
  ],
  [
    "Pipe, tap, supply, or unsure?",
    "Pipe, tap, supply, or unsure?",
    "पाइप, नल, आपूर्ति, या पता नहीं?",
  ],
  [
    "What kind of leak is it: pipe, tap, supply, or unknown?",
    "Pipe, tap, supply, or unsure?",
    "पाइप, नल, आपूर्ति, या पता नहीं?",
  ],
  [
    "Sewage, drain, hygiene, or other?",
    "Sewage, drain, hygiene, or other?",
    "सीवेज, नाली, स्वच्छता, या अन्य?",
  ],
  [
    "What kind of sanitation issue is it: sewage, drain, public hygiene, or other?",
    "Sewage, drain, hygiene, or other?",
    "सीवेज, नाली, स्वच्छता, या अन्य?",
  ],
  [
    "Know the pole number? Say don't know if not.",
    "Know the pole number? Say don't know if not.",
    "पोल नंबर पता है? नहीं तो 'पता नहीं' कहें।",
  ],
  [
    "Do you know the streetlight pole number? You can say I don't know.",
    "Know the pole number? Say don't know if not.",
    "पोल नंबर पता है? नहीं तो 'पता नहीं' कहें।",
  ],
  [
    "When did you first notice it?",
    "When did you first notice it?",
    "आपने पहली बार कब देखा?",
  ],
  [
    "When did you first notice the issue?",
    "When did you first notice it?",
    "आपने पहली बार कब देखा?",
  ],
  [
    "One more detail, please.",
    "One more detail, please.",
    "एक विवरण और चाहिए।",
  ],
  [
    "Please provide the missing detail.",
    "One more detail, please.",
    "एक विवरण और चाहिए।",
  ],
  [
    "I still need one more detail.",
    "One more detail, please.",
    "एक विवरण और चाहिए।",
  ],
  [
    "Couldn't find that yet. Share a nearby landmark or area.",
    "Couldn't find that yet. Share a nearby landmark or area.",
    "स्थान नहीं मिला। पास का स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Please provide a nearby landmark or area.",
    "Couldn't find that yet. Share a nearby landmark or area.",
    "स्थान नहीं मिला। पास का स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Share a nearby landmark or area.",
    "Share a nearby landmark or area.",
    "पास का स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Please tell me a nearby landmark or area.",
    "Share a nearby landmark or area.",
    "पास का स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Please share a landmark, area, or street.",
    "Please share a landmark, area, or street.",
    "स्थलचिह्न, क्षेत्र या सड़क बताएँ।",
  ],
  [
    "Please provide a recognizable landmark, area, or street.",
    "Please share a landmark, area, or street.",
    "स्थलचिह्न, क्षेत्र या सड़क बताएँ।",
  ],
  [
    "Couldn't find that. Try a landmark and city, or pin it on the map.",
    "Couldn't find that. Try a landmark and city, or pin it on the map.",
    "स्थान नहीं मिला। स्थलचिह्न और शहर लिखें, या मानचित्र पर पिन करें।",
  ],
  [
    "I could not find that place yet. Try an area and city, or drop a pin on the map.",
    "Couldn't find that. Try a landmark and city, or pin it on the map.",
    "स्थान नहीं मिला। स्थलचिह्न और शहर लिखें, या मानचित्र पर पिन करें।",
  ],
  [
    "I could not match that location yet. Please provide a nearby landmark, area, or street.",
    "Couldn't find that yet. Share a nearby landmark or area.",
    "स्थान नहीं मिला। पास का स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Is this the spot — ",
    "Is this the spot — ",
    "क्या यही स्थान है — ",
  ],
  [
    "I found this location:",
    "Is this the spot — ",
    "क्या यही स्थान है — ",
  ],
  [
    "A few matches came up (",
    "A few matches came up (",
    "कुछ स्थान मिले (",
  ],
  [
    "I found more than one possible location (",
    "A few matches came up (",
    "कुछ स्थान मिले (",
  ],
  [
    "). Which one?",
    "). Which one?",
    ")। कौन-सा?",
  ],
  [
    "). Which one is correct?",
    "). Which one?",
    ")। कौन-सा?",
  ],
  [
    "That photo doesn't look relevant to this",
    "That photo doesn't look relevant to this",
    "यह तस्वीर इस",
  ],
  [
    "That photo does not look relevant to this",
    "That photo doesn't look relevant to this",
    "यह तस्वीर इस",
  ],
  [
    "Upload a clearer photo, or choose No image to continue without one.",
    "Upload a clearer photo, or choose No image to continue without one.",
    "साफ़ तस्वीर भेजें, या बिना तस्वीर जारी रखें।",
  ],
  [
    "Please upload a correct photo of the issue, or choose No image to continue without one.",
    "Upload a clearer photo, or choose No image to continue without one.",
    "साफ़ तस्वीर भेजें, या बिना तस्वीर जारी रखें।",
  ],
  [
    "The image appears to be a selfie, not civic evidence.",
    "That looks like a selfie, not evidence of the issue.",
    "यह सेल्फी लगती है, समस्या का साक्ष्य नहीं।",
  ],
  [
    "The image appears relevant to a road issue.",
    "That photo looks relevant to the road issue.",
    "यह तस्वीर सड़क समस्या से जुड़ी लगती है।",
  ],
  [
    "The photo appears relevant to this civic issue.",
    "That photo looks relevant.",
    "यह तस्वीर संबंधित लगती है।",
  ],
  [
    "Image saved as evidence; no field was inferred.",
    "Photo saved as evidence.",
    "तस्वीर साक्ष्य के रूप में सहेजी गई।",
  ],
  [
    "Please upload a relevant civic photo.",
    "Please upload a photo of the issue.",
    "समस्या की तस्वीर अपलोड करें।",
  ],
  [
    "Upload a photo when you're ready.",
    "Upload a photo when you're ready.",
    "तैयार हों तो तस्वीर अपलोड करें।",
  ],
  [
    "Please attach a photo of the issue when you are ready.",
    "Upload a photo when you're ready.",
    "तैयार हों तो तस्वीर अपलोड करें।",
  ],
  [
    "No photo — that's fine. A few details still needed.",
    "No photo — that's fine. A few details still needed.",
    "कोई तस्वीर नहीं — ठीक है। कुछ विवरण बाकी हैं।",
  ],
  [
    "No image added. Please complete the remaining details.",
    "No photo — that's fine. A few details still needed.",
    "कोई तस्वीर नहीं — ठीक है। कुछ विवरण बाकी हैं।",
  ],
  [
    "I can only submit after you review the summary and confirm.",
    "I can only submit after you review and confirm.",
    "सार जाँच और पुष्टि के बाद ही दर्ज होगा।",
  ],
  [
    "I can collect and submit a civic report only after the required review and your explicit confirmation.",
    "I can only submit after you review and confirm.",
    "सार जाँच और पुष्टि के बाद ही दर्ज होगा।",
  ],
  [
    "I can't give legal or response-time advice, but I can lodge your report.",
    "I can't give legal or response-time advice, but I can lodge your report.",
    "कानूनी सलाह या समय की गारंटी नहीं, पर शिकायत दर्ज कर सकता हूँ।",
  ],
  [
    "I can help collect a civic issue report, but I cannot provide legal, eligibility, or guaranteed-response advice.",
    "I can't give legal or response-time advice, but I can lodge your report.",
    "कानूनी सलाह या समय की गारंटी नहीं, पर शिकायत दर्ज कर सकता हूँ।",
  ],
  [
    "I can help with road, garbage, streetlight, water, or sanitation complaints.",
    "I can help with road, garbage, streetlight, water, or sanitation complaints.",
    "सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता की शिकायत में मदद कर सकता हूँ।",
  ],
  [
    "I can help collect a civic issue report using the supported service types.",
    "I can help with road, garbage, streetlight, water, or sanitation complaints.",
    "सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता की शिकायत में मदद कर सकता हूँ।",
  ],
  [
    "Registered. Reference",
    "Registered. Reference",
    "दर्ज हो गया। संदर्भ",
  ],
  [
    "Complaint submitted successfully. Reference:",
    "Registered. Reference",
    "दर्ज हो गया। संदर्भ",
  ],
  [
    "Complaint submitted successfully. Service request",
    "Registered. Service request",
    "दर्ज हो गया। सेवा अनुरोध",
  ],
  [
    "Your complaint was submitted. Reference:",
    "Registered. Reference",
    "दर्ज हो गया। संदर्भ",
  ],
  [
    "Save your access key on the acknowledgement to track it.",
    "Save your access key on the acknowledgement to track it.",
    "ट्रैक करने के लिए पावती की प्रवेश कुंजी सहेजें।",
  ],
  [
    "Save the access key on the acknowledgement to track this request.",
    "Save your access key on the acknowledgement to track it.",
    "ट्रैक करने के लिए पावती की प्रवेश कुंजी सहेजें।",
  ],
  [
    "Updated. ",
    "Updated. ",
    "अपडेट किया। ",
  ],
  [
    "Updated ",
    "Updated. ",
    "अपडेट किया। ",
  ],
  ["Is that correct?", "Is that correct?", "क्या यह सही है?"],
  ["Uploaded an image.", "Photo uploaded.", "तस्वीर अपलोड की।"],
  ["road / pothole complaint", "road issue", "सड़क समस्या"],
  ["garbage accumulation complaint", "garbage issue", "कचरा समस्या"],
  ["streetlight complaint", "streetlight issue", "स्ट्रीटलाइट समस्या"],
  ["water leak complaint", "water issue", "पानी समस्या"],
  ["sanitation complaint", "sanitation issue", "स्वच्छता समस्या"],
];

export function localizeAgentText(text: string, hindi: boolean): string {
  if (!text) return text;
  let localized = text;
  for (const [english, conversational, hindiText] of PHRASES) {
    const replacement = hindi ? hindiText : conversational;
    if (localized.includes(english)) localized = localized.split(english).join(replacement);
  }
  return localized;
}
