import type {SessionView} from './types';
const base={session_id:'demo',schema_version:'1.0',agent_message:null,error:null};
export const demoFixtures:Record<string,SessionView>={
 idle:{...base,state:'IDLE',service_id:null,fields:[]},
 collecting:{...base,state:'COLLECTING',service_id:'road_issue',fields:[{id:'location',value:null,required:true,status:'missing'},{id:'description',value:'Large pothole near JNTU Metro',required:true,source:'citizen',confidence:1,status:'accepted'}]},
 reviewing:{...base,state:'REVIEWING',service_id:'road_issue',fields:[{id:'location',value:'JNTU Metro Station, Kukatpally, Hyderabad 500085',required:true,source:'location',confidence:.98,status:'accepted'},{id:'description',value:'Large pothole near JNTU Metro',required:true,source:'citizen',confidence:1,status:'accepted'},{id:'severity',value:'high',required:true,source:'photo',confidence:.82,status:'candidate'}]},
 completed:{...base,state:'COMPLETED',service_id:'road_issue',fields:[],receipt:{reference:'CIV-DEMO-1842',status:'Received',department:'Roads & Infrastructure',timestamp:'2026-08-28T08:42:00Z'}}
};
