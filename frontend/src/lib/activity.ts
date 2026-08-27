export type PendingAction =
  | "starting"
  | "recording"
  | "resolving_location"
  | "checking_image"
  | "saving_details"
  | "submitting"
  | "resetting"
  | null;

export type AvatarState = "idle" | "processing" | "success" | "error";

const ACTIVITY: Record<Exclude<PendingAction, null>, { en: string; hi: string }> = {
  starting: { en: "Starting your session", hi: "सत्र शुरू किया जा रहा है" },
  recording: { en: "Recording your details", hi: "विवरण दर्ज किया जा रहा है" },
  resolving_location: { en: "Resolving the location", hi: "स्थान खोजा जा रहा है" },
  checking_image: { en: "Checking the image", hi: "तस्वीर जाँची जा रही है" },
  saving_details: { en: "Saving your details", hi: "विवरण सहेजा जा रहा है" },
  submitting: { en: "Submitting your grievance", hi: "शिकायत भेजी जा रही है" },
  resetting: { en: "Starting a new grievance", hi: "नई शिकायत तैयार की जा रही है" },
};

export function activityLabel(action: PendingAction, hindi: boolean): string {
  if (!action) return hindi ? "विवरण दर्ज किया जा रहा है" : "Recording your details";
  return hindi ? ACTIVITY[action].hi : ACTIVITY[action].en;
}
