/** Human labels for schema field ids shown in chat, review, and summary. */

const LABELS: Record<string, { en: string; hi: string; hintEn?: string; hintHi?: string }> = {
  location: { en: "Location", hi: "स्थान" },
  description: { en: "Description", hi: "विवरण" },
  severity: { en: "Severity", hi: "गंभीरता" },
  photo: { en: "Photo", hi: "तस्वीर" },
  additional_details: { en: "Additional details", hi: "अतिरिक्त विवरण" },
  landmark: { en: "Landmark", hi: "स्थलचिह्न" },
  duration: {
    en: "How long has this been happening?",
    hi: "यह समस्या कब से हो रही है?",
    hintEn: "Example: 3 days, since Monday, about a week",
    hintHi: "उदाहरण: 3 दिन, सोमवार से, लगभग एक सप्ताह",
  },
  time_noticed: {
    en: "When did you first notice it?",
    hi: "आपने इसे पहली बार कब देखा?",
    hintEn: "Example: this morning, yesterday evening",
    hintHi: "उदाहरण: आज सुबह, कल शाम",
  },
  pole_number: {
    en: "Streetlight pole number",
    hi: "स्ट्रीटलाइट पोल नंबर",
    hintEn: "If unknown, you can say I don't know",
    hintHi: "अगर पता नहीं है तो लिख सकते हैं: पता नहीं",
  },
  leak_type: { en: "Leak type", hi: "रिसाव का प्रकार" },
  issue_type: { en: "Issue type", hi: "समस्या का प्रकार" },
};

export function fieldLabel(fieldId: string, hindi = false): string {
  const entry = LABELS[fieldId];
  if (entry) return hindi ? entry.hi : entry.en;
  return fieldId.replaceAll("_", " ");
}

export function fieldHint(fieldId: string, hindi = false): string | undefined {
  const entry = LABELS[fieldId];
  if (!entry) return undefined;
  return hindi ? entry.hintHi : entry.hintEn;
}
