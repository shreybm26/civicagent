/** Backend English → conversational English → Hindi */
const PHRASES: [string, string, string][] = [
  [
    "Namaste, I am Civic Sevak. What issue would you like to report?",
    "Namaste, I am Civic Sevak. What issue would you like to report?",
    "नमस्ते, मैं सिविक सेवक हूँ। आप किस समस्या की शिकायत दर्ज करना चाहते हैं?",
  ],
  [
    "Namaste. Please describe the civic issue you want to report. I will collect the required details and show you a review form before anything is submitted.",
    "Namaste, I am Civic Sevak. What issue would you like to report?",
    "नमस्ते, मैं सिविक सेवक हूँ। आप किस समस्या की शिकायत दर्ज करना चाहते हैं?",
  ],
  [
    "I can currently help with road, garbage, streetlight, water, or sanitation issues. Which issue would you like to report?",
    "I can help with road, garbage, streetlight, water, or sanitation issues. Which one should we report?",
    "मैं सड़क, कचरा, स्ट्रीटलाइट, पानी या स्वच्छता की शिकायत में मदद कर सकता हूँ। आप कौन-सी समस्या बताना चाहते हैं?",
  ],
  [
    "I can help with potholes, garbage, streetlights, water leaks, or sanitation issues. Which one would you like to report?",
    "I can help with potholes, garbage, streetlights, water leaks, or sanitation issues. Which one should we report?",
    "मैं गड्ढे, कचरा, स्ट्रीटलाइट, पानी रिसाव या स्वच्छता की शिकायत में मदद कर सकता हूँ। आप किसके बारे में बताना चाहते हैं?",
  ],
  [
    "I’m not sure which civic service fits. Could you describe the issue a little more?",
    "I’m not sure which service fits yet. Could you describe the issue a little more?",
    "मुझे अभी स्पष्ट नहीं है कि यह किस सेवा में आता है। कृपया समस्या थोड़ा और बताएँ।",
  ],
  [
    "I’ve matched this to the right civic service.",
    "I’ve matched this to the right civic service.",
    "यह शिकायत सही नागरिक सेवा से मिला दी गई है।",
  ],
  [
    "I need a little more detail about the civic issue you want to report.",
    "I need a little more detail about the issue. What else can you tell me?",
    "कृपया समस्या के बारे में थोड़ा और बताएँ।",
  ],
  [
    "Please review the details below and confirm submission.",
    "Please review the application summary on the right and confirm when you are ready.",
    "कृपया दाईं ओर आवेदन सार जाँचें और तैयार होने पर पुष्टि करें।",
  ],
  [
    "Please review the completed details below.",
    "I recorded what I could from your photo. Please review the application summary — you can change any suggested value.",
    "मैंने तस्वीर से जो समझा वह दर्ज कर लिया। कृपया आवेदन सार जाँचें — आप कोई भी सुझाव बदल सकते हैं।",
  ],
  [
    "Please complete the remaining details.",
    "I still need a few details. You can answer below, and you can change anything later in the summary.",
    "कुछ विवरण अभी बाकी हैं। नीचे बताएँ; बाद में आवेदन सार में भी बदल सकते हैं।",
  ],
  [
    "No form fields were filled from this image. Please complete the remaining details.",
    "I could not fill form fields from this image. Please share the remaining details below — you can edit them later in the summary.",
    "इस तस्वीर से फ़ॉर्म नहीं भरा जा सका। कृपया बाकी विवरण नीचे दें — बाद में सार में बदल सकते हैं।",
  ],
  [
    "Do you have a photo of this issue?",
    "Do you have a photo of this issue? You can skip if you prefer.",
    "क्या आपके पास इस समस्या की तस्वीर है? चाहें तो छोड़ भी सकते हैं।",
  ],
  [
    "Location selected:",
    "I’ve recorded the location:",
    "मैंने स्थान दर्ज कर लिया:",
  ],
  ["Where exactly is the issue?", "Where exactly is the issue?", "समस्या ठीक कहाँ है?"],
  ["Please describe the issue.", "Please describe the issue.", "कृपया समस्या का वर्णन करें।"],
  [
    "How severe is the issue: low, medium, or high?",
    "How severe is the issue: low, medium, or high?",
    "समस्या कितनी गंभीर है: कम, मध्यम या अधिक?",
  ],
  ["How long has this been happening?", "How long has this been happening?", "यह समस्या कितने समय से है?"],
  [
    "What kind of leak is it: pipe, tap, supply, or unknown?",
    "What kind of leak is it: pipe, tap, supply, or unknown?",
    "यह किस तरह का रिसाव है: पाइप, नल, आपूर्ति, या अज्ञात?",
  ],
  [
    "What kind of sanitation issue is it: sewage, drain, public hygiene, or other?",
    "What kind of sanitation issue is it: sewage, drain, public hygiene, or other?",
    "यह किस तरह की स्वच्छता समस्या है: सीवेज, नाली, सार्वजनिक स्वच्छता, या अन्य?",
  ],
  [
    "Do you know the streetlight pole number? You can say I don't know.",
    "Do you know the streetlight pole number? You can say you don’t know.",
    "क्या आपको स्ट्रीटलाइट का पोल नंबर पता है? नहीं पता हो तो कह सकते हैं।",
  ],
  ["When did you first notice the issue?", "When did you first notice the issue?", "आपने यह समस्या पहली बार कब देखी?"],
  ["Please provide the missing detail.", "I still need one missing detail.", "कृपया बाकी विवरण दें।"],
  ["I still need one more detail.", "I still need one more detail.", "एक विवरण और चाहिए।"],
  [
    "Please provide a nearby landmark or area.",
    "Please share a nearby landmark or area.",
    "कृपया पास का कोई स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Please tell me a nearby landmark or area.",
    "Please tell me a nearby landmark or area.",
    "कृपया पास का कोई स्थलचिह्न या क्षेत्र बताएँ।",
  ],
  [
    "Please provide a recognizable landmark, area, or street.",
    "Please share a recognizable landmark, area, or street.",
    "कृपया कोई जाना-माना स्थलचिह्न, क्षेत्र या सड़क बताएँ।",
  ],
  [
    "I could not match that location yet. Please provide a nearby landmark, area, or street.",
    "I could not match that location yet. Please share a nearby landmark, area, or street.",
    "यह स्थान अभी नहीं मिला। कृपया पास का स्थलचिह्न, क्षेत्र या सड़क बताएँ।",
  ],
  [
    "I could not find that place yet. Try an area and city, or drop a pin on the map.",
    "I could not find that place yet. Try an area and city, like Junnasandra, Bengaluru, or drop a pin on the map.",
    "यह स्थान अभी नहीं मिला। क्षेत्र और शहर लिखें, या मानचित्र पर पिन डालें।",
  ],
  [
    "The image appears to be a selfie, not civic evidence.",
    "That photo looks like a selfie, not civic evidence.",
    "यह फ़ोटो सेल्फी लगती है, नागरिक साक्ष्य नहीं।",
  ],
  [
    "The image appears relevant to a road issue.",
    "That photo looks relevant to a road issue. I’ve suggested details you can change.",
    "यह फ़ोटो सड़क समस्या से संबंधित लगती है। मैंने सुझाव भरे हैं जिन्हें आप बदल सकते हैं।",
  ],
  [
    "The photo appears relevant to this civic issue.",
    "That photo looks relevant. I’ve suggested details you can change in the summary.",
    "यह फ़ोटो संबंधित लगती है। मैंने सुझाव भरे हैं जिन्हें आप सार में बदल सकते हैं।",
  ],
  [
    "Image saved as evidence; no field was inferred.",
    "I’ve saved the photo as evidence. No form fields were filled from it.",
    "फ़ोटो साक्ष्य के रूप में सहेज ली गई; कोई फ़ील्ड नहीं निकाला गया।",
  ],
  [
    "Please upload a relevant civic photo.",
    "Please upload a relevant photo of the issue.",
    "कृपया समस्या की प्रासंगिक फ़ोटो अपलोड करें।",
  ],
  [
    "No image added. Please complete the remaining details.",
    "No image added. I’ll ask for the remaining details next.",
    "कोई तस्वीर नहीं जोड़ी गई। अब बाकी विवरण पूछूँगा।",
  ],
  [
    "Please attach a photo of the issue when you are ready.",
    "Please attach a photo of the issue when you are ready.",
    "जब आप तैयार हों, समस्या की तस्वीर जोड़ें।",
  ],
  [
    "I can collect and submit a civic report only after the required review and your explicit confirmation.",
    "I can submit only after you review the summary and confirm.",
    "समीक्षा और आपकी स्पष्ट पुष्टि के बाद ही शिकायत दर्ज होगी।",
  ],
  [
    "I can help collect a civic issue report, but I cannot provide legal, eligibility, or guaranteed-response advice.",
    "I can help you lodge a report, but I cannot give legal advice or response guarantees.",
    "मैं शिकायत दर्ज करने में मदद कर सकता हूँ, लेकिन कानूनी सलाह या समय की गारंटी नहीं दे सकता।",
  ],
  [
    "I can help collect a civic issue report using the supported service types.",
    "I can help lodge a report for the supported service types.",
    "मैं निर्धारित सेवा प्रकारों में नागरिक शिकायत दर्ज करने में मदद कर सकता हूँ।",
  ],
  ["Is that correct?", "Is that correct?", "क्या यह सही है?"],
  ["Which one is correct?", "Which one is correct?", "कौन-सा सही है?"],
  ["I found this location:", "I found this location:", "यह स्थान मिला:"],
  ["I found more than one possible location", "I found more than one possible location", "एक से अधिक संभावित स्थान मिले"],
  ["I can help report this", "I can help report this", "मैं यह दर्ज कर सकता हूँ:"],
  ["I identified this as a", "I’ve identified this as a", "यह सेवा पहचानी गई:"],
  [
    "Complaint submitted successfully. Reference:",
    "Your complaint was submitted. Reference:",
    "शिकायत दर्ज हो गई है। संदर्भ:",
  ],
  [
    "Complaint submitted successfully. Service request",
    "Your complaint was submitted. Service request",
    "शिकायत दर्ज हो गई है। सेवा अनुरोध",
  ],
  [
    "Save the access key on the acknowledgement to track this request.",
    "Save the access key on the acknowledgement to track this request.",
    "आवेदन ट्रैक करने के लिए पावती पर दी गई प्रवेश कुंजी सहेजें।",
  ],
  ["Updated ", "I’ve updated ", "मैंने अपडेट किया: "],
  ["Uploaded an image.", "I uploaded an image.", "मैंने एक तस्वीर अपलोड की।"],
  ["road / pothole complaint", "road / pothole complaint", "सड़क / गड्ढा शिकायत"],
  ["garbage accumulation complaint", "garbage accumulation complaint", "कचरा जमाव शिकायत"],
  ["streetlight complaint", "streetlight complaint", "स्ट्रीटलाइट शिकायत"],
  ["water leak complaint", "water leak complaint", "पानी रिसाव शिकायत"],
  ["sanitation complaint", "sanitation complaint", "स्वच्छता शिकायत"],
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
