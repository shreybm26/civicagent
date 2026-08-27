import avatar from "../../assets/civic-sevak.svg";
import type { AvatarState } from "../../lib/activity";

export function CivicSevakAvatar({
  size = "message",
  state = "idle",
}: {
  size?: "header" | "message";
  state?: AvatarState;
}) {
  return (
    <span className={`sevak-avatar size-${size} state-${state}`} aria-hidden="true">
      <img src={avatar} alt="" className="sevak-avatar-img" />
      {state === "success" && <span className="sevak-badge success" />}
      {state === "error" && <span className="sevak-badge error" />}
    </span>
  );
}
