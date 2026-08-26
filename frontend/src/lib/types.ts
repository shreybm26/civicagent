export type State = "IDLE"|"IDENTIFYING"|"COLLECTING"|"LOCATION_REQUIRED"|"MEDIA_ANALYSIS"|"VALIDATING"|"REVIEWING"|"SUBMITTING"|"SUBMISSION_FAILED"|"COMPLETED";
export type Field = {id:string; value:unknown; required:boolean; source?:string|null; confidence?:number|null; status:"missing"|"candidate"|"accepted"|"rejected"; reason?:string|null};
export type SessionView = {session_id:string; state:State; service_id:string|null; schema_version:string; fields:Field[]; agent_message:string|null; error:{code:string;message:string;retryable:boolean}|null};
