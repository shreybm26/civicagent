import type { Message, SessionView } from "./types";

const welcome: Message = {
  role: "agent",
  text: "Namaste. Please describe the civic issue you want to report. I will collect the required details and show you a review form before anything is submitted.",
  timestamp: new Date().toISOString(),
};

export function conversation(session: SessionView | null): Message[] {
  if (!session) return [welcome];
  const messages = [...(session.messages ?? [])];
  if (!messages.length) messages.push(welcome);
  if (session.agent_message && messages[messages.length - 1]?.text !== session.agent_message) {
    messages.push({
      role: "agent",
      text: session.agent_message,
      timestamp: new Date().toISOString(),
    });
  }
  return messages;
}

export const SUGGESTIONS = [
  { label: "Pothole", hi: "गड्ढा", text: "There is a pothole near JNTU Metro" },
  { label: "Garbage", hi: "कचरा", text: "Garbage has not been collected near Hitech City Metro" },
  { label: "Streetlight", hi: "स्ट्रीटलाइट", text: "The streetlight outside Ameerpet Metro has been off for a week" },
  { label: "Water leak", hi: "पानी रिसाव", text: "There is a water leak near Charminar" },
  { label: "Sanitation", hi: "स्वच्छता", text: "There is a sanitation issue near Secunderabad Railway Station" },
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
