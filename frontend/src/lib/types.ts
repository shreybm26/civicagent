export type State = "IDLE"|"IDENTIFYING"|"COLLECTING"|"LOCATION_REQUIRED"|"MEDIA_ANALYSIS"|"VALIDATING"|"REVIEWING"|"SUBMITTING"|"SUBMISSION_FAILED"|"COMPLETED";
export type Field = {id:string; value:unknown; required:boolean; source?:string|null; confidence?:number|null; status:"missing"|"candidate"|"accepted"|"rejected"; reason?:string|null};
export type Message={role:"citizen"|"agent"|"system";text:string;timestamp:string};
export type Evidence={media_id:string;filename:string;relevant:boolean;reason:string};
export type Receipt={reference:string;status:string;department?:string|null;timestamp:string};
export type SessionView = {session_id:string; state:State; service_id:string|null; schema_version:string; messages?:Message[]; fields:Field[]; evidence?:Evidence[]; location?:{query:string;address?:string|null;lat?:number|null;lng?:number|null;confidence:number;source?:string|null}|null; agent_message:string|null; service?:{service_id:string;name:string;department:string}|null; receipt?:Receipt|null; error:{code:string;message:string;retryable:boolean}|null};
