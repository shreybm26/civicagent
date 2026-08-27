const PHRASES: [string, string][] = [
  [
    "Namaste. Please describe the civic issue you want to report. I will collect the required details and show you a review form before anything is submitted.",
    "नमस्ते। कृपया बताएँ कि आप कौन-सी नागरिक समस्या दर्ज करना चाहते हैं। मैं आवश्यक विवरण एकत्र करूँगा और प्रस्तुत करने से पहले समीक्षा फ़ॉर्म दिखाऊँगा।",
  ],
  [
    "I can currently help with road, garbage, streetlight, water, or sanitation issues. Which issue would you like to report?",
    "मैं सड़क, कचरा, स्ट्रीटलाइट, पानी रिसाव या स्वच्छता की शिकायत दर्ज कर सकता हूँ। आप कौन-सी समस्या बताना चाहते हैं?",
  ],
  [
    "I can help with potholes, garbage, streetlights, water leaks, or sanitation issues. Which one would you like to report?",
    "मैं गड्ढे, कचरा, स्ट्रीटलाइट, पानी रिसाव या स्वच्छता की शिकायत दर्ज कर सकता हूँ। आप किस बारे में बताना चाहते हैं?",
  ],
  [
    "I’m not sure which civic service fits. Could you describe the issue a little more?",
    "मुझे स्पष्ट नहीं है कि यह किस सेवा में आता है। कृपया समस्या थोड़ा और बताएँ।",
  ],
  ["I’ve matched this to the right civic service.", "यह शिकायत सही नागरिक सेवा से मिला दी गई है।"],
  ["I need a little more detail about the civic issue you want to report.", "कृपया समस्या के बारे में थोड़ा और बताएँ।"],
  ["Please review the details below and confirm submission.", "कृपया नीचे दिए विवरण जाँचें और प्रस्तुत करने की पुष्टि करें।"],
  ["Where exactly is the issue?", "समस्या ठीक कहाँ है?"],
  ["Please describe the issue.", "कृपया समस्या का वर्णन करें।"],
  ["How severe is the issue: low, medium, or high?", "समस्या कितनी गंभीर है: कम, मध्यम या अधिक?"],
  ["How long has this been happening?", "यह समस्या कितने समय से है?"],
  ["What kind of leak is it: pipe, tap, supply, or unknown?", "यह किस तरह का रिसाव है: पाइप, नल, आपूर्ति, या अज्ञात?"],
  [
    "What kind of sanitation issue is it: sewage, drain, public hygiene, or other?",
    "यह किस तरह की स्वच्छता समस्या है: सीवेज, नाली, सार्वजनिक स्वच्छता, या अन्य?",
  ],
  ["Do you know the streetlight pole number? You can say I don't know.", "क्या आपको स्ट्रीटलाइट का पोल नंबर पता है? नहीं पता हो तो कह सकते हैं।"],
  ["When did you first notice the issue?", "आपने यह समस्या पहली बार कब देखी?"],
  ["Please provide the missing detail.", "कृपया बाकी विवरण दें।"],
  ["I still need one more detail.", "एक विवरण और चाहिए।"],
  ["Please provide a nearby landmark or area.", "कृपया पास का कोई स्थलचिह्न या क्षेत्र बताएँ।"],
  ["Please tell me a nearby landmark or area.", "कृपया पास का कोई स्थलचिह्न या क्षेत्र बताएँ।"],
  ["Please provide a recognizable landmark, area, or street.", "कृपया कोई जाना-माना स्थलचिह्न, क्षेत्र या सड़क बताएँ।"],
  [
    "I could not match that location yet. Please provide a nearby landmark, area, or street.",
    "यह स्थान अभी नहीं मिला। कृपया पास का स्थलचिह्न, क्षेत्र या सड़क बताएँ।",
  ],
  ["The image appears to be a selfie, not civic evidence.", "यह फ़ोटो सेल्फी लगती है, नागरिक साक्ष्य नहीं।"],
  ["The image appears relevant to a road issue.", "यह फ़ोटो सड़क समस्या से संबंधित लगती है।"],
  ["The photo appears relevant to this civic issue.", "यह फ़ोटो इस नागरिक समस्या से संबंधित लगती है।"],
  ["Image saved as evidence; no field was inferred.", "फ़ोटो साक्ष्य के रूप में सहेज ली गई; कोई फ़ील्ड नहीं निकाला गया।"],
  ["Please upload a relevant civic photo.", "कृपया समस्या की प्रासंगिक फ़ोटो अपलोड करें।"],
  [
    "I can collect and submit a civic report only after the required review and your explicit confirmation.",
    "समीक्षा और आपकी स्पष्ट पुष्टि के बाद ही शिकायत दर्ज होगी।",
  ],
  [
    "I can help collect a civic issue report, but I cannot provide legal, eligibility, or guaranteed-response advice.",
    "मैं शिकायत दर्ज करने में मदद कर सकता हूँ, लेकिन कानूनी सलाह, पात्रता या समय की गारंटी नहीं दे सकता।",
  ],
  [
    "I can help collect a civic issue report using the supported service types.",
    "मैं निर्धारित सेवा प्रकारों में नागरिक शिकायत दर्ज करने में मदद कर सकता हूँ।",
  ],
  ["Is that correct?", "क्या यह सही है?"],
  ["Which one is correct?", "कौन-सा सही है?"],
  ["I found this location:", "यह स्थान मिला:"],
  ["I found more than one possible location", "एक से अधिक संभावित स्थान मिले"],
  ["I can help report this", "मैं यह दर्ज कर सकता हूँ:"],
  ["I identified this as a", "यह सेवा पहचानी गई:"],
  ["Complaint submitted successfully. Reference:", "शिकायत दर्ज हो गई है। संदर्भ:"],
  ["Complaint submitted successfully. Service request", "शिकायत दर्ज हो गई है। सेवा अनुरोध"],
  [
    "Save the access key on the acknowledgement to track this request.",
    "आवेदन ट्रैक करने के लिए पावती पर दी गई प्रवेश कुंजी सहेजें।",
  ],
  ["Updated ", "अपडेट: "],
  ["road / pothole complaint", "सड़क / गड्ढा शिकायत"],
  ["garbage accumulation complaint", "कचरा जमाव शिकायत"],
  ["streetlight complaint", "स्ट्रीटलाइट शिकायत"],
  ["water leak complaint", "पानी रिसाव शिकायत"],
  ["sanitation complaint", "स्वच्छता शिकायत"],
];

export function localizeAgentText(text: string, hindi: boolean): string {
  if (!hindi || !text) return text;
  let localized = text;
  for (const [english, hindiText] of PHRASES) {
    localized = localized.split(english).join(hindiText);
    localized = localized.split(english.toLowerCase()).join(hindiText);
  }
  return localized;
}
