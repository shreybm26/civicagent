import type { Message, SessionView } from "./types";

const welcome: Message = {
  role: "agent",
  text: "Namaste, I am Civic Sevak. What issue would you like to report?",
  timestamp: "1970-01-01T00:00:00.000Z",
};

export function conversation(session: SessionView | null): Message[] {
  if (!session) return [welcome];
  const messages = [...(session.messages ?? [])];
  if (!messages.length) messages.push(welcome);
  if (session.agent_message && messages[messages.length - 1]?.text !== session.agent_message) {
    messages.push({
      role: "agent",
      text: session.agent_message,
      timestamp: `${session.session_id}-agent-overlay`,
    });
  }
  return messages;
}

export const SUGGESTIONS = [
  { label: "Pothole", hi: "गड्ढा", text: "There is a pothole on my street", textHi: "मेरी सड़क पर गड्ढा है" },
  { label: "Garbage", hi: "कचरा", text: "Garbage has not been collected in my area", textHi: "मेरे इलाके में कचरा नहीं उठाया गया" },
  { label: "Streetlight", hi: "स्ट्रीटलाइट", text: "The streetlight outside my house has been off for a week", textHi: "मेरे घर के बाहर स्ट्रीटलाइट एक हफ्ते से बंद है" },
  { label: "Water leak", hi: "पानी रिसाव", text: "There is a water leak near my building", textHi: "मेरी इमारत के पास पानी का रिसाव है" },
  { label: "Sanitation", hi: "स्वच्छता", text: "There is a sanitation issue in my neighbourhood", textHi: "मेरे मोहल्ले में स्वच्छता की समस्या है" },
];

export const STATE_LABEL: Record<string, { en: string; hi: string }> = {
  IDLE: { en: "New grievance", hi: "नई शिकायत" },
  IDENTIFYING: { en: "Identifying service", hi: "सेवा की पहचान" },
  COLLECTING: { en: "Collecting details", hi: "विवरण एकत्र" },
  LOCATION_REQUIRED: { en: "Location required", hi: "स्थान आवश्यक" },
  MEDIA_ANALYSIS: { en: "Checking evidence", hi: "साक्ष्य जाँच" },
  VALIDATING: { en: "Validating", hi: "सत्यापन" },
  REVIEWING: { en: "Pending confirmation", hi: "पुष्टि लंबित" },
  SUBMITTING: { en: "Submitting", hi: "प्रस्तुत" },
  SUBMISSION_FAILED: { en: "Submission failed", hi: "प्रस्तुति असफल" },
  COMPLETED: { en: "Acknowledged", hi: "पावती जारी" },
};
